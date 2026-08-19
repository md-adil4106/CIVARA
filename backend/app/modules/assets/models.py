import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.core.database import Base


class AssetType(str, enum.Enum):
    ROAD_SEGMENT = "road_segment"
    DRAIN_SEGMENT = "drain_segment"
    STREETLIGHT = "streetlight"
    OTHER = "other"


class InfraAsset(Base):
    __tablename__ = "infra_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_type = Column(
        Enum(AssetType, values_callable=lambda obj: [e.value for e in obj], name="asset_type_enum"),
        nullable=False,
    )
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False), nullable=False)
    ward_id = Column(UUID(as_uuid=True), ForeignKey("wards.id", ondelete="CASCADE"), nullable=False)
    health_score = Column(Float, nullable=False, default=100.0)
    last_incident_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_infra_assets_geometry", geometry, postgresql_using="gist"),
    )
