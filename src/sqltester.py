# =============================================================================
#  Filename: sqltester.py
#
#  Short Description: Test queries for FedEx rates database with service tiers
#
#  Creation date: 2025-10-08
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Test various SQL queries including joins with fedex_service_tiers table.
"""

import sqlite3

import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("fedex_rates.db")

print("="*70)
print("FEDEX RATES DATABASE - SQL QUERY TESTS")
print("="*70 + "\n")

# ============================================================================
# BASIC QUERIES (Original)
# ============================================================================

print("📊 BASIC QUERIES\n")

# Example 1: Count rows
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM fedex_rates;")
count = cursor.fetchone()[0]
print(f"1. Total records in fedex_rates: {count}")

# Example 2: Show distinct zones
zones = pd.read_sql_query(
    "SELECT DISTINCT Zone FROM fedex_rates ORDER BY Zone LIMIT 5;",
    conn
)
print(f"\n2. Sample Zones:\n{zones.to_string(index=False)}")

# Example 3: Sample weight range
range_df = pd.read_sql_query(
    "SELECT MIN(Weight) as MinWeight, MAX(Weight) as MaxWeight FROM fedex_rates;",
    conn
)
print(f"\n3. Weight range:\n{range_df.to_string(index=False)}")

# Example 4: Preview data
sample = pd.read_sql_query("SELECT * FROM fedex_rates LIMIT 5;", conn)
print(f"\n4. Sample records:\n{sample.to_string(index=False)}")

# Example 5: Total count
total = pd.read_sql_query(
    "SELECT count(*) as TotalRecords FROM fedex_rates;",
    conn
)
print(f"\n5. Total records:\n{total.to_string(index=False)}")

# ============================================================================
# SERVICE TIERS QUERIES (NEW)
# ============================================================================

print("\n" + "="*70)
print("📦 SERVICE TIERS QUERIES (NEW)\n")

# Check if service tiers table exists
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='fedex_service_tiers';
""")
service_table_exists = cursor.fetchone() is not None

if service_table_exists:
    # Example 6: Show all service tiers
    services = pd.read_sql_query(
        "SELECT * FROM fedex_service_tiers ORDER BY id;",
        conn
    )
    print(f"6. All FedEx Service Tiers:\n{services.to_string(index=False)}")
    
    # Example 7: Join rates with service descriptions for Zone 2, Weight 10
    query7 = """
    SELECT 
        r.Zone,
        r.Weight,
        s.service_name,
        s.delivery_time_desc,
        CASE s.column_name
            WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
            WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
            WHEN 'FedEx_Standard_Overnight' THEN r.FedEx_Standard_Overnight
            WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
            WHEN 'FedEx_2Day' THEN r.FedEx_2Day
            WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
        END as rate
    FROM fedex_rates r
    CROSS JOIN fedex_service_tiers s
    WHERE r.Zone = 2 AND r.Weight = 10
    ORDER BY rate;
    """
    result7 = pd.read_sql_query(query7, conn)
    print(f"\n7. All services for Zone 2, 10 lbs (sorted by price):\n{result7.to_string(index=False)}")
    
    # Example 8: Find cheapest service for Zone 5, 50 lbs
    query8 = """
    WITH service_rates AS (
        SELECT 
            s.service_name,
            s.delivery_time_desc,
            CASE s.column_name
                WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
                WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
                WHEN 'FedEx_Standard_overnight' THEN r.FedEx_Standard_Overnight
                WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
                WHEN 'FedEx_2Day' THEN r.FedEx_2Day
                WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
            END as rate
        FROM fedex_rates r
        CROSS JOIN fedex_service_tiers s
        WHERE r.Zone = 5 AND r.Weight = 50
    )
    SELECT service_name, delivery_time_desc, ROUND(rate, 2) as rate
    FROM service_rates
    WHERE rate = (SELECT MIN(rate) FROM service_rates);
    """
    result8 = pd.read_sql_query(query8, conn)
    print(f"\n8. Cheapest service for Zone 5, 50 lbs:\n{result8.to_string(index=False)}")
    
    # Example 9: Compare delivery speeds vs cost for Zone 3, 25 lbs
    query9 = """
    SELECT 
        s.delivery_day,
        s.service_name,
        s.delivery_deadline,
        ROUND(
            CASE s.column_name
                WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
                WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
                WHEN 'FedEx_Standard_Overnight' THEN r.FedEx_Standard_Overnight
                WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
                WHEN 'FedEx_2Day' THEN r.FedEx_2Day
                WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
            END, 2
        ) as rate
    FROM fedex_rates r
    CROSS JOIN fedex_service_tiers s
    WHERE r.Zone = 3 AND r.Weight = 25
    ORDER BY 
        CASE s.delivery_day
            WHEN 'Next day' THEN 1
            WHEN '2nd day' THEN 2
            WHEN '3rd day' THEN 3
        END,
        rate;
    """
    result9 = pd.read_sql_query(query9, conn)
    print(f"\n9. Delivery speed vs cost for Zone 3, 25 lbs:\n{result9.to_string(index=False)}")
    
    # Example 10: Average rates by delivery tier across all zones
    query10 = """
    SELECT 
        s.delivery_day,
        COUNT(DISTINCT r.Zone) as num_zones,
        ROUND(AVG(
            CASE s.column_name
                WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
                WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
                WHEN 'FedEx_Standard_Overnight' THEN r.FedEx_Standard_Overnight
                WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
                WHEN 'FedEx_2Day' THEN r.FedEx_2Day
                WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
            END
        ), 2) as avg_rate,
        ROUND(MIN(
            CASE s.column_name
                WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
                WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
                WHEN 'FedEx_Standard_Overnight' THEN r.FedEx_Standard_Overnight
                WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
                WHEN 'FedEx_2Day' THEN r.FedEx_2Day
                WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
            END
        ), 2) as min_rate,
        ROUND(MAX(
            CASE s.column_name
                WHEN 'FedEx_First_Overnight' THEN r.FedEx_First_Overnight
                WHEN 'FedEx_Priority_Overnight' THEN r.FedEx_Priority_Overnight
                WHEN 'FedEx_Standard_Overnight' THEN r.FedEx_Standard_Overnight
                WHEN 'FedEx_2Day_AM' THEN r.FedEx_2Day_AM
                WHEN 'FedEx_2Day' THEN r.FedEx_2Day
                WHEN 'FedEx_Express_Saver' THEN r.FedEx_Express_Saver
            END
        ), 2) as max_rate
    FROM fedex_rates r
    CROSS JOIN fedex_service_tiers s
    WHERE r.Weight = 50
    GROUP BY s.delivery_day
    ORDER BY 
        CASE s.delivery_day
            WHEN 'Next day' THEN 1
            WHEN '2nd day' THEN 2
            WHEN '3rd day' THEN 3
        END;
    """
    result10 = pd.read_sql_query(query10, conn)
    print(f"\n10. Average rates by delivery tier (50 lbs across all zones):\n{result10.to_string(index=False)}")
    
    # Check for sample_shipments table
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='sample_shipments';
    """)
    shipments_exist = cursor.fetchone() is not None
    
    if shipments_exist:
        # Example 11: Shipments with service details and costs
        query11 = """
        SELECT 
            sh.shipment_id,
            sh.tracking_number,
            st.service_name,
            st.delivery_time_desc,
            sh.weight || ' lbs' as weight,
            'Zone ' || sh.destination_zone as dest_zone,
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
        FROM sample_shipments sh
        JOIN fedex_service_tiers st ON sh.service_id = st.id
        LEFT JOIN fedex_rates r ON r.Zone = sh.destination_zone AND r.Weight = sh.weight
        ORDER BY sh.shipment_id;
        """
        result11 = pd.read_sql_query(query11, conn)
        print(f"\n11. Sample shipments with costs:\n{result11.to_string(index=False)}")
    else:
        print("\n11. Sample shipments table not found. Run create_service_tiers.py first.")

else:
    print("⚠️  fedex_service_tiers table not found!")
    print("   Run: uv run python src/create_service_tiers.py")

# Close connection
conn.close()

print("\n" + "="*70)
print("✅ ALL QUERIES COMPLETED")
print("="*70)
