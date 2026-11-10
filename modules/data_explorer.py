
import pandas as pd


def get_dataset_overview(df):
    """
    Return general information about a dataset.
    """

    overview = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage": int(df.memory_usage(deep=True).sum())
    }

    return overview


def get_column_information(df):
    """
    Return information about each dataset column.
    """

    column_info = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isna().sum().values,
        "Unique Values": df.nunique().values
    })

    return column_info
