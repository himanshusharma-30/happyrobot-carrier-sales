"""Deterministic negotiation engine.

Design philosophy: the LLM discovers what the carrier wants; THIS code decides
the number. That separation is what makes the system safe to deploy — rates
are governed by broker-configurable multipliers, not model temperature.
"""
from dataclasses import dataclass
from typing import Literal, Optional

from api.config import settings


@dataclass
class NegotiationDecision:
    action: Literal["accept", "counter", "reject"]
    round_number: int
    agreed_rate: Optional[float] = None
    counter_offer: Optional[float] = None
    message: str = ""


MAX_ROUNDS = 3


def evaluate(
    loadboard_rate: float,
    carrier_offer: float,
    round_number: int,
    last_counter: Optional[float] = None,
) -> NegotiationDecision:
    """Core negotiation logic. Pure function — easy to unit test.

    round_number is the round this call represents (1, 2, or 3).
    """
    target = loadboard_rate
    floor = loadboard_rate * settings.floor_multiplier
    ceiling = loadboard_rate * settings.ceiling_multiplier

    # --- Rule 1: Carrier offered at or below listed → instant accept
    if carrier_offer <= target:
        return NegotiationDecision(
            action="accept",
            round_number=round_number,
            agreed_rate=round(carrier_offer, 2),
            message=f"Deal. ${carrier_offer:,.2f} on this load.",
        )

    # --- Rule 2: Proximity accept. If we countered previously and they're within
    # 2% of that number, just take it — closing the deal beats a 4th round.
    if last_counter is not None and round_number >= 2:
        if abs(carrier_offer - last_counter) / last_counter <= settings.proximity_accept_pct:
            return NegotiationDecision(
                action="accept",
                round_number=round_number,
                agreed_rate=round(carrier_offer, 2),
                message=f"You got it. ${carrier_offer:,.2f}, we're done.",
            )

    # --- Rule 3: Hit max rounds, still above listed → reject
    if round_number > MAX_ROUNDS:
        return NegotiationDecision(
            action="reject",
            round_number=round_number,
            message="I'm sorry, I'm not able to get there on this one.",
        )

    # --- Rule 4: Carrier asking above ceiling — counter at ceiling (rounds 1–2) or reject (3)
    if carrier_offer > ceiling:
        if round_number >= MAX_ROUNDS:
            return NegotiationDecision(
                action="reject",
                round_number=round_number,
                message=(
                    f"${carrier_offer:,.2f} is above what I can do on this load. "
                    "Let's keep in touch on the next one."
                ),
            )
        return NegotiationDecision(
            action="counter",
            round_number=round_number,
            counter_offer=round(ceiling, 2),
            message=(
                f"${carrier_offer:,.2f} is above my budget on this one, but I can "
                f"go to ${ceiling:,.2f}."
            ),
        )

    # --- Rule 5: Within target–ceiling range → counter, tightening each round
    gap = carrier_offer - target
    if round_number == 1:
        counter = target + gap * 0.4
    elif round_number == 2:
        counter = target + gap * 0.65
    else:  # round 3 — final offer, meet them closer
        counter = target + gap * 0.85

    counter = round(min(counter, ceiling), 2)

    return NegotiationDecision(
        action="counter",
        round_number=round_number,
        counter_offer=counter,
        message=f"I can meet you at ${counter:,.2f}. How's that sound?",
    )