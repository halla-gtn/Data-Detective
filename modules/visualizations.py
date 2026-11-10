
import pandas as pd
import plotly.express as px


def create_histogram(df, column):
    """
    Create an interactive histogram for a numerical column.
    """

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise TypeError("Histogram requires a numerical column.")

    fig = px.histogram(
        df,
        x=column,
        title=f"Distribution of {column}",
        color_discrete_sequence=["#6366F1"],
        template="plotly_white"
    )

    fig.update_layout(
        xaxis_title=column,
        yaxis_title="Frequency",
        title_x=0.5
    )

    return fig


def create_bar_chart(df, column):
    """
    Create an interactive bar chart for a categorical column.
    """

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if not (
        pd.api.types.is_object_dtype(df[column])
        or pd.api.types.is_categorical_dtype(df[column])
        or pd.api.types.is_string_dtype(df[column])
    ):
        raise TypeError("Bar chart requires a categorical column.")

    value_counts = (
        df[column]
        .value_counts()
        .reset_index()
    )

    value_counts.columns = [column, "Count"]

    fig = px.bar(
        value_counts,
        x=column,
        y="Count",
        title=f"Distribution of {column}",
        color=column,
        template="plotly_white"
    )

    fig.update_layout(
        xaxis_title=column,
        yaxis_title="Number of occurrences",
        title_x=0.5,
        showlegend=False
    )

    return fig


def create_scatter_plot(df, x_column, y_column):
    """
    Create an interactive scatter plot between two numerical columns.
    """

    for column in [x_column, y_column]:

        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' does not exist."
            )

        if not pd.api.types.is_numeric_dtype(df[column]):
            raise TypeError(
                f"Column '{column}' must be numerical."
            )

    fig = px.scatter(
        df,
        x=x_column,
        y=y_column,
        title=f"{y_column} vs {x_column}",
        color_discrete_sequence=["#6366F1"],
        template="plotly_white",
        hover_data=df.columns.tolist()
    )

    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        title_x=0.5
    )

    return fig


def create_box_plot(df, column):
    """
    Create an interactive box plot for a numerical column.
    """

    if column not in df.columns:
        raise ValueError(
            f"Column '{column}' does not exist."
        )

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise TypeError(
            "Box plot requires a numerical column."
        )

    fig = px.box(
        df,
        y=column,
        title=f"Box Plot of {column}",
        points="outliers",
        color_discrete_sequence=["#8B5CF6"],
        template="plotly_white"
    )

    fig.update_layout(
        yaxis_title=column,
        title_x=0.5
    )

    return fig


def create_correlation_heatmap(df):
    """
    Create an interactive correlation heatmap
    for numerical columns.
    """

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        raise ValueError(
            "At least two numerical columns are required."
        )

    correlation_matrix = numeric_df.corr()

    fig = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Correlation Heatmap",
        template="plotly_white"
    )

    fig.update_layout(
        title_x=0.5,
        coloraxis_colorbar_title="Correlation"
    )

    return fig


from itertools import combinations


def suggest_visualizations(df):
    """
    Automatically recommend suitable visualizations
    based on dataset column types.
    """

    recommendations = []

    # Identify numerical columns
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    # Identify categorical columns
    categorical_columns = df.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    # 1. Numerical visualizations
    for column in numeric_columns:

        recommendations.append({
            "type": "Histogram",
            "columns": [column],
            "description": f"Distribution of {column}"
        })

        recommendations.append({
            "type": "Box Plot",
            "columns": [column],
            "description": f"Outlier analysis of {column}"
        })

    # 2. Categorical visualizations
    for column in categorical_columns:

        unique_count = df[column].nunique()

        # Avoid columns that look like identifiers
        if (
            2 <= unique_count <= 20
            and unique_count / max(len(df), 1) < 0.8
        ):

            recommendations.append({
                "type": "Bar Chart",
                "columns": [column],
                "description": f"Frequency distribution of {column}"
            })

    # 3. Relationships between numerical columns
    numeric_pairs = list(
        combinations(numeric_columns, 2)
    )

    # Limit the number of scatter plots
    for x_column, y_column in numeric_pairs[:3]:

        recommendations.append({
            "type": "Scatter Plot",
            "columns": [x_column, y_column],
            "description": f"Relationship between {x_column} and {y_column}"
        })

    # 4. Correlation heatmap
    if len(numeric_columns) >= 2:

        recommendations.append({
            "type": "Correlation Heatmap",
            "columns": numeric_columns,
            "description": "Correlation between numerical variables"
        })

    return recommendations


def generate_visualizations(df):
    """
    Generate all recommended visualizations automatically.

    Returns
    -------
    list
        A list of dictionaries containing visualization
        information and Plotly figures.
    """

    recommendations = suggest_visualizations(df)

    generated_figures = []

    for recommendation in recommendations:

        chart_type = recommendation["type"]
        columns = recommendation["columns"]

        # Select the appropriate visualization function
        if chart_type == "Histogram":
            fig = create_histogram(df, columns[0])

        elif chart_type == "Box Plot":
            fig = create_box_plot(df, columns[0])

        elif chart_type == "Bar Chart":
            fig = create_bar_chart(df, columns[0])

        elif chart_type == "Scatter Plot":
            fig = create_scatter_plot(
                df,
                columns[0],
                columns[1]
            )

        elif chart_type == "Correlation Heatmap":
            fig = create_correlation_heatmap(df)

        else:
            continue

        generated_figures.append({
            "type": chart_type,
            "columns": columns,
            "description": recommendation["description"],
            "figure": fig
        })

    return generated_figures

