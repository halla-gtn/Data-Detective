# Data Detective

**An Interactive Data Exploration and Analysis Tool**

[**Live Demo — Try Data Detective**](https://data-detective-halla-gtn.streamlit.app/)

Data Detective is a Python-based web application developed with Streamlit. It helps users explore, understand, analyze, and visualize datasets through an intuitive and interactive interface.

## Features

- **Dataset Overview:** Get a summary of the dataset, including dimensions, columns, and data types.
- **Data Exploration:** Examine individual columns and explore their contents.
- **Statistical Analysis:** Generate descriptive statistics for numerical and categorical variables.
- **Interactive Visualizations:** Create different types of charts to identify patterns, distributions, and relationships in data.
- **Data Filtering:** Filter datasets using interactive controls.
- **Data Insights:** Discover useful information and potential patterns in the dataset.
- **Export:** Download analysis results and processed data.
- **Light and Dark Modes:** Choose the interface appearance.

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- OpenPyXL

## Screenshots

Explore the application's interface and features through the project screenshots:

[View all screenshots](assets/screenshots/)

## Project Structure

```text
Data-Detective/
│
├── app.py
├── Data_Detective.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── modules/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── data_explorer.py
│   ├── statistics.py
│   ├── visualizations.py
│   └── insights.py
│
└── assets/
    ├── style.css
    └── screenshots/
```

## Installation and Local Execution

To run Data Detective locally:

1. Clone the repository:

```bash
git clone https://github.com/halla-gtn/Data-Detective.git
```

2. Navigate to the project directory:

```bash
cd Data-Detective
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Launch the application:

```bash
streamlit run app.py
```

## Deployment

Data Detective is deployed using Streamlit Community Cloud and is publicly accessible through the following link:

[https://data-detective-halla-gtn.streamlit.app/](https://data-detective-halla-gtn.streamlit.app/)

## Project Objective

Data Detective aims to make data exploration and analysis more accessible by providing an interactive environment where users can examine datasets, generate visualizations, and gain insights without writing extensive analysis code.

## Author

Developed as a personal Python data analysis project.
