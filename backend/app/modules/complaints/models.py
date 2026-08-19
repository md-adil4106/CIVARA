import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class ComplaintStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    AI_PROCESSED = "ai_processed"
    CORRELATED = "correlated"
    ROUTED = "routed"
    IN_PROGRESS = "in_progress"
    RESOLVED_PENDING_VERIFICATION = "resolved_pending_verification"
    VERIFIED_RESOLVED = "verified_resolved"
    REOPENED = "reopened"


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    description_text = Column(Text, nullable=False)
    image_url = Column(String(1024), nullable=True)
    voice_url = Column(String(1024), nullable=True)
    location = Column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)
    ward_id = Column(UUID(as_uuid=True), ForeignKey("wards.id", ondelete="SET NULL"), nullable=True)
    status = Column(
        Enum(ComplaintStatus, values_callable=lambda obj: [e.value for e in obj], name="complaint_status_enum"),
        nullable=False,
        default=ComplaintStatus.SUBMITTED,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # AI-derived fields (NULLABLE for Phase 4)
    ai_category_confidence = Column(Float, nullable=True)
    ai_extracted_summary = Column(Text, nullable=True)
    embedding = Column(Vector(1536), nullable=True)

    __table_args__ = (
        Index("idx_complaints_location", location, postgresql_using="gist"),
        Index("idx_complaints_status", status),
        Index("idx_complaints_ward_id", ward_id),
        Index("idx_complaints_created_at", created_at),
        Index("idx_complaints_category_id", category_id),
    )
