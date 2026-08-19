"""0001 Initial Schema with PostGIS, pgvector, and Core Tables

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable PostGIS and pgvector extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create Enums explicitly
    user_role_enum = postgresql.ENUM('citizen', 'officer', 'admin', name='user_role_enum', create_type=False)
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role_enum') THEN CREATE TYPE user_role_enum AS ENUM ('citizen', 'officer', 'admin'); END IF; END $$;")

    complaint_status_enum = postgresql.ENUM(
        'submitted', 'ai_processed', 'correlated', 'routed',
        'in_progress', 'resolved_pending_verification', 'verified_resolved', 'reopened',
        name='complaint_status_enum', create_type=False
    )
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'complaint_status_enum') THEN CREATE TYPE complaint_status_enum AS ENUM ('submitted', 'ai_processed', 'correlated', 'routed', 'in_progress', 'resolved_pending_verification', 'verified_resolved', 'reopened'); END IF; END $$;")

    asset_type_enum = postgresql.ENUM(
        'road_segment', 'drain_segment', 'streetlight', 'other',
        name='asset_type_enum', create_type=False
    )
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'asset_type_enum') THEN CREATE TYPE asset_type_enum AS ENUM ('road_segment', 'drain_segment', 'streetlight', 'other'); END IF; END $$;")

    # 3. Create Departments Table
    op.create_table(
        'departments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category_scope', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 4. Create Users Table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('phone_or_email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', user_role_enum, nullable=False, server_default='citizen'),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_users_phone_or_email', 'users', ['phone_or_email'])

    # 5. Create Wards Table
    op.create_table(
        'wards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('ward_code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('geometry', Geometry(geometry_type='POLYGON', srid=4326, spatial_index=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_wards_ward_code', 'wards', ['ward_code'])
    op.create_index('idx_wards_geometry', 'wards', ['geometry'], postgresql_using='gist')

    # 6. Create Categories Table
    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False),
    )

    # 7. Create Complaints Table
    op.create_table(
        'complaints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('citizen_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('description_text', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=1024), nullable=True),
        sa.Column('voice_url', sa.String(length=1024), nullable=True),
        sa.Column('location', Geometry(geometry_type='POINT', srid=4326, spatial_index=False), nullable=False),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('wards.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', complaint_status_enum, nullable=False, server_default='submitted'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        # AI-derived fields (NULLABLE)
        sa.Column('ai_category_confidence', sa.Float(), nullable=True),
        sa.Column('ai_extracted_summary', sa.Text(), nullable=True),
        sa.Column('embedding', Vector(1536), nullable=True),
    )
    op.create_index('idx_complaints_location', 'complaints', ['location'], postgresql_using='gist')
    op.create_index('idx_complaints_status', 'complaints', ['status'])
    op.create_index('idx_complaints_ward_id', 'complaints', ['ward_id'])
    op.create_index('idx_complaints_created_at', 'complaints', ['created_at'])
    op.create_index('idx_complaints_category_id', 'complaints', ['category_id'])

    # 8. Create InfraAssets Table
    op.create_table(
        'infra_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('asset_type', asset_type_enum, nullable=False),
        sa.Column('geometry', Geometry(geometry_type='GEOMETRY', srid=4326, spatial_index=False), nullable=False),
        sa.Column('ward_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('wards.id', ondelete='CASCADE'), nullable=False),
        sa.Column('health_score', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('last_incident_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('idx_infra_assets_geometry', 'infra_assets', ['geometry'], postgresql_using='gist')


def downgrade() -> None:
    op.drop_index('idx_infra_assets_geometry', table_name='infra_assets')
    op.drop_table('infra_assets')

    op.drop_index('idx_complaints_category_id', table_name='complaints')
    op.drop_index('idx_complaints_created_at', table_name='complaints')
    op.drop_index('idx_complaints_ward_id', table_name='complaints')
    op.drop_index('idx_complaints_status', table_name='complaints')
    op.drop_index('idx_complaints_location', table_name='complaints')
    op.drop_table('complaints')

    op.drop_table('categories')

    op.drop_index('idx_wards_geometry', table_name='wards')
    op.drop_index('idx_wards_ward_code', table_name='wards')
    op.drop_table('wards')

    op.drop_index('idx_users_phone_or_email', table_name='users')
    op.drop_table('users')

    op.drop_table('departments')

    op.execute("DROP TYPE IF EXISTS asset_type_enum;")
    op.execute("DROP TYPE IF EXISTS complaint_status_enum;")
    op.execute("DROP TYPE IF EXISTS user_role_enum;")
