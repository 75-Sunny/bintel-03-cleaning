"""data_prep_products.py - example.

An example of cleaning and preparing raw smart sales data.
Cleaning and preparation is a critical step in any BI workflow.
It is different for every project and every dataset.

This example is designed to be copied and modified.
On new datasets, you will need to change the cleaning and preparation logic.
This example is only an illustration.

Cleaning can be 80-90% of the work in a BI project.
It is often the most time-consuming step and
to do it well requires domain knowledge, attention to detail,
tenacity, and resourcefulness.

It is often the most important step because
if the data is not clean, the analysis will be wrong and
the business decisions will be wrong.

Common cleaning and preparation tasks include:
- Remove duplicate rows.
- Remove rows with missing or invalid values.
- Normalize inconsistent values (e.g., "East", "east", " EAST ").
- Convert data types (e.g., text to numeric, text to datetime).

Author: Denise Case
Date: 2026-06

Process:
    - Load raw CSV data files.
    - Clean and prepare each dataset.
    - Verify data quality after cleaning.
    - Save prepared data to data/prepared/.

Data Source:
- data/raw/products_data.csv

Output:
- data/prepared/products_data_prepared.csv

Terminal command to run this file from the root project folder:

uv run python -m bizintel.data_prep_products

OBS:
  Don't edit this file - it should remain a working example.
  Copy it, rename it with your alias, and modify your copy.
  If you do, include your command to run it in the docstring above and in README.md.
"""

# === DECLARE IMPORTS (bring in free code from elsewhere) ===

from pathlib import Path
from typing import Final

from datafun_toolkit.logger import log_path
import pandas as pd

from bizintel.utils_data import (
    check_quality,
    inspect_basic,
    load_data,
    summarize_numeric,
)
from bizintel.utils_logger import LOG, log_header

# === DECLARE GLOBAL CONSTANTS AND CONFIGURATION ===

# Raw data folder path (relative to the root project folder).
DATA_RAW: Final[Path] = Path("data/raw")

# Prepared data folder path (relative to the root project folder).
DATA_PREPARED: Final[Path] = Path("data/prepared")

# Input files.
CUSTOMERS_FILE: Final[Path] = DATA_RAW / "customers_data.csv"
PRODUCTS_FILE: Final[Path] = DATA_RAW / "products_data.csv"


# Output files.
PRODUCTS_PREPARED: Final[Path] = DATA_PREPARED / "products_data_prepared.csv"


# === Section 2. Define Reusable Functions ===


# === Section 2.2 DEFINE A PREPARE PRODUCTS FUNCTION ===

# Define a reusable function that takes the products DataFrame,
# cleans it, and returns a prepared DataFrame ready for the warehouse.


def prepare_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the products DataFrame.

    WHY: Even clean-looking data should be verified.
    We confirm types and check for unexpected values.

    Args:
        df: Raw products DataFrame.

    Returns:
        Cleaned products DataFrame.
    """
    LOG.info("Preparing products data")

    # Make a copy to avoid modifying the original DataFrame.
    # This ensures the original raw DataFrame is not changed.
    df = df.copy()

    LOG.info("Products Prep 1. Convert UnitPrice to numeric")

    # Select the UnitPrice column from the DataFrame.
    # A column is a Series - a single column of values.
    price_column = df["UnitPrice"]

    # Call pd.to_numeric() to convert the column to numeric values.
    # errors="coerce" means any value that cannot be converted
    # (like text or symbols) will be replaced with NaN (not a number).
    price_numeric = pd.to_numeric(price_column, errors="coerce")

    # Put the converted values back into the UnitPrice column.
    df["UnitPrice"] = price_numeric

    # Log how many prices could not be converted.
    bad_prices: int = int(df["UnitPrice"].isna().sum())
    LOG.info(f"  Non-numeric prices replaced with NaN: {bad_prices}")

    LOG.info("Products Prep 2. Remove duplicate rows")

    # Remove duplicate rows - keep the first occurrence.
    # before and after let us see how many rows were removed.
    before: int = df.shape[0]
    df = df.drop_duplicates()
    after: int = df.shape[0]

    LOG.info(f"  Rows before: {before}")
    LOG.info(f"  Rows after: {after}")
    LOG.info(f"  Removed {before - after} duplicate row(s)")
    LOG.info(f"  Products prepared: {df.shape[0]} rows")
    return df


# === Section 2.4 DEFINE A SAVE FUNCTION ===

# Define a reusable function that saves a prepared DataFrame
# to a CSV file in the data/prepared/ folder.


def save_prepared(df: pd.DataFrame, filepath: Path, name: str) -> None:
    """Save a prepared DataFrame to CSV.

    WHY: Saving prepared data to a separate folder keeps raw data
    untouched and gives downstream steps a clean input to work from.

    Args:
        df: Prepared DataFrame to save.
        filepath: Path to the output CSV file.
        name: A short name for logging.

    Returns:
        None
    """
    # Create the output folder if it does not exist
    # parents=True means create any missing parent folders as well.
    # exist_ok=True means
    # do not raise an error (it's ok) if the folder already exists.
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Call the df.to_csv() method to save the DataFrame to a CSV file.
    # Pass in the filepath where the file should be saved.
    # Set the index parameter to False to avoid saving the index column.
    # This is important because the index is not part of the original data
    # and should not be included in the saved file.
    df.to_csv(filepath, index=False)

    # Use df.shape[0] to get the number of rows in the DataFrame.
    row_count: int = df.shape[0]

    # Log useful information about the saved file,
    # including the number of rows and the file path.
    LOG.info(f"Saved {name}")
    LOG.info(f"  Rows: {row_count}")
    LOG.info(f"  Path: {filepath}")


# === MAIN FUNCTION ===


def main() -> None:
    """Main function to run the data preparation logic.

    This is where the main logic starts
    when this script is run.
    """
    # First, log the header for the BI module to indicate the start of the workflow.
    log_header(LOG, "BI")

    LOG.info("========================")
    LOG.info("START main()")
    LOG.info("========================")

    log_path(LOG, "Raw data:     ", DATA_RAW)
    log_path(LOG, "Prepared data:", DATA_PREPARED)

    LOG.info("Task 1. LOAD. Call a function to load each dataset......")
    df_products = load_data(PRODUCTS_FILE, "products")

    LOG.info("Task 2. INSPECT. Call a function to inspect each dataset...")
    inspect_basic(df_products, "products")

    LOG.info("Task 3. CHECK QUALITY BEFORE........")
    check_quality(df_products, "products")

    LOG.info("Task 4. SUMMARIZE BEFORE.......... ")
    summarize_numeric(df_products, "products")

    LOG.info("Task 5. PREPARE DATASETS.........")
    df_products_prepared = prepare_products(df_products)

    LOG.info("Task 6. CHECK QUALITY AFTER PREPARATION........")
    check_quality(df_products_prepared, "products prepared")

    LOG.info("Task 7. SUMMARIZE AFTER PREPARATION........")
    summarize_numeric(df_products_prepared, "products prepared")

    LOG.info("Task 8. SAVE PREPARED DATASETS........")
    save_prepared(df_products_prepared, PRODUCTS_PREPARED, "products")

    LOG.info("Workflow complete")
    LOG.info("========================")
    LOG.info("Executed successfully!")
    LOG.info("========================")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    # This conditional ensures that main() is only called
    # when this script is run directly, not when imported.
    main()
