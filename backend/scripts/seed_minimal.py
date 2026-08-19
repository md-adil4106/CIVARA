import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon, LineString, Point
from app.core.database import SessionLocal, engine
from app.models import (
    Base,
    Ward,
    Department,
    User,
    UserRole,
    Category,
    InfraAsset,
    AssetType,
)


def seed_minimal_data():
    db = SessionLocal()
    try:
        print("Starting minimal seed script...")

        # 1. Seed Departments
        dept_data = [
            ("Roads & Infrastructure Department", "roads"),
            ("Water Supply & Drainage Department", "drainage"),
            ("Sanitation & Waste Management Department", "sanitation"),
            ("Electricity & Public Lighting Department", "electricity"),
            ("Public Health & Safety Department", "health"),
            ("Civic Services Department", "other"),
        ]

        departments = {}
        for name, scope in dept_data:
            dept = db.query(Department).filter_by(category_scope=scope).first()
            if not dept:
                dept = Department(name=name, category_scope=scope)
                db.add(dept)
                db.flush()
            departments[scope] = dept
        print(f"Seeded {len(departments)} departments.")

        # 2. Seed Categories
        categories_data = [
            ("pothole", "roads"),
            ("waterlogging", "drainage"),
            ("drain_block", "drainage"),
            ("garbage", "sanitation"),
            ("streetlight", "electricity"),
            ("health_hazard", "health"),
            ("other", "other"),
        ]

        categories = {}
        for cat_name, scope in categories_data:
            cat = db.query(Category).filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name, department_id=departments[scope].id)
                db.add(cat)
                db.flush()
            categories[cat_name] = cat
        print(f"Seeded {len(categories)} categories.")

        # 3. Seed Ward (Ranchi Ward 15, Jharkhand)
        ward_code = "JH-RAN-W15"
        ward = db.query(Ward).filter_by(ward_code=ward_code).first()
        if not ward:
            # WGS84 Polygon coordinates around Ranchi Main Road - Lalpur area
            ward_polygon = Polygon([
                (85.3200, 23.3500),
                (85.3400, 23.3500),
                (85.3400, 23.3700),
                (85.3200, 23.3700),
                (85.3200, 23.3500),
            ])
            ward = Ward(
                name="Ranchi Ward 15 (Main Road - Lalpur)",
                ward_code=ward_code,
                geometry=from_shape(ward_polygon, srid=4326),
            )
            db.add(ward)
            db.flush()
        print(f"Seeded Ward: {ward.name} ({ward.ward_code})")

        # 4. Seed Default Citizen User
        user_email = "citizen@civara.gov.in"
        user = db.query(User).filter_by(phone_or_email=user_email).first()
        if not user:
            user = User(
                phone_or_email=user_email,
                password_hash="$2b$12$eImiTXuWVxfM37uY4JANjO5E/w92b1G9d2Oa4R3B1O3B1O3B1O3B1", # Demo hash
                role=UserRole.CITIZEN,
                full_name="Rajesh Kumar",
            )
            db.add(user)
            db.flush()
        print(f"Seeded User: {user.full_name} ({user.phone_or_email})")

        # 5. Seed InfraAssets inside Ward 15
        assets_data = [
            (
                AssetType.ROAD_SEGMENT,
                LineString([(85.3250, 23.3550), (85.3350, 23.3550)]),
                92.5,
                "Main Road Arterial Segment A",
            ),
            (
                AssetType.DRAIN_SEGMENT,
                LineString([(85.3250, 23.3555), (85.3350, 23.3555)]),
                85.0,
                "Lalpur Main Stormwater Drain",
            ),
            (
                AssetType.STREETLIGHT,
                Point(85.3300, 23.3600),
                98.0,
                "Lalpur Chowk High-Mast Light #104",
            ),
            (
                AssetType.ROAD_SEGMENT,
                LineString([(85.3300, 23.3500), (85.3300, 23.3650)]),
                78.0,
                "Circular Road North Corridor",
            ),
        ]

        existing_assets = db.query(InfraAsset).filter_by(ward_id=ward.id).count()
        if existing_assets == 0:
            for asset_type, geom, health, label in assets_data:
                asset = InfraAsset(
                    asset_type=asset_type,
                    geometry=from_shape(geom, srid=4326),
                    ward_id=ward.id,
                    health_score=health,
                )
                db.add(asset)
            db.flush()
            print(f"Seeded {len(assets_data)} InfraAsset records in Ward 15.")
        else:
            print(f"InfraAssets already present ({existing_assets} records).")

        db.commit()
        print("Seed minimal script completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding minimal data: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_minimal_data()
