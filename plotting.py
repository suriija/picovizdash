import matplotlib.pyplot as plt
import numpy as np
from data_loading import df_excel, pd, patiente_df
import plotly.graph_objects as go

# Function to parse an interval from a string
def parse_interval(interval_str):
    try:
        parts = interval_str.replace('–', ' - ').split(' - ')
        # Converts the parts to float values and returns them as a tuple
        return tuple(map(lambda x: float(x.replace(',', '.').strip()), parts))
    except Exception as e:
        print(f"Error parsing interval: {e}")
        return None, None

# Function to get a value from a DataFrame row
def get_value(row, column_name):
    value = row[column_name]
     # Converts the value to a float if it's not None
    return float(value.replace(',', '.')) if pd.notna(value) else None

# Function to get the confidence interval from a DataFrame row
def get_ci(row, pattern_prefix):
    # Defines possible column names for the confidence interval
    ci_column_names = [f'{pattern_prefix}_95-%-KI', f'{pattern_prefix}_95-%-Konfidenzintervall']
    for column in ci_column_names:
        if pd.notna(row[column]):
             # Parses the interval from the column value
            return parse_interval(row[column])
    return None, None

# Function to get statistical metrics from a DataFrame row
def get_statistics(row, pattern_prefix):
    columns = ['p-Wert', 'Cohens d', 'partielles eta2', 'Hedges g']
    result = {}
    for col in columns:
        try:
            column_name = f'{pattern_prefix}_{col}'
            result[col] = row[column_name] if column_name in row and pd.notna(row[column_name]) else None
        except Exception as e:
            print(f"Error parsing interval: {e}")
    return result

# Function to plot data based on a DiGA ID and a pattern prefix (forest plot)
def plot_data(diga_id, pattern_prefix):
    row = df_excel[df_excel['diga_id'] == int(diga_id)].iloc[0]
    title = row[f'{pattern_prefix}_Title']
    description = str(row[f'{pattern_prefix}_Beschreibung'])
    key = row['keys'].split('; ')[int(pattern_prefix.split('_')[-1]) - 1] 

    mean_diff = None
     # Checks if the description contains an interval
    if isinstance(description, str) and (' - ' in description or ' – ' in description):
        mean_diff_lower, mean_diff_upper = parse_interval(description)
        if mean_diff_lower is not None and mean_diff_upper is not None:
            mean_diff = (mean_diff_lower + mean_diff_upper) / 2
    else:
        mean_diff = float(description.replace(',', '.')) if pd.notna(description) else None

    ci_lower, ci_upper = get_ci(row, pattern_prefix)
    if ci_lower is not None and ci_upper is not None:
        mean_diff = (ci_lower + ci_upper) / 2

    stats = get_statistics(row, pattern_prefix)

    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(1)

    # Plots the mean difference and the confidence interval
    if mean_diff is not None and ci_lower is not None and ci_upper is not None:
        ax.errorbar(mean_diff, y_pos, xerr=[[mean_diff - ci_lower], [ci_upper - mean_diff]], fmt='o', ecolor='black', capsize=10, label='Mittelwertdifferenz')

    # Adds annotations for statistical metrics
    annotations = [f'{k}: {v}' for k, v in stats.items() if v is not None]
    for i, annotation in enumerate(annotations):
        ax.annotate(annotation, (mean_diff, y_pos[0]), textcoords="offset points", xytext=(10, 10*(i+1)), ha='center')

    plt.axvline(x=0, color='gray', linestyle='--')
    ax.set_xlabel('Bewertungsskala Einheit (siehe Information)', labelpad=10, loc='right')
    ax.set_ylabel('Bewertungsskalen', labelpad=10, loc='top')
    ax.set_yticks(y_pos)

    plt.title(title)
    plt.legend(bbox_to_anchor=(1, 1))
    plt.grid(True)
    return fig


# Function to create a summary forest plot based on a DiGA ID
def plot_summary(diga_id):
    row = df_excel[df_excel['diga_id'] == int(diga_id)].iloc[0]
    keys = row['keys'].split(';') if pd.notna(row['keys']) else []

    summaries = []
    for idx, key in enumerate(keys):
        pattern_prefix = f'pattern_{idx + 1}'
        description = str(row[f'{pattern_prefix}_Beschreibung'])
        mean_diff = None
        # Checks if the description contains an interval
        if isinstance(description, str) and (' - ' in description or ' – ' in description):
            mean_diff_lower, mean_diff_upper = parse_interval(description)
            if mean_diff_lower is not None and mean_diff_upper is not None:
                mean_diff = (mean_diff_lower + mean_diff_upper) / 2
        else:
            mean_diff = float(description.replace(',', '.')) if pd.notna(description) else None

        ci_lower, ci_upper = get_ci(row, pattern_prefix)
        if ci_lower is not None and ci_upper is not None:
            mean_diff = (ci_lower + ci_upper) / 2
        summaries.append((key, mean_diff, ci_lower, ci_upper))

    fig = go.Figure()
    # Adds the data to the plot
    for i, (key, mean_diff, ci_lower, ci_upper) in enumerate(summaries):
        if mean_diff is not None and ci_lower is not None and ci_upper is not None:
            fig.add_trace(go.Scatter(
                x=[mean_diff],
                y=[i],
                error_x=dict(type='data', symmetric=False, array=[ci_upper - mean_diff], arrayminus=[mean_diff - ci_lower]),
                mode='markers',
                name=key
            ))

    fig.update_layout(
        yaxis=dict(
            tickvals=list(range(len(summaries))),
            ticktext=[key for key, mean_diff, ci_lower, ci_upper in summaries],
            title="Bewertungsskalen"
        ),
        xaxis=dict(
            title="Bewertungsskala Einheit (siehe Information)"
        ),
        title="Zusammenfassungs-Forest-Plot",
        shapes=[dict(type='line', x0=0, x1=0, y0=-1, y1=len(summaries), line=dict(dash='dash'))]
    )

    return fig

# Function to create a pie chart based on a DiGA ID
def create_pie_chart(diga_id, labels=None, colors=None, show_labels=True):
    filtered_df = patiente_df[patiente_df['diga_id'] == diga_id]
    if filtered_df.empty:
        empty_plot()

    ig_values, ik_values = filtered_df['ig'].tolist(), filtered_df['ik'].tolist()

    sizes = []
    # Determines the sizes of the pie segments
    for ig, ik in zip(ig_values, ik_values):
        if ig != 0:
            sizes.extend([ik,ig])
        elif ik != 0:
            sizes.extend([ik / 2]*2)

    explode = [0, 0.1]
    # Creates the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=sizes,
        marker=dict(colors=colors),
        textinfo='label+value' if show_labels else 'value',
        #insidetextorientation='radial',
        pull=explode,
        hoverinfo='label+value',
        sort=False
    )])

    fig.update_layout(
        title_text="Patienanzahl",
        showlegend=show_labels
    )

    return fig
    
# Function to create an empty plot
def empty_plot():
        fig = go.Figure()
        fig.add_annotation(
            text="Keine Daten verfügbar",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20),
            align="center"
        )
        fig.update_layout(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
