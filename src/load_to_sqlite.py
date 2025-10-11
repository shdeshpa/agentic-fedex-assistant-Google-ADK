# =============================================================================
#  Filename: load_to_sqlite.py
#
#  Short Description: Load FedEx rates CSV into SQLite database with validation
#
#  Creation date: 2025-10-08
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Load FedEx rate data from CSV into SQLite database.
Follows COSTAR prompt specifications for data validation.
"""

import os
import sqlite3
from pathlib import Path

import pandas as pd
from loguru import logger


class FedExDatabaseLoader:
    """Load and validate FedEx rates in SQLite database."""

    def __init__(self, csv_path: Path, db_path: Path) -> None:
        """Initialize loader with file paths."""
        self.csv_path = csv_path
        self.db_path = db_path
        self.table_name = "fedex_rates"

    def remove_existing_database(self) -> None:
        """Remove existing database file if it exists."""
        if self.db_path.exists():
            logger.info(f"Removing existing database: {self.db_path}")
            os.remove(self.db_path)
            logger.success("✅ Existing database removed")
        else:
            logger.info("No existing database found")

    def load_csv_to_dataframe(self) -> pd.DataFrame:
        """Read CSV file into pandas DataFrame."""
        logger.info(f"Reading CSV file: {self.csv_path}")
        
        try:
            df = pd.read_csv(self.csv_path)
            logger.success(f"✅ CSV loaded successfully. Shape: {df.shape}")
            
            # Display column info
            logger.info(f"Columns: {list(df.columns)}")
            logger.info(f"Data types:\n{df.dtypes}")
            
            return df
            
        except FileNotFoundError:
            logger.error(f"❌ CSV file not found: {self.csv_path}")
            raise
        except pd.errors.EmptyDataError:
            logger.error("❌ CSV file is empty")
            raise
        except Exception as e:
            logger.error(f"❌ Error reading CSV: {e}")
            raise

    def create_database_and_load(self, df: pd.DataFrame) -> None:
        """Create SQLite database and load DataFrame."""
        logger.info(f"Creating database: {self.db_path}")
        
        try:
            # Create connection
            conn = sqlite3.connect(self.db_path)
            
            # Write DataFrame to SQLite
            # if_exists='replace' will drop and recreate the table
            # index=False prevents pandas index from being written
            df.to_sql(
                self.table_name,
                conn,
                if_exists="replace",
                index=False,
                dtype={
                    "Zone": "INTEGER",
                    "Weight": "INTEGER",
                    "FedEx_First_Overnight": "REAL",
                    "FedEx_Priority_Overnight": "REAL",
                    "FedEx_Standard_Overnight": "REAL",
                    "FedEx_2Day_AM": "REAL",
                    "FedEx_2Day": "REAL",
                    "FedEx_Express_Saver": "REAL",
                }
            )
            
            conn.close()
            logger.success(f"✅ Data loaded successfully into table '{self.table_name}'")
            
        except Exception as e:
            logger.error(f"❌ Error creating database: {e}")
            raise

    def run_validation_queries(self) -> None:
        """Execute validation SQL queries and display results."""
        logger.info("\n" + "="*70)
        logger.info("RUNNING VALIDATION QUERIES")
        logger.info("="*70 + "\n")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query 1: Total record count
            logger.info("📊 Query 1: Total Record Count")
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            count = cursor.fetchone()[0]
            logger.success(f"✅ Total records: {count:,} rows")
            print()
            
            # Query 2: First 5 rows
            logger.info("📊 Query 2: First 5 Rows")
            df_sample = pd.read_sql_query(
                f"SELECT * FROM {self.table_name} LIMIT 5",
                conn
            )
            print(df_sample.to_string(index=False))
            print()
            
            # Query 3: Unique zones
            logger.info("📊 Query 3: Unique Zones")
            cursor.execute(f"SELECT DISTINCT Zone FROM {self.table_name} ORDER BY Zone")
            zones = [row[0] for row in cursor.fetchall()]
            logger.success(f"✅ Zones found: {zones}")
            print()
            
            # Query 4: Weight range
            logger.info("📊 Query 4: Weight Range")
            cursor.execute(
                f"SELECT MIN(Weight) as Min_Weight, MAX(Weight) as Max_Weight "
                f"FROM {self.table_name}"
            )
            min_weight, max_weight = cursor.fetchone()
            logger.success(f"✅ Weight range: {min_weight} lbs to {max_weight} lbs")
            print()
            
            # Query 5: Example rate check (Zone 2, Weight 10)
            logger.info("📊 Query 5: Rate Check for Zone 2, Weight 10 lbs")
            df_example = pd.read_sql_query(
                f"SELECT * FROM {self.table_name} WHERE Zone = 2 AND Weight = 10",
                conn
            )
            if not df_example.empty:
                print(df_example.to_string(index=False))
                logger.success("✅ Rate data retrieved successfully")
            else:
                logger.warning("⚠️ No data found for Zone 2, Weight 10")
            print()
            
            # Additional Query 6: Records per zone
            logger.info("📊 Query 6: Records Per Zone (Distribution Check)")
            cursor.execute(
                f"SELECT Zone, COUNT(*) as Record_Count "
                f"FROM {self.table_name} GROUP BY Zone ORDER BY Zone"
            )
            zone_counts = cursor.fetchall()
            for zone, cnt in zone_counts:
                print(f"  Zone {zone}: {cnt:,} records")
            logger.success("✅ Zone distribution verified")
            print()
            
            # Additional Query 7: Sample rates for each zone at weight 50
            logger.info("📊 Query 7: Sample Rates at 50 lbs Across All Zones")
            df_weight50 = pd.read_sql_query(
                f"SELECT Zone, Weight, FedEx_2Day, FedEx_Express_Saver "
                f"FROM {self.table_name} WHERE Weight = 50 ORDER BY Zone",
                conn
            )
            print(df_weight50.to_string(index=False))
            logger.success("✅ Cross-zone rate comparison complete")
            print()
            
            conn.close()
            
            logger.info("="*70)
            logger.success("✅ ALL VALIDATION QUERIES COMPLETED SUCCESSFULLY")
            logger.info("="*70)
            
        except sqlite3.Error as e:
            logger.error(f"❌ SQLite error during validation: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error running validation queries: {e}")
            raise

    def verify_data_integrity(self) -> None:
        """Additional data integrity checks."""
        logger.info("\n" + "="*70)
        logger.info("DATA INTEGRITY CHECKS")
        logger.info("="*70 + "\n")
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Check for NULL values
            logger.info("🔍 Checking for NULL values in rate columns...")
            cursor = conn.cursor()
            rate_columns = [
                "FedEx_First_Overnight",
                "FedEx_Priority_Overnight",
                "FedEx_Standard_Overnight",
                "FedEx_2Day_AM",
                "FedEx_2Day",
                "FedEx_Express_Saver"
            ]
            
            has_nulls = False
            for col in rate_columns:
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.table_name} WHERE {col} IS NULL"
                )
                null_count = cursor.fetchone()[0]
                if null_count > 0:
                    logger.warning(f"⚠️  {col}: {null_count} NULL values")
                    has_nulls = True
            
            if not has_nulls:
                logger.success("✅ No NULL values found in rate columns")
            print()
            
            # Check for negative rates
            logger.info("🔍 Checking for negative or zero rates...")
            has_invalid = False
            for col in rate_columns:
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.table_name} WHERE {col} <= 0"
                )
                invalid_count = cursor.fetchone()[0]
                if invalid_count > 0:
                    logger.warning(f"⚠️  {col}: {invalid_count} invalid values")
                    has_invalid = True
            
            if not has_invalid:
                logger.success("✅ All rates are positive values")
            print()
            
            # Check weight coverage
            logger.info("🔍 Checking weight coverage (1-150 lbs)...")
            cursor.execute(
                f"SELECT Zone, COUNT(DISTINCT Weight) as weight_count "
                f"FROM {self.table_name} GROUP BY Zone"
            )
            weight_coverage = cursor.fetchall()
            all_complete = True
            for zone, count in weight_coverage:
                if count != 150:
                    logger.warning(f"⚠️  Zone {zone}: Only {count}/150 weights")
                    all_complete = False
            
            if all_complete:
                logger.success("✅ All zones have complete weight coverage (1-150 lbs)")
            print()
            
            conn.close()
            
            logger.info("="*70)
            logger.success("✅ DATA INTEGRITY CHECKS COMPLETE")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"❌ Error during integrity checks: {e}")
            raise


def main() -> None:
    """Main execution workflow."""
    # Setup paths (relative to project root)
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "output" / "fedex_rates_final.csv"
    db_path = project_root / "fedex_rates.db"
    
    logger.info("\n" + "="*70)
    logger.info("FEDEX RATES DATABASE LOADER")
    logger.info("="*70 + "\n")
    
    # Verify CSV exists
    if not csv_path.exists():
        logger.error(f"❌ CSV file not found: {csv_path}")
        logger.error("Please run extract_fedex_rates.py first")
        return
    
    # Initialize loader
    loader = FedExDatabaseLoader(csv_path, db_path)
    
    try:
        # Step 1: Remove existing database
        logger.info("STEP 1: Removing existing database (if any)")
        loader.remove_existing_database()
        print()
        
        # Step 2: Load CSV into DataFrame
        logger.info("STEP 2: Loading CSV data")
        df = loader.load_csv_to_dataframe()
        print()
        
        # Step 3: Create database and load data
        logger.info("STEP 3: Creating SQLite database and loading data")
        loader.create_database_and_load(df)
        print()
        
        # Step 4: Run validation queries
        logger.info("STEP 4: Running validation queries")
        loader.run_validation_queries()
        
        # Step 5: Data integrity checks
        logger.info("STEP 5: Running data integrity checks")
        loader.verify_data_integrity()
        
        # Final summary
        logger.info("\n" + "="*70)
        logger.success("✅ DATABASE CREATION COMPLETE!")
        logger.info(f"📁 Database location: {db_path}")
        logger.info(f"📊 Table name: {loader.table_name}")
        logger.info(f"📈 Total records: {len(df):,}")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Process failed: {e}")
        raise


if __name__ == "__main__":
    main()

