"""Unit tests for the negotiation engine. Run with: pytest -v"""
from api.negotiation import MAX_ROUNDS, evaluate


def test_accept_at_or_below_listed():
    d = evaluate(loadboard_rate=2400, carrier_offer=2400, round_number=1)
    assert d.action == "accept" and d.agreed_rate == 2400

    d = evaluate(loadboard_rate=2400, carrier_offer=2200, round_number=1)
    assert d.action == "accept" and d.agreed_rate == 2200


def test_counter_within_ceiling_round_1():
    # 2400 listed, 2500 ask → round 1 counters at 2400 + 40% of (2500-2400) = 2440
    d = evaluate(loadboard_rate=2400, carrier_offer=2500, round_number=1)
    assert d.action == "counter"
    assert d.counter_offer == 2440.0


def test_counter_above_ceiling_becomes_ceiling():
    # 2400 listed, 2700 ask, ceiling = 2592 → counter at 2592
    d = evaluate(loadboard_rate=2400, carrier_offer=2700, round_number=1)
    assert d.action == "counter"
    assert d.counter_offer == 2592.0


def test_reject_above_ceiling_on_final_round():
    d = evaluate(loadboard_rate=2400, carrier_offer=2700, round_number=MAX_ROUNDS)
    assert d.action == "reject"


def test_proximity_accept_round_2():
    # We last countered 2500, they come back at 2490 (within 2%) → accept
    d = evaluate(loadboard_rate=2400, carrier_offer=2490, round_number=2, last_counter=2500)
    assert d.action == "accept"


def test_reject_after_max_rounds():
    d = evaluate(loadboard_rate=2400, carrier_offer=2550, round_number=MAX_ROUNDS + 1)
    assert d.action == "reject"


def test_tightening_counters_across_rounds():
    # Same carrier_offer across rounds should give progressively higher counters
    r1 = evaluate(2400, 2580, round_number=1).counter_offer
    r2 = evaluate(2400, 2580, round_number=2).counter_offer
    r3 = evaluate(2400, 2580, round_number=3).counter_offer
    assert r1 < r2 < r3