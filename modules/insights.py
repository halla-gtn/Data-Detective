
import pandas as pd


def analyze_missing_values(df):
    """
    Analyze missing values and generate textual insights.
    """
    insights = []

    missing_counts = df.isna().sum()
    total_missing = int(missing_counts.sum())

    if total_missing == 0:
        insights.append({
            "category": "Missing Values",
            "message": "No missing values were detected."
        })
    else:
        insights.append({
            "category": "Missing Values",
            "message": (
                f"The dataset contains {total_missing} missing values."
            )
        })

        for column, count in missing_counts.items():
            if count > 0:
                percentage = (count / len(df)) * 100

                insights.append({
                    "category": "Missing Values",
                    "message": (
                        f"Column '{column}' contains {count} missing values "
                        f"({percentage:.2f}%)."
                    )
                })

    return insights


def analyze_duplicates(df):
    """
    Detect duplicate rows and generate textual insights.
    """
    insights = []

    duplicate_count = int(df.duplicated().sum())

    if duplicate_count == 0:
        insights.append({
            "category": "Duplicate Rows",
            "message": "No duplicate rows were detected."
        })
    else:
        percentage = (duplicate_count / len(df)) * 100

        insights.append({
            "category": "Duplicate Rows",
            "message": (
                f"The dataset contains {duplicate_count} duplicate rows "
                f"({percentage:.2f}%)."
            )
        })

    return insights


def analyze_outliers(df):
    """
    Detect numerical outliers using the IQR method.
    """
    insights = []

    numeric_columns = df.select_dtypes(include="number").columns

    if len(numeric_columns) == 0:
        insights.append({
            "category": "Outliers",
            "message": (
                "No numerical columns available for outlier analysis."
            )
        })
        return insights

    for column in numeric_columns:

        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = df[
            (df[column] < lower_bound) |
            (df[column] > upper_bound)
        ][column]

        outlier_count = len(outliers)

        if outlier_count > 0:
            insights.append({
                "category": "Outliers",
                "message": (
                    f"Column '{column}' contains {outlier_count} "
                    f"potential outlier(s)."
                )
            })
        else:
            insights.append({
                "category": "Outliers",
                "message": (
                    f"No outliers were detected in column '{column}'."
                )
            })

    return insights


def analyze_correlations(df, threshold=0.7):
    """
    Identify strong correlations between numerical columns.
    """
    insights = []

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        insights.append({
            "category": "Correlation",
            "message": (
                "At least two numerical columns are required "
                "for correlation analysis."
            )
        })
        return insights

    correlation_matrix = numeric_df.corr()

    for i in range(len(correlation_matrix.columns)):
        for j in range(i + 1, len(correlation_matrix.columns)):

            col1 = correlation_matrix.columns[i]
            col2 = correlation_matrix.columns[j]

            correlation = correlation_matrix.iloc[i, j]

            if pd.isna(correlation):
                continue

            if abs(correlation) >= threshold:

                relationship = (
                    "positive" if correlation > 0 else "negative"
                )

                insights.append({
                    "category": "Correlation",
                    "message": (
                        f"Strong {relationship} correlation detected "
                        f"between '{col1}' and '{col2}' "
                        f"(r = {correlation:.2f})."
                    )
                })

    if not insights:
        insights.append({
            "category": "Correlation",
            "message": (
                f"No strong correlations detected "
                f"(threshold = {threshold})."
            )
        })

    return insights

def generate_all_insights(df):
    """
    Generate all dataset insights in one operation.
    """
    all_insights = []

    all_insights.extend(analyze_missing_values(df))
    all_insights.extend(analyze_duplicates(df))
    all_insights.extend(analyze_outliers(df))
    all_insights.extend(analyze_correlations(df))

    return all_insights

