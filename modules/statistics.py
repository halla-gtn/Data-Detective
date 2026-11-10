
import pandas as pd


def get_numeric_statistics(df):
    """
    Generate descriptive statistics for numerical columns.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.empty:
        return pd.DataFrame()

    return numeric_df.describe().T


def get_categorical_statistics(df):
    """
    Generate descriptive statistics for categorical columns.
    """

    categorical_df = df.select_dtypes(
        include=["object", "category", "string"]
    )

    if categorical_df.empty:
        return pd.DataFrame()

    results = []

    for column in categorical_df.columns:

        most_frequent = df[column].mode()

        results.append({
            "Column": column,
            "Unique Values": df[column].nunique(),
            "Most Frequent Value": (
                most_frequent.iloc[0]
                if not most_frequent.empty
                else None
            ),
            "Frequency": (
                int(df[column].value_counts().iloc[0])
                if not df[column].value_counts().empty
                else 0
            )
        })

    return pd.DataFrame(results)

