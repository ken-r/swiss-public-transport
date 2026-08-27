from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import time

import pandas as pd

from .config import GTFS_FILES, GTFS_FILE_NAMES, PROJECT_ROOT


GTFS_SUMMARY_PATH = PROJECT_ROOT / "output" / "gtfs_summary.md"


def check_unique_column(df: pd.DataFrame, column_name: str) -> bool:
    """Check whether a column of a DataFrame only contains unique values.

    Args:
        df: The DataFrame to check for a unique column.
        column_name: The column name of the column that should be checked.

    Returns:
        True if the column only contains unique values, False otherwise.
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
    """Load a GTFS file into a DataFrame.

    Args:
        file_name: The name of the GTFS file to load (e.g., "agency", "routes").

    Returns:
        A DataFrame containing the contents of the specified GTFS file.
    """
    if file_name not in GTFS_FILES:
        raise ValueError(f"Invalid GTFS file name: {file_name}. Must be one of {GTFS_FILE_NAMES}.")

    file_path = GTFS_FILES[file_name]
    return pd.read_csv(file_path)

@dataclass
class GTFSSummary:
    file_name: str
    load_time: float
    n_rows: int
    n_cols: int
    column_names: list[str]
    first_five_rows: pd.DataFrame

    def __str__(self) -> str:
        return (
            f"Summary of {self.file_name}\n"
            f"Time to load from disk: {self.load_time:.2f}s.\n"
            f"Number of columns / Number of rows: {self.n_cols} / {self.n_rows}\n"
            f"Column names: {self.column_names}\n"
            f"First five rows:\n"
            f"{self.first_five_rows.to_string(index=False)}"
        )

    def to_markdown(self) -> str:
        columns = "\n".join(f"- `{column}`" for column in self.column_names)
        return (
            f"## {self.file_name}\n\n"
            f"- Load time: {self.load_time:.2f}s\n"
            f"- Number of rows: {self.n_rows}\n"
            f"- Number of columns: {self.n_cols}\n\n"
            f"### Column names\n\n"
            f"{columns}\n\n"
            f"### First five rows\n\n"
            f"```text\n{self.first_five_rows.to_string(index=False)}\n```\n"
        )

def build_gtfs_summary(file_name: str) -> GTFSSummary:
    """Build a summary of a GTFS file.

    Args:
        file_name: The name of the GTFS file to summarize.

    Returns:
        A GTFSSummary object containing the summary information.
    """
    start_time = time.perf_counter()
    df = load_gtfs_file(file_name)
    load_time = time.perf_counter() - start_time
    n_rows = len(df)
    column_names = list(df.columns)
    n_cols = len(column_names)
    first_five_rows = df.head()

    return GTFSSummary(
        file_name=file_name,
        load_time=load_time,
        n_rows=n_rows,
        n_cols=n_cols,
        column_names=column_names,
        first_five_rows=first_five_rows
    )

def print_summaries(gtfs_summaries: list[GTFSSummary]) -> None:
    """Print the summaries of GTFS files to the console.

    Args:
        gtfs_summaries: A list of GTFSSummary objects to print.
    
    """
    for gtfs_summary in gtfs_summaries:
        print(f"\n{'=' * 60}")
        print(gtfs_summary)
        print("=" * 60)


def write_markdown_report(gtfs_summaries: list[GTFSSummary], report_path: Path) -> None:
    """Write a markdown report of the GTFS summaries to a file.
    
    Args:
        gtfs_summaries: A list of GTFSSummary objects to include in the report.
        report_path: The path to the markdown file where the report will be written.
    """
    report_path.parent.mkdir(parents=True, exist_ok=True)
    sections = [summary.to_markdown() for summary in gtfs_summaries]
    report_path.write_text("# GTFS Dataset Summary\n\n" + "\n".join(sections), encoding="utf-8")


def analyze_gtfs_files(file_names: list[str]) -> list[GTFSSummary]:
    """Analyze a list of GTFS files and return their summaries.
    
    Args:
        file_names: A list of GTFS file names to analyze.
    
    Returns:
        A list of GTFSSummary objects containing the summary information for each file.
    """
    gtfs_summaries = []
    for file_name in file_names:
        gtfs_summary = build_gtfs_summary(file_name)
        gtfs_summaries.append(gtfs_summary)
    return gtfs_summaries


def main() -> None:
    gtfs_summaries = analyze_gtfs_files(GTFS_FILE_NAMES)
    print_summaries(gtfs_summaries)
    write_markdown_report(gtfs_summaries, GTFS_SUMMARY_PATH)
    print(f"\nMarkdown report written to {GTFS_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
