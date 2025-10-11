# =============================================================================
#  Filename: create_service_tiers.py
#
#  Short Description: Create FedEx service tiers mapping table in SQLite
#
#  Creation date: 2025-10-08
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Create fedex_service_tiers table with service level mappings.
Includes example queries joining with rates and sample shipments.
"""

import sqlite3
from pathlib import Path

from loguru import logger


def create_service_tiers_table(conn: sqlite3.Connection) -> None:
    """Create the fedex_service_tiers table."""
    logger.info("Creating fedex_service_tiers table...")
    
    cursor = conn.cursor()
    
    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS fedex_service_tiers")
    
    # Create table
    create_table_sql = """
    CREATE TABLE fedex_service_tiers (
        id INTEGER PRIMARY KEY,
        service_name TEXT NOT NULL,
        delivery_time_desc TEXT NOT NULL,
        delivery_day TEXT NOT NULL,
        delivery_deadline TEXT NOT NULL,
        column_name TEXT NOT NULL
    )
    """
    cursor.execute(create_table_sql)
    
    logger.success("✅ Table created")


def populate_service_tiers(conn: sqlite3.Connection) -> None:
    """Populate fedex_service_tiers with FedEx Express services."""
    logger.info("Populating service tiers...")
    
    cursor = conn.cursor()
    
    services = [
        (
            1,
            "FedEx First Overnight",
            "Next day by 8 or 8:30 a.m.",
            "Next day",
            "8:00 AM - 8:30 AM",
            "FedEx_First_Overnight"
        ),
        (
            2,
            "FedEx Priority Overnight",
            "Next day by 10:30 a.m. or 11 a.m.",
            "Next day",
            "10:30 AM - 11:00 AM",
            "FedEx_Priority_Overnight"
        ),
        (
            3,
            "FedEx Standard Overnight",
            "Next day by 5 p.m.",
            "Next day",
            "5:00 PM",
            "FedEx_Standard_Overnight"
        ),
        (
            4,
            "FedEx 2Day A.M.",
            "2nd day by 10:30 a.m. or 11 a.m.",
            "2nd day",
            "10:30 AM - 11:00 AM",
            "FedEx_2Day_AM"
        ),
        (
            5,
            "FedEx 2Day",
            "2nd day by 5 p.m.",
            "2nd day",
            "5:00 PM",
            "FedEx_2Day"
        ),
        (
            6,
            "FedEx Express Saver",
            "3rd day by 5 p.m.",
            "3rd day",
            "5:00 PM",
            "FedEx_Express_Saver"
        ),
    ]
    
    insert_sql = """
    INSERT INTO fedex_service_tiers 
    (id, service_name, delivery_time_desc, delivery_day, delivery_deadline, column_name)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    cursor.executemany(insert_sql, services)
    conn.commit()
    
    logger.success(f"✅ Inserted {len(services)} service tiers")


def create_sample_shipments_table(conn: sqlite3.Connection) -> None:
    """Create sample shipments table for demonstration."""
    logger.info("Creating sample_shipments table...")
    
    cursor = conn.cursor()
    
    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS sample_shipments")
    
    # Create table
    create_table_sql = """
    CREATE TABLE sample_shipments (
        shipment_id INTEGER PRIMARY KEY,
        service_id INTEGER NOT NULL,
        tracking_number TEXT NOT NULL,
        destination_zone INTEGER NOT NULL,
        weight INTEGER NOT NULL,
        FOREIGN KEY (service_id) REFERENCES fedex_service_tiers(id)
    )
    """
    cursor.execute(create_table_sql)
    
    logger.success("✅ Table created")


def populate_sample_shipments(conn: sqlite3.Connection) -> None:
    """Populate sample shipments for demonstration."""
    logger.info("Populating sample shipments...")
    
    cursor = conn.cursor()
    
    # Sample shipments with various services and zones
    shipments = [
        (1, 6, "TRK123456789", 2, 10),    # Express Saver, Zone 2, 10 lbs
        (2, 5, "TRK234567890", 3, 25),    # 2Day, Zone 3, 25 lbs
        (3, 4, "TRK345678901", 5, 50),    # 2Day AM, Zone 5, 50 lbs
        (4, 1, "TRK456789012", 2, 5),     # First Overnight, Zone 2, 5 lbs
        (5, 3, "TRK567890123", 4, 100),   # Standard Overnight, Zone 4, 100 lbs
        (6, 2, "TRK678901234", 6, 75),    # Priority Overnight, Zone 6, 75 lbs
        (7, 6, "TRK789012345", 7, 15),    # Express Saver, Zone 7, 15 lbs
        (8, 5, "TRK890123456", 3, 40),    # 2Day, Zone 3, 40 lbs
    ]
    
    insert_sql = """
    INSERT INTO sample_shipments 
    (shipment_id, service_id, tracking_number, destination_zone, weight)
    VALUES (?, ?, ?, ?, ?)
    """
    
    cursor.executemany(insert_sql, shipments)
    conn.commit()
    
    logger.success(f"✅ Inserted {len(shipments)} sample shipments")


def run_example_queries(conn: sqlite3.Connection) -> None:
    """Run example queries to demonstrate table joins."""
    logger.info("\n" + "="*70)
    logger.info("EXAMPLE QUERIES WITH SERVICE TIERS")
    logger.info("="*70 + "\n")
    
    import pandas as pd
    
    # Query 1: Show all service tiers
    logger.info("Query 1: All FedEx Service Tiers")
    query1 = "SELECT * FROM fedex_service_tiers ORDER BY id"
    df1 = pd.read_sql_query(query1, conn)
    print(df1.to_string(index=False))
    print()
    
    # Query 2: Join sample shipments with service tiers
    logger.info("Query 2: Sample Shipments with Service Details")
    query2 = """
    SELECT 
        s.shipment_id,
        s.tracking_number,
        st.service_name,
        st.delivery_time_desc,
        s.destination_zone,
        s.weight
    FROM sample_shipments s
    JOIN fedex_service_tiers st ON s.service_id = st.id
    ORDER BY s.shipment_id
    """
    df2 = pd.read_sql_query(query2, conn)
    print(df2.to_string(index=False))
    print()
    
    # Query 3: Join shipments with rates to get costs
    logger.info("Query 3: Shipments with Calculated Costs")
    query3 = """
    SELECT 
        s.shipment_id,
        s.tracking_number,
        st.service_name,
        s.weight || ' lbs' as weight,
        'Zone ' || s.destination_zone as zone,
        ROUND(
            CASE st.column_name
                WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
                WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
                WHEN 'FedEx_Standard_Overnight' THEN r.FedEx_Standard_Overnight
                WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
                WHEN 'FedEx_2Day' THEN r.FedEx_2Day
                WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
            END, 2
        ) as cost
    FROM sample_shipments s
    JOIN fedex_service_tiers st ON s.service_id = st.id
    LEFT JOIN fedex_rates r ON r.Zone = s.destination_zone AND r.Weight = s.weight
    ORDER BY s.shipment_id
    """
    df3 = pd.read_sql_query(query3, conn)
    print(df3.to_string(index=False))
    print()
    
    # Query 4: Compare service options for a specific zone/weight
    logger.info("Query 4: Service Options for Zone 3, 25 lbs")
    query4 = """
    SELECT 
        st.service_name,
        st.delivery_day,
        st.delivery_deadline,
        ROUND(
            CASE st.column_name
                WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
                WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
                WHEN 'FedEx_Standard_Overnight' THEN r.FedEx_Standard_Overnight
                WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
                WHEN 'FedEx_2Day' THEN r.FedEx_2Day
                WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
            END, 2
        ) as rate
    FROM fedex_service_tiers st
    CROSS JOIN fedex_rates r
    WHERE r.Zone = 3 AND r.Weight = 25
    ORDER BY rate
    """
    df4 = pd.read_sql_query(query4, conn)
    print(df4.to_string(index=False))
    print()
    
    # Query 5: Average shipping cost by service tier
    logger.info("Query 5: Average Cost by Service Tier (for 50 lbs)")
    query5 = """
    SELECT 
        st.service_name,
        st.delivery_day,
        ROUND(AVG(
            CASE st.column_name
                WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
                WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
                WHEN 'FedEx_Standard_Overnight' THEN r.FedEx_Standard_Overnight
                WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
                WHEN 'FedEx_2Day' THEN r.FedEx_2Day
                WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
            END
        ), 2) as avg_cost
    FROM fedex_service_tiers st
    CROSS JOIN fedex_rates r
    WHERE r.Weight = 50
    GROUP BY st.id, st.service_name, st.delivery_day
    ORDER BY avg_cost
    """
    df5 = pd.read_sql_query(query5, conn)
    print(df5.to_string(index=False))
    print()
    
    logger.success("✅ All example queries completed")


def main() -> None:
    """Main execution workflow."""
    project_root = Path(__file__).parent.parent
    db_path = project_root / "fedex_rates.db"
    
    if not db_path.exists():
        logger.error(f"❌ Database not found: {db_path}")
        logger.error("Please run load_to_sqlite.py first")
        return
    
    logger.info("\n" + "="*70)
    logger.info("CREATING FEDEX SERVICE TIERS TABLE")
    logger.info("="*70 + "\n")
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        
        # Step 1: Create and populate service tiers
        create_service_tiers_table(conn)
        populate_service_tiers(conn)
        print()
        
        # Step 2: Create and populate sample shipments
        create_sample_shipments_table(conn)
        populate_sample_shipments(conn)
        print()
        
        # Step 3: Run example queries
        run_example_queries(conn)
        
        # Close connection
        conn.close()
        
        logger.info("\n" + "="*70)
        logger.success("✅ SERVICE TIERS SETUP COMPLETE")
        logger.info("="*70)
        logger.info("\nTables created:")
        logger.info("  • fedex_service_tiers (6 services)")
        logger.info("  • sample_shipments (8 sample records)")
        logger.info("\n📝 Now update sqltester.py to use these joins!\n")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()



