"""Seed loads from a JSON file into SQLite (idempotent)."""
import json
from datetime import datetime
from pathlib import Path

from api.db import SessionLocal
from api.models import Load


def seed_loads_from_json(path: str = "loads.json") -> int:
    p = Path(path)
    if not p.exists():
        print(f"[seed] {path} not found — skipping")
        return 0

    with p.open() as f:
        rows = json.load(f)

    db = SessionLocal()
    inserted = 0
    try:
        for row in rows:
            if db.query(Load).filter(Load.load_id == row["load_id"]).first():
                continue
            load = Load(
                load_id=row["load_id"],
                origin=row["origin"],
                destination=row["destination"],
                pickup_datetime=datetime.fromisoformat(row["pickup_datetime"].replace("Z", "+00:00")),
                delivery_datetime=datetime.fromisoformat(row["delivery_datetime"].replace("Z", "+00:00")),
                equipment_type=row["equipment_type"],
                loadboard_rate=row["loadboard_rate"],
                notes=row.get("notes"),
                weight=row.get("weight"),
                commodity_type=row.get("commodity_type"),
                num_of_pieces=row.get("num_of_pieces"),
                miles=row.get("miles"),
                dimensions=row.get("dimensions"),
            )
            db.add(load)
            inserted += 1
        db.commit()
        print(f"[seed] inserted {inserted} loads")
    finally:
        db.close()
    return inserted