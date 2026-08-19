import time
import pandas as pd

from .config import GTFS_FILES, GTFS_FILE_NAMES


def summarize_df(df: pd.DataFrame, name: str=None) -> None:
    """
    Prints some summary information about a DataFrame.

    Args:
       df (pd.DataFrame): The DataFrame to summarize.
       name (str): The name that should be displayed before the summary of the df (optional).
    """
    if name:
        print(f"Summary of {name}:")
    print(f"Number of rows in the DataFrame: {len(df)}.")
    column_names = df.columns
    print(f"Number of columns in the DataFrame: {len(column_names)}")
    print(f"Column names in the DataFrame:\n{', '.join(column_names)}")
    print(f"First 5 rows:\n{df.head()}")

def check_unique_column(df: pd.DataFrame, column_name: str) -> bool:
    """
    Checks whether a column of a DataFrame only contains unique values.

    Args:
        df (pd.DataFrame): The DataFrame to check for a unique column.
        column_name (str): The column that should be checked.

    Returns:
        bool: True if the column only contains unique values, False otherwise.
    """
    unique_values = df[column_name].unique()
    n_unique_values = len(unique_values)
    n_df = len(df)
    if n_unique_values == n_df:
        print(f"Column {column_name} only contains unique values.")
    else:
        print(f"Column {column_name} contains some values that appear more than once.")

    return n_unique_values == n_df

def load_gtfs_file(file_name: str) -> pd.DataFrame:
    """
    Load a GTFS file into a pandas DataFrame.

    Args:
        file_name (str): The name of the GTFS file to load (e.g., "agency", "routes").

    Returns:
        pd.DataFrame: A DataFrame containing the contents of the specified GTFS file.
    """
    if file_name not in GTFS_FILES:
        raise ValueError(f"Invalid GTFS file name: {file_name}. Must be one of {GTFS_FILE_NAMES}.")

    file_path = GTFS_FILES[file_name]
    return pd.read_csv(file_path)

def analyze_gtfs_files(file_names: list[str]):
    for file_name in file_names:
        print(f"\n{'=' * 60}")
        print(f"Analyzing: {file_name}")
        print("=" * 60)
        start_time = time.perf_counter()
        df = load_gtfs_file(file_name)
        load_time = time.perf_counter() - start_time
        print(f"Time to load: {load_time:.2f} seconds.")
        summarize_df(df)
        print("-" * 60)

def main() -> None:
    analyze_gtfs_files(GTFS_FILE_NAMES)


if __name__ == "__main__":
    main()
