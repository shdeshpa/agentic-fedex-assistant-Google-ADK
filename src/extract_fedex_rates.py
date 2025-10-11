# =============================================================================
#  Filename: extract_fedex_rates.py
#
#  Short Description: Extract FedEx rate tables from Service Guide PDF
#
#  Creation date: 2025-10-08
#  Author: Shrinivas Deshpande
# =============================================================================

"""
Extract FedEx U.S. Express Package Rate Tables from PDF pages 13-30.
Follows COSTAR prompt specifications for clean tabular output.
"""

import re
from pathlib import Path
from typing import Any

import pandas as pd
import pdfplumber
from loguru import logger


class FedExRateExtractor:
    """Extract and validate FedEx rate tables from PDF."""

    COLUMNS = [
        "Zone",
        "Weight",
        "FedEx_First_Overnight",
        "FedEx_Priority_Overnight",
        "FedEx_Standard_Overnight",
        "FedEx_2Day_AM",
        "FedEx_2Day",
        "FedEx_Express_Saver",
    ]

    def __init__(self, pdf_path: Path) -> None:
        """Initialize extractor with PDF path."""
        self.pdf_path = pdf_path
        self.data: list[dict[str, Any]] = []

    def _clean_numeric(self, value: str) -> float | None:
        """Clean and convert string to numeric value."""
        if not value or value.strip() == "":
            return None

        # Remove currency, units, commas, spaces, asterisks, and periods at end
        cleaned = re.sub(r"[$,*\s]", "", str(value))
        cleaned = re.sub(r"lbs?\.?$", "", cleaned)  # Remove lb/lbs at end
        cleaned = cleaned.rstrip(".")  # Remove trailing periods

        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def extract_zone_tables(self, start_page: int = 13, end_page: int = 33) -> None:
        """
        Extract rate tables from specified pages.
        Zones 2-8, each spanning 3 pages.
        """
        zone_mapping = {
            (13, 15): 2,
            (16, 18): 3,
            (19, 21): 4,
            (22, 24): 5,
            (25, 27): 6,
            (28, 30): 7,
            (31, 33): 8,
        }

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_range, zone in zone_mapping.items():
                logger.info(f"Processing Zone {zone}, pages {page_range}")
                zone_data = self._extract_zone(
                    pdf, zone, page_range[0], page_range[1]
                )
                self.data.extend(zone_data)

    def _parse_multiline_cell(self, cell: str | None) -> list[str]:
        """Parse a cell that may contain multiple values on separate lines."""
        if not cell:
            return []
        # Split by newlines and clean each value
        values = [v.strip() for v in str(cell).split("\n") if v.strip()]
        return values

    def _extract_zone(
        self, pdf: pdfplumber.PDF, zone: int, start: int, end: int
    ) -> list[dict[str, Any]]:
        """Extract data for a single zone across its 3 pages."""
        zone_rows = []

        for page_num in range(start, end + 1):
            page = pdf.pages[page_num - 1]  # 0-indexed
            tables = page.extract_tables()

            if not tables:
                logger.warning(f"No tables found on page {page_num}")
                continue

            for table_idx, table in enumerate(tables):
                if not table or len(table) < 2:
                    continue

                # Look for the main rate table (has 8 columns)
                if len(table[0]) < 8:
                    continue

                # Process each row
                for row_idx, row in enumerate(table):
                    if not row or len(row) < 8:
                        continue

                    # Weight column is column index 1
                    # Rate columns are indices 2-7
                    weight_cell = row[1]
                    if not weight_cell:
                        continue

                    # Parse multi-line cells
                    weights = self._parse_multiline_cell(weight_cell)
                    rate_cols = [
                        self._parse_multiline_cell(row[i]) for i in range(2, 8)
                    ]

                    # Ensure all columns have same number of values
                    if not weights:
                        continue

                    num_values = len(weights)
                    if any(len(col) != num_values for col in rate_cols):
                        continue

                    # Process each weight/rate combination
                    for i in range(num_values):
                        weight = self._clean_numeric(weights[i])
                        if weight is None or weight < 1 or weight > 150:
                            continue

                        rates = [
                            self._clean_numeric(rate_cols[j][i])
                            for j in range(6)
                        ]

                        # Only add if we have some valid rate data
                        # Note: Using standard order as per headers
                        if any(r is not None for r in rates):
                            zone_rows.append(
                                {
                                    "Zone": zone,
                                    "Weight": int(weight),
                                    "FedEx_First_Overnight": rates[0],
                                    "FedEx_Priority_Overnight": rates[1],
                                    "FedEx_Standard_Overnight": rates[2],
                                    "FedEx_2Day_AM": rates[3],
                                    "FedEx_2Day": rates[4],
                                    "FedEx_Express_Saver": rates[5],
                                }
                            )

        logger.info(f"Zone {zone}: extracted {len(zone_rows)} rows")
        # Sort by weight and remove duplicates
        zone_rows.sort(key=lambda x: x["Weight"])
        return zone_rows

    def validate_against_reference(self, validation_csv: Path) -> None:
        """Validate extracted data against reference CSV."""
        validation_df = pd.read_csv(validation_csv)
        extracted_df = pd.DataFrame(self.data)

        logger.info(f"Extracted {len(extracted_df)} rows")
        logger.info(f"Validation set has {len(validation_df)} rows")

        # Check specific validation points
        for _, val_row in validation_df.iterrows():
            zone = val_row["Zone"]
            weight = val_row["Weight"]

            match = extracted_df[
                (extracted_df["Zone"] == zone) & (extracted_df["Weight"] == weight)
            ]

            if match.empty:
                logger.warning(f"Missing: Zone {zone}, Weight {weight}")
            else:
                # Compare values
                for col in self.COLUMNS[2:]:  # Skip Zone and Weight
                    expected = val_row[col]
                    actual = match.iloc[0][col]

                    if pd.notna(expected) and pd.notna(actual):
                        diff = abs(float(expected) - float(actual))
                        if diff > 0.01:  # Allow small rounding differences
                            logger.error(
                                f"Mismatch at Zone {zone}, Weight {weight}, "
                                f"{col}: expected {expected}, got {actual}"
                            )

    def save_to_csv(self, output_path: Path) -> None:
        """Save extracted data to CSV in COSTAR format."""
        df = pd.DataFrame(self.data)

        # Ensure proper column order
        df = df[self.COLUMNS]

        # Sort by Zone then Weight
        df = df.sort_values(["Zone", "Weight"])

        # Format numeric columns to 2 decimals
        for col in self.COLUMNS[2:]:
            df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

        # Save without index
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(df)} rows to {output_path}")


def main() -> None:
    """Main extraction workflow."""
    project_root = Path(__file__).parent.parent
    pdf_path = project_root / "data" / "Service_Guide_2025.pdf"
    validation_path = project_root / "validation_set_corrected.csv"
    output_path = project_root / "output" / "fedex_rates_final.csv"

    # Ensure output directory exists
    output_path.parent.mkdir(exist_ok=True)

    # Extract
    extractor = FedExRateExtractor(pdf_path)
    extractor.extract_zone_tables(start_page=13, end_page=33)

    # Validate
    extractor.validate_against_reference(validation_path)

    # Save
    extractor.save_to_csv(output_path)

    logger.success("Extraction complete!")


if __name__ == "__main__":
    main()

