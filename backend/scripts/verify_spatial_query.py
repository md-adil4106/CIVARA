import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from app.core.database import engine


def run_manual_spatial_query():
    sql = """
    SELECT 
        c.id AS complaint_id,
        c.description_text,
        a.id AS asset_id,
        a.asset_type,
        ROUND(ST_Distance(c.location::geography, a.geometry::geography)::numeric, 2) AS distance_meters
    FROM complaints c, infra_assets a
    WHERE ST_DWithin(c.location::geography, a.geometry::geography, 200)
    ORDER BY distance_meters ASC
    LIMIT 5;
    """

    print("=" * 70)
    print("MANUAL POSTGIS SPATIAL QUERY:")
    print(sql.strip())
    print("=" * 70)
    print("EXECUTING QUERY AGAINST LIVE DOCKERIZED POSTGIS DB...")
    
    with engine.connect() as conn:
        result = conn.execute(text(sql)).fetchall()
        print(f"\nQUERY RESULTS ({len(result)} matching rows found):")
        print("-" * 70)
        for row in result:
            print(f"Complaint ID : {row.complaint_id}")
            print(f"Description  : {row.description_text}")
            print(f"Asset ID     : {row.asset_id}")
            print(f"Asset Type   : {row.asset_type}")
            print(f"Distance (m) : {row.distance_meters} meters")
            print("-" * 70)


if __name__ == "__main__":
    run_manual_spatial_query()
