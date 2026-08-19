import pytest
from geoalchemy2 import Geography
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy import func, cast
from app.core.database import SessionLocal
from app.models import (
    Ward,
    User,
    Category,
    Complaint,
    ComplaintStatus,
    InfraAsset,
)


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_insert_complaint_with_valid_point_geometry(db_session):
    """Test inserting a Complaint with a valid WGS84 Point geometry."""
    ward = db_session.query(Ward).filter_by(ward_code="JH-RAN-W15").first()
    category = db_session.query(Category).filter_by(name="pothole").first()
    user = db_session.query(User).filter_by(phone_or_email="citizen@civara.gov.in").first()

    assert ward is not None, "Ward should be seeded"
    assert category is not None, "Category should be seeded"
    assert user is not None, "User should be seeded"

    # Create complaint at Main Road intersection (85.3280, 23.3550)
    point_geom = Point(85.3280, 23.3550)
    complaint = Complaint(
        citizen_id=user.id,
        category_id=category.id,
        ward_id=ward.id,
        description_text="Severe pothole on Main Road causing traffic slowdown",
        location=from_shape(point_geom, srid=4326),
        status=ComplaintStatus.SUBMITTED,
    )

    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)

    assert complaint.id is not None
    assert complaint.status == ComplaintStatus.SUBMITTED
    assert complaint.ai_category_confidence is None  # Phase 1 AI fields are NULL

    # Verify geometry retrieval
    saved_shape = to_shape(complaint.location)
    assert isinstance(saved_shape, Point)
    assert abs(saved_shape.x - 85.3280) < 1e-5
    assert abs(saved_shape.y - 23.3550) < 1e-5


def test_spatial_query_st_dwithin(db_session):
    """Test PostGIS ST_DWithin spatial query matching a Complaint to nearby InfraAssets."""
    user = db_session.query(User).filter_by(phone_or_email="citizen@civara.gov.in").first()
    category = db_session.query(Category).filter_by(name="pothole").first()
    ward = db_session.query(Ward).filter_by(ward_code="JH-RAN-W15").first()

    # Insert complaint near Main Road Arterial Segment
    complaint_location = Point(85.3300, 23.3551)
    complaint = Complaint(
        citizen_id=user.id,
        category_id=category.id,
        ward_id=ward.id,
        description_text="Deep asphalt crack near road segment",
        location=from_shape(complaint_location, srid=4326),
    )
    db_session.add(complaint)
    db_session.commit()

    # Query InfraAssets within 200 meters using ST_DWithin on geography
    nearby_assets = (
        db_session.query(
            InfraAsset,
            func.ST_Distance(
                cast(InfraAsset.geometry, Geography),
                cast(Complaint.location, Geography),
            ).label("distance_meters"),
        )
        .filter(Complaint.id == complaint.id)
        .filter(
            func.ST_DWithin(
                cast(InfraAsset.geometry, Geography),
                cast(Complaint.location, Geography),
                200.0,  # 200 meters
            )
        )
        .all()
    )

    assert len(nearby_assets) > 0, "Should find at least one nearby asset within 200m"
    asset, distance = nearby_assets[0]
    assert asset.ward_id == ward.id
    assert distance < 200.0
