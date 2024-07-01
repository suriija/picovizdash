import pandas as pd
import sqlite3

# Load Excel data
file_path = 'Transformed.xlsx'
df_excel = pd.read_excel(file_path)

# Function to load data from SQLite database
def load_data():
    conn = sqlite3.connect('newdigaDB.db')
    diga_df = pd.read_sql_query("SELECT * FROM diga", conn)
    patiente_df = pd.read_sql_query("SELECT * FROM patiente", conn)
    score_df = pd.read_sql_query("SELECT * FROM score", conn)
    conn.close()
    return diga_df, patiente_df, score_df

# Load data
diga_df, patiente_df, score_df = load_data()

# Function to extract names
def extract_names(name_list):
    names = []
    for name in name_list:
        if name:
            names.append(name)
    return names


# Ensure necessary columns exist
for column in ['patientengruppe_name', 'patientengruppe', 'app_name', 'geeignete_altersgruppen', 'geeignete_geschlechter']:
    if column not in diga_df.columns:
        raise KeyError(f"Die Spalte '{column}' existiert nicht in den Daten.")

# Split columns into lists
def split_columns_into_lists():
    columns = ['patientengruppe_name', 'patientengruppe', 'geeignete_altersgruppen', 'geeignete_geschlechter']
    for col in columns:
        diga_df[col] = diga_df[col].apply(lambda x: x.split(';') if isinstance(x, str) else [])

split_columns_into_lists()

# Create column patientengruppe_full based on names
diga_df['patientengruppe_full'] = diga_df['patientengruppe_name'].apply(lambda x: extract_names(x))

# Create a list of unique names for selection
all_names = pd.Series([name for sublist in diga_df['patientengruppe_full'] for name in sublist]).unique()

# Add "All" option
all_names = ['Alle'] + list(all_names)

# Create a list of unique app names for selection
all_app_names = list(diga_df['app_name'].unique())

# Create a list of unique genders for selection
all_genders = ['Männlich', 'Weiblich', 'Nichtbinäre Geschlechtsidentität']

# Convert name lists to strings for display with semicolon
diga_df['patientengruppe_full'] = diga_df['patientengruppe_full'].apply(lambda x: '; '.join(x))

# Create a list of unique categories for selection
all_categories = ['Alle'] + list(diga_df['kategorie'].explode().unique())

