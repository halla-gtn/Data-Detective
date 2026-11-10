
import pandas as pd
from pathlib import Path


def load_dataset(file_path):
    """
    Load a dataset from a CSV or Excel file.

    Parameters
    ----------
    file_path : str or Path
        Path to the dataset.

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension == ".csv":
        return pd.read_csv(file_path)

    elif extension in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    else:
        raise ValueError(
            "Unsupported file format. "
            "Please use CSV or Excel files."
        )

