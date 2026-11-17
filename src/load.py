from collections.abc import Iterator

import pandas as pd

from .config import GTFS_FILES, GTFS_FILE_NAMES

def load_gtfs_file(
        file_name: str,
        *,
        columns: list[str] | None = None,
        dtype: dict[str: str] | None = None,
) -> pd.DataFrame:
    """Load a GTFS file into a DataFrame.

    Args:
        file_name: The name of the GTFS file to load (e.g., "agency", "routes").
        columns: The columns to load. If None, load all columns.
        dtype: The data type to use for each specified column. If None, automatically infer data types.

    Returns:
        A DataFrame containing the contents of the specified GTFS file.
    """
    if file_name not in GTFS_FILES:
        raise ValueError(f"Invalid GTFS file name: {file_name}. Must be one of {GTFS_FILE_NAMES}.")

    file_path = GTFS_FILES[file_name]
    return pd.read_csv(
        file_path,
        usecols=columns,
        dtype=dtype
    )


def iter_gtfs_file(
    file_name: str,
    *,
    columns: list[str],
    dtype: dict[str, str],
    chunksize: int = 100_000,
) -> Iterator[pd.DataFrame]:
    """Read selected GTFS columns in chunks to limit memory use.

    Args:
        file_name: Key of a file in ``GTFS_FILES``.
        columns: Columns to read from the file.
        dtype: pandas data types for those columns.
        chunksize: Maximum number of rows per chunk.

    Returns:
        An iterator of DataFrames with the requested columns and data types.

    Raises:
        ValueError: If ``file_name`` is not in ``GTFS_FILES``.
    """
    if file_name not in GTFS_FILES:
        raise ValueError(f"Invalid GTFS file name: {file_name}.")
    return pd.read_csv(
        GTFS_FILES[file_name], usecols=columns, dtype=dtype, chunksize=chunksize
    )
