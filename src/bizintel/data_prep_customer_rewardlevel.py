"""data_prep_customer_rewardlevel.py - example.

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
- data/raw/customers_data.csv
- data/raw/products_data.csv
- data/raw/sales_data.csv

Output:
- data/prepared/customers_data_prepared_rewardlevel.csv


Terminal command to run this file from the root project folder:

uv run python -m bizintel.data_prep_customer_rewardlevel

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

# Output files.
CUSTOMERS_PREPARED: Final[Path] = (
    DATA_PREPARED / "customers_data_prepared_rewardlevel.csv"
)


# === Section 2. Define Reusable Functions ===

# === Section 2.1 DEFINE A PREPARE CUSTOMERS FUNCTION ===

# Define a reusable function that takes the customers DataFrame,
# cleans it, and returns a prepared DataFrame ready for the warehouse.


def prepare_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and prepare the customers DataFrame.

    WHY: Inconsistent region values and duplicate rows
    will cause problems in the warehouse and in reporting.
    We fix them here before loading.

    Args:
        df: Raw customers DataFrame.

    Returns:
        Cleaned customers DataFrame.
    """
    LOG.info("Preparing customers data")

    # Make a copy to avoid modifying the original DataFrame.
    # This ensures the original raw DataFrame is not changed.
    df = df.copy()

    LOG.info("Customers Prep 1. Normalize Region values")

    # Select the Region column from the DataFrame.
    # A column is a Series - a single column of values.
    region_column = df["Region"]

    # Use the built-in .str property to access string methods on every value.
    # .str.strip() removes leading and trailing whitespace from each value.
    stripped = region_column.str.strip()

    # .str.title() capitalizes the first letter of each word in each value.
    # So "east", "EAST", and " East " all become "East".
    titled = stripped.str.title()

    # Put the cleaned values back into the Region column of the DataFrame.
    df["Region"] = titled

    # Call the dropna() method to remove any rows where the Region value is missing (NaN).
    df["Region"] = df["Region"].dropna()

    # Call the unique() method and tolist() method chained together
    # to get unique region values after normalization and assign them to a list named regions.
    # You can modify your copy to chain more functions together.
    # This example is designed for teaching and clarity not production.
    regions: list[str] = df["Region"].unique().tolist()

    # Call the built-in Python sorted() function to sort the list of unique region values.
    regions_sorted: list[str] = sorted(regions)

    # Log the sorted unique region values
    # to verify cleaning and preparation.
    LOG.info(f"  Regions after normalization: {regions_sorted}")

    # NOTE: 'South-West' does not match any standard region.
    # In your copy of the data prep logic, you can
    # split into South and West,
    # or map to nearest region,
    # or keep as its own region.
    # The analyst makes a LOT of decisions during cleaning.
    # Think about what is "best" for your data and intent.
    # Always document your decisions and rationale.

    LOG.info("Customers Prep 2. Normalize RewardLevel values")

    # Select the RewardLevel column from the DataFrame.
    rewardlevel_column = df["RewardLevel"]

    # Strip leading and trailing whitespace and capitalize each value.
    df["RewardLevel"] = rewardlevel_column.str.strip().str.title()

    # Creates a list of valid reward levels:
    # Bronze
    # Silver
    # Platinum
    # Counts the number of invalid rows, counts the number of updated RewardLevel values.
    # then log the number of invalid rows and the number of updated RewardLevel values.
    # Find rows whose RewardLevel is not one of those values.
    # Use the RewardPoints value to assign:
    # Bronze if RewardPoints < 200000
    # Silver if 200000 <= RewardPoints < 300000
    # Platinum if RewardPoints >= 300000

    # Define valid reward levels.
    valid_levels = ["Bronze", "Silver", "Platinum"]

    # Find invalid RewardLevel values in order to include in results logging
    invalid = ~df["RewardLevel"].isin(valid_levels)
    # Create DataFrame of the invalid rows
    invalid_rows = df[invalid]

    # Assigns apprriate RewardLevel values based on RewardPoints for invalid rows.
    df.loc[
        invalid & (df["RewardPoints"] < 200000),
        "RewardLevel",
    ] = "Bronze"
    df.loc[
        invalid & (df["RewardPoints"] >= 200000) & (df["RewardPoints"] < 300000),
        "RewardLevel",
    ] = "Silver"
    df.loc[
        invalid & (df["RewardPoints"] >= 300000),
        "RewardLevel",
    ] = "Platinum"

    # Count the number of updated RewardLevel values for logging.
    updated_count = invalid_rows.shape[0]
    LOG.info(f"  Updated {updated_count} RewardLevel value(s)")

    # Log the invalid rows for review.
    LOG.info(f"  Invalid RewardLevel values found: {invalid_rows.shape[0]} rows")
    updated_count = invalid_rows.shape[0]

    # Identify rows where RewardLevel is not one of the valid values.
    LOG.info("Customers Prep 2. Remove duplicate rows")

    # Remove duplicate rows - keep the first occurrence.
    # before and after let us see how many rows were removed.
    # Remember that df.shape[0] gives the number of rows in the DataFrame.
    before: int = df.shape[0]
    df = df.drop_duplicates()
    after: int = df.shape[0]

    LOG.info(f"  Rows before: {before}")
    LOG.info(f"  Rows after: {after}")
    LOG.info(f"  Removed {before - after} duplicate row(s)")
    LOG.info(f"  Customers prepared: {df.shape[0]} rows")
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
    df_customers = load_data(CUSTOMERS_FILE, "customers")

    LOG.info("Task 2. INSPECT. Call a function to inspect each dataset...")
    inspect_basic(df_customers, "customers")

    LOG.info("Task 3. CHECK QUALITY BEFORE........")
    check_quality(df_customers, "customers")

    LOG.info("Task 4. SUMMARIZE BEFORE.......... ")
    summarize_numeric(df_customers, "customers")

    LOG.info("Task 5. PREPARE DATASETS.........")
    df_customers_prepared = prepare_customers(df_customers)

    LOG.info("Task 6. CHECK QUALITY AFTER PREPARATION........")
    check_quality(df_customers_prepared, "customers prepared")

    LOG.info("Task 7. SUMMARIZE AFTER PREPARATION........")
    summarize_numeric(df_customers_prepared, "customers prepared")

    LOG.info("Task 8. SAVE PREPARED DATASETS........")
    save_prepared(df_customers_prepared, CUSTOMERS_PREPARED, "customers")

    LOG.info("Workflow complete")
    LOG.info("========================")
    LOG.info("Executed successfully!")
    LOG.info("========================")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    # This conditional ensures that main() is only called
    # when this script is run directly, not when imported.
    main()
