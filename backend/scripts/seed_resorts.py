"""
Seed script to populate the database with real ski resort data.

Usage:
    python scripts/seed_resorts.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from app.database import SessionLocal
from app.models.resort import Resort

# Real ski resort data
RESORTS = [
    {
        "name": "Jackson Hole Mountain Resort",
        "slug": "jackson-hole",
        "latitude": 43.5878,
        "longitude": -110.8279,
        "timezone": "America/Denver",
        "region": "Rocky Mountains",
        "state": "Wyoming",
        "country": "USA",
        "base_elevation_ft": 6311,
        "summit_elevation_ft": 10450,
        "vertical_drop_ft": 4139,
        "total_lifts": 13,
        "total_runs": 133,
        "total_acres": 2500,
        "official_url": "https://www.jacksonhole.com",
        "is_active": True
    },
    {
        "name": "Vail Mountain",
        "slug": "vail",
        "latitude": 39.6061,
        "longitude": -106.3550,
        "timezone": "America/Denver",
        "region": "Rocky Mountains",
        "state": "Colorado",
        "country": "USA",
        "base_elevation_ft": 8120,
        "summit_elevation_ft": 11570,
        "vertical_drop_ft": 3450,
        "total_lifts": 31,
        "total_runs": 195,
        "total_acres": 5317,
        "official_url": "https://www.vail.com",
        "is_active": True
    },
    {
        "name": "Breckenridge Ski Resort",
        "slug": "breckenridge",
        "latitude": 39.4817,
        "longitude": -106.0384,
        "timezone": "America/Denver",
        "region": "Rocky Mountains",
        "state": "Colorado",
        "country": "USA",
        "base_elevation_ft": 9600,
        "summit_elevation_ft": 12998,
        "vertical_drop_ft": 3398,
        "total_lifts": 35,
        "total_runs": 187,
        "total_acres": 2908,
        "official_url": "https://www.breckenridge.com",
        "is_active": True
    },
    {
        "name": "Aspen Snowmass",
        "slug": "aspen-snowmass",
        "latitude": 39.2130,
        "longitude": -106.9478,
        "timezone": "America/Denver",
        "region": "Rocky Mountains",
        "state": "Colorado",
        "country": "USA",
        "base_elevation_ft": 8104,
        "summit_elevation_ft": 12510,
        "vertical_drop_ft": 4406,
        "total_lifts": 21,
        "total_runs": 94,
        "total_acres": 3342,
        "official_url": "https://www.aspensnowmass.com",
        "is_active": True
    },
    {
        "name": "Park City Mountain Resort",
        "slug": "park-city",
        "latitude": 40.6514,
        "longitude": -111.5079,
        "timezone": "America/Denver",
        "region": "Rocky Mountains",
        "state": "Utah",
        "country": "USA",
        "base_elevation_ft": 6800,
        "summit_elevation_ft": 10000,
        "vertical_drop_ft": 3200,
        "total_lifts": 41,
        "total_runs": 348,
        "total_acres": 7300,
        "official_url": "https://www.parkcitymountain.com",
        "is_active": True
    },
    {
        "name": "Alta Ski Area",
        "slug": "alta",
        "latitude": 40.5885,
        "longitude": -111.6381,
        "timezone": "America/Denver",
        "region": "Wasatch Range",
        "state": "Utah",
        "country": "USA",
        "base_elevation_ft": 8530,
        "summit_elevation_ft": 11068,
        "vertical_drop_ft": 2538,
        "total_lifts": 6,
        "total_runs": 116,
        "total_acres": 2200,
        "official_url": "https://www.alta.com",
        "is_active": True
    },
    {
        "name": "Snowbird",
        "slug": "snowbird",
        "latitude": 40.5838,
        "longitude": -111.6570,
        "timezone": "America/Denver",
        "region": "Wasatch Range",
        "state": "Utah",
        "country": "USA",
        "base_elevation_ft": 7760,
        "summit_elevation_ft": 11000,
        "vertical_drop_ft": 3240,
        "total_lifts": 11,
        "total_runs": 169,
        "total_acres": 2500,
        "official_url": "https://www.snowbird.com",
        "is_active": True
    },
    {
        "name": "Mammoth Mountain",
        "slug": "mammoth",
        "latitude": 37.6308,
        "longitude": -119.0326,
        "timezone": "America/Los_Angeles",
        "region": "Sierra Nevada",
        "state": "California",
        "country": "USA",
        "base_elevation_ft": 7953,
        "summit_elevation_ft": 11053,
        "vertical_drop_ft": 3100,
        "total_lifts": 25,
        "total_runs": 175,
        "total_acres": 3500,
        "official_url": "https://www.mammothmountain.com",
        "is_active": True
    },
    {
        "name": "Palisades Tahoe",
        "slug": "palisades-tahoe",
        "latitude": 39.1970,
        "longitude": -120.2356,
        "timezone": "America/Los_Angeles",
        "region": "Sierra Nevada",
        "state": "California",
        "country": "USA",
        "base_elevation_ft": 6200,
        "summit_elevation_ft": 9050,
        "vertical_drop_ft": 2850,
        "total_lifts": 29,
        "total_runs": 270,
        "total_acres": 6000,
        "official_url": "https://www.palisadestahoe.com",
        "is_active": True
    },
    {
        "name": "Heavenly Mountain Resort",
        "slug": "heavenly",
        "latitude": 38.9352,
        "longitude": -119.9394,
        "timezone": "America/Los_Angeles",
        "region": "Sierra Nevada",
        "state": "California",
        "country": "USA",
        "base_elevation_ft": 6540,
        "summit_elevation_ft": 10067,
        "vertical_drop_ft": 3527,
        "total_lifts": 28,
        "total_runs": 97,
        "total_acres": 4800,
        "official_url": "https://www.skiheavenly.com",
        "is_active": True
    },
    {
        "name": "Killington Resort",
        "slug": "killington",
        "latitude": 43.6046,
        "longitude": -72.8201,
        "timezone": "America/New_York",
        "region": "Green Mountains",
        "state": "Vermont",
        "country": "USA",
        "base_elevation_ft": 1165,
        "summit_elevation_ft": 4241,
        "vertical_drop_ft": 3050,
        "total_lifts": 21,
        "total_runs": 155,
        "total_acres": 1509,
        "official_url": "https://www.killington.com",
        "is_active": True
    },
    {
        "name": "Stowe Mountain Resort",
        "slug": "stowe",
        "latitude": 44.5306,
        "longitude": -72.7817,
        "timezone": "America/New_York",
        "region": "Green Mountains",
        "state": "Vermont",
        "country": "USA",
        "base_elevation_ft": 1562,
        "summit_elevation_ft": 3625,
        "vertical_drop_ft": 2160,
        "total_lifts": 13,
        "total_runs": 116,
        "total_acres": 485,
        "official_url": "https://www.stowe.com",
        "is_active": True
    },
    {
        "name": "Big Sky Resort",
        "slug": "big-sky",
        "latitude": 45.2847,
        "longitude": -111.3908,
        "timezone": "America/Denver",
        "region": "Rocky Mountains",
        "state": "Montana",
        "country": "USA",
        "base_elevation_ft": 7500,
        "summit_elevation_ft": 11166,
        "vertical_drop_ft": 4350,
        "total_lifts": 36,
        "total_runs": 300,
        "total_acres": 5800,
        "official_url": "https://www.bigskyresort.com",
        "is_active": True
    },
    {
        "name": "Telluride Ski Resort",
        "slug": "telluride",
        "latitude": 37.9374,
        "longitude": -107.8123,
        "timezone": "America/Denver",
        "region": "Rocky Mountains",
        "state": "Colorado",
        "country": "USA",
        "base_elevation_ft": 8725,
        "summit_elevation_ft": 13150,
        "vertical_drop_ft": 4425,
        "total_lifts": 18,
        "total_runs": 148,
        "total_acres": 2000,
        "official_url": "https://www.tellurideskiresort.com",
        "is_active": True
    },
    {
        "name": "Steamboat Resort",
        "slug": "steamboat",
        "latitude": 40.4572,
        "longitude": -106.8044,
        "timezone": "America/Denver",
        "region": "Rocky Mountains",
        "state": "Colorado",
        "country": "USA",
        "base_elevation_ft": 6900,
        "summit_elevation_ft": 10568,
        "vertical_drop_ft": 3668,
        "total_lifts": 18,
        "total_runs": 169,
        "total_acres": 2965,
        "official_url": "https://www.steamboat.com",
        "is_active": True
    }
]


def seed_resorts():
    """Seed the database with resort data."""
    db = SessionLocal()
    try:
        # Check if resorts already exist
        existing_count = db.query(Resort).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} resorts.")
            response = input("Do you want to continue and add more? (y/n): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return

        # Add resorts
        added = 0
        skipped = 0

        for resort_data in RESORTS:
            # Check if resort with this slug already exists
            existing = db.query(Resort).filter(Resort.slug == resort_data["slug"]).first()

            if existing:
                print(f"⏭️  Skipping {resort_data['name']} (already exists)")
                skipped += 1
                continue

            # Create new resort
            resort = Resort(**resort_data)
            db.add(resort)
            print(f"✅ Adding {resort_data['name']}")
            added += 1

        # Commit all changes
        db.commit()

        print(f"\n{'='*60}")
        print(f"Seeding complete!")
        print(f"Added: {added} resorts")
        print(f"Skipped: {skipped} resorts (already existed)")
        print(f"Total resorts in database: {db.query(Resort).count()}")
        print(f"{'='*60}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting resort database seeding...\n")
    seed_resorts()
