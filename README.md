# PICO Dashboard

## Overview

The PICO Dashboard is a web application designed to provide interactive data visualization. It leverages the `shiny` framework for the user interface and various data processing and visualization libraries.

## Requirements

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

1. **Clone the repository:**

```bash
git clone https://github.com/suriija/picovizdash.git
cd picovizdash
```

2. **Install the dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the application:**

```bash
shiny run --reload --launch-browser app.py
```

Replace `app.py` with the actual entry point script of your application if it's named differently.

## File Structure

- `app.py`: Main application script.
- `data_loading.py`: Script for loading data from Excel and SQLite.
- `plotting.py`: Functions for generating various plots and charts.
- `ui_components.py`: Functions for creating UI components.
- `requirements.txt`: List of dependencies.
- `README.md`: This file.

## Data Sources

- `Transformed.xlsx`: Excel file containing the transformed data. (Outcome)
- `newdigaDB.db`: SQLite database. (DiGA Information, PICO Information)

## Dependencies

- `shiny==0.1.0`
- `shinywidgets==0.1.0`
- `pandas==1.3.3`
- `numpy==1.21.2`
- `matplotlib==3.4.3`
- `plotly==5.3.1`

