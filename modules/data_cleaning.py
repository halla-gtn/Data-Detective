
"""Data cleaning utilities for Data Detective."""

import pandas as pd


def clean_missing_values(df, strategy="mean_median_mode"):
    """Handle missing values using the selected strategy."""

    cleaned = df.copy()

    if strategy == "keep":
        return cleaned, 0

    if strategy == "remove_rows":
        before = len(cleaned)
        cleaned = cleaned.dropna()
        return cleaned, before - len(cleaned)

    if strategy == "mean_median_mode":

        for column in cleaned.columns:

            if cleaned[column].isna().sum() == 0:
                continue

            if pd.api.types.is_numeric_dtype(cleaned[column]):
                mean_value = cleaned[column].mean()
                median_value = cleaned[column].median()

                if pd.notna(mean_value):
                    cleaned[column] = cleaned[column].fillna(
                        median_value
                    )

            else:
                modes = cleaned[column].mode(dropna=True)

                if not modes.empty:
                    cleaned[column] = cleaned[column].fillna(
                        modes.iloc[0]
                    )

        return cleaned, 0

    raise ValueError("Unknown missing values strategy.")


def remove_duplicates(df):
    """Remove duplicated rows."""

    cleaned = df.copy()

    before = len(cleaned)
    cleaned = cleaned.drop_duplicates()

    return cleaned, before - len(cleaned)


def treat_outliers(df, method="keep", factor=1.5):
    """Treat numerical outliers using the IQR method."""

    cleaned = df.copy()
    numeric_columns = cleaned.select_dtypes(include="number").columns

    outlier_count = 0

    if method == "keep":
        return cleaned, 0

    if method not in ["remove", "cap"]:
        raise ValueError("Unknown outlier treatment method.")

    outlier_mask = pd.Series(False, index=cleaned.index)

    bounds = {}

    for column in numeric_columns:

        q1 = cleaned[column].quantile(0.25)
        q3 = cleaned[column].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - factor * iqr
        upper = q3 + factor * iqr

        bounds[column] = (lower, upper)

        mask = (
            (cleaned[column] < lower) |
            (cleaned[column] > upper)
        )

        outlier_mask |= mask.fillna(False)

    if method == "remove":

        outlier_count = int(outlier_mask.sum())
        cleaned = cleaned.loc[~outlier_mask].copy()

    elif method == "cap":

        for column, (lower, upper) in bounds.items():

            mask = (
                (cleaned[column] < lower) |
                (cleaned[column] > upper)
            )

            outlier_count += int(mask.sum())

            cleaned[column] = cleaned[column].clip(
                lower=lower,
                upper=upper
            )

    return cleaned, outlier_count


def clean_dataset(
    df,
    missing_strategy="mean_median_mode",
    remove_duplicate_rows=True,
    outlier_method="keep",
    iqr_factor=1.5
):
    """Apply all selected cleaning operations."""

    original = df.copy()
    cleaned = df.copy()

    report = {
        "original_rows": len(original),
        "original_columns": len(original.columns),
        "missing_values_before": int(original.isna().sum().sum()),
        "duplicate_rows_before": int(original.duplicated().sum()),
    }

    # 1. Missing values
    cleaned, missing_rows_removed = clean_missing_values(
        cleaned, missing_strategy
    )

    report["missing_rows_removed"] = missing_rows_removed

    # 2. Duplicate rows
    if remove_duplicate_rows:
        cleaned, duplicates_removed = remove_duplicates(cleaned)
    else:
        duplicates_removed = 0

    report["duplicates_removed"] = duplicates_removed

    # 3. Outliers
    cleaned, outliers_treated = treat_outliers(
        cleaned,
        method=outlier_method,
        factor=iqr_factor
    )

    report["outliers_treated"] = outliers_treated

    # 4. Final report
    report["cleaned_rows"] = len(cleaned)
    report["cleaned_columns"] = len(cleaned.columns)
    report["missing_values_after"] = int(cleaned.isna().sum().sum())
    report["duplicate_rows_after"] = int(cleaned.duplicated().sum())

    return cleaned, report
