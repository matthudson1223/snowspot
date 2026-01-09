"""
Seed script to populate the database with sample condition data for resorts.

Usage:
    python scripts/seed_conditions.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone
from app.database import SessionLocal
from app.models.resort import Resort
from app.models.condition import Condition
import random


def seed_conditions():
    """Seed the database with sample condition data."""
    db = SessionLocal()
    try:
        # Get all resorts
        resorts = db.query(Resort).filter(Resort.is_active == True).all()

        if not resorts:
            print("No resorts found. Please run seed_resorts.py first.")
            return

        print(f"Found {len(resorts)} resorts. Adding sample conditions...\n")

        added = 0
        for resort in resorts:
            # Create realistic condition data based on region
            is_rockies = "Colorado" in resort.state or "Wyoming" in resort.state or "Utah" in resort.state or "Montana" in resort.state
            is_west_coast = "California" in resort.state
            is_east_coast = "Vermont" in resort.state

            # Base values depend on region and elevation
            if is_rockies:
                base_depth = random.randint(40, 120)
                new_snow_24h = random.randint(0, 12)
                temperature = random.randint(10, 35)
            elif is_west_coast:
                base_depth = random.randint(30, 100)
                new_snow_24h = random.randint(0, 18)
                temperature = random.randint(20, 40)
            else:  # East coast
                base_depth = random.randint(20, 60)
                new_snow_24h = random.randint(0, 8)
                temperature = random.randint(5, 30)

            # Calculate summit depth (usually more)
            summit_depth = base_depth + random.randint(10, 40)

            # Calculate snow quality score based on conditions
            quality_score = min(100, (
                min(30, new_snow_24h * 3) +  # Fresh snow (0-30 points)
                min(25, max(0, 30 - abs(temperature - 28)) * 1.5) +  # Temperature (0-25)
                random.randint(20, 45)  # Other factors (wind, humidity, etc)
            ))

            # Lift and run status
            total_lifts_open = random.randint(int(resort.total_lifts * 0.6), resort.total_lifts)
            total_runs_open = random.randint(int(resort.total_runs * 0.5), resort.total_runs)

            condition = Condition(
                time=datetime.now(timezone.utc),
                resort_id=resort.id,
                base_depth_in=base_depth,
                summit_depth_in=summit_depth,
                new_snow_24h_in=new_snow_24h,
                new_snow_48h_in=new_snow_24h + random.randint(0, 8),
                new_snow_7d_in=new_snow_24h + random.randint(10, 30),
                temperature_f=temperature,
                wind_speed_mph=random.randint(5, 25),
                wind_direction=random.randint(0, 359),  # Wind direction in degrees
                humidity_percent=random.randint(30, 70),
                lifts_open=total_lifts_open,
                lifts_total=resort.total_lifts,
                runs_open=total_runs_open,
                runs_total=resort.total_runs,
                terrain_parks_open=random.randint(0, 3),
                snow_quality_score=int(quality_score),
                skiability_index=random.randint(60, 95),
                crowd_level=random.randint(1, 4),
                confidence_score=0.85
            )

            db.add(condition)
            print(f"✅ Adding conditions for {resort.name}")
            print(f"   Base: {base_depth}\" | New Snow: {new_snow_24h}\" | Temp: {temperature}°F | Quality: {quality_score}")
            added += 1

        # Commit all changes
        db.commit()

        print(f"\n{'='*60}")
        print(f"Seeding complete!")
        print(f"Added conditions for {added} resorts")
        print(f"{'='*60}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting condition database seeding...\n")
    seed_conditions()
