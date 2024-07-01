import inspect

# Function to convert age group to an interval (tuple) of years
def convert_age_group_to_interval(age_group):
    mapping = {
        'Jugendliche(r) (12-17 Jahre)': (12, 17),
        'Erwachsene(r) (18-65 Jahre)': (18, 65),
        'Erwachsene (älter als 65 Jahre)': (65, 90)
    }
    return mapping.get(age_group.strip(), (None, None))

# Function to combine multiple age intervals into a single interval
def combine_intervals(intervals):
    if not intervals:
        return "Keine Altersgruppen verfügbar"

    min_age = min(interval[0] for interval in intervals if interval[0] is not None)
    max_age = max(interval[1] for interval in intervals if interval[1] is not None)
    
    return f"{min_age}-{max_age} Jahre"

# Function to get filtered app names based on input filters
def get_filtered_app_names(input, diga_df):
    filtered_df = filter_data(input, diga_df)
    return list(filtered_df['app_name'].unique())

# Function to filter data based on user input and predefined criteria
def filter_data(input, diga_df):
    stack = inspect.stack()  # Gets the stack frame from which the function was called
    #selected_name = input.sort_by() or 'Alle'
    selected_gender = input.gender_filter() or 'Alle'
    selected_categories = input.category_filter() or 'Alle'
    if stack[1].function != "get_filtered_app_names":
        selected_apps = input.search_app_name() or []

    # Filter the dataframe to include only those with data_full equal to 1
    filtered_df = diga_df[diga_df["data_full"] == 1]

    #if selected_name != 'Alle':
    #   filtered_df = filtered_df[filtered_df['patientengruppe_full'].apply(lambda x: selected_name.strip() in x.split('; '))]

    # Filter by selected gender if not 'Alle' (all)
    if selected_gender != 'Alle':
        filtered_df = filtered_df[filtered_df['geeignete_geschlechter'].apply(lambda x: selected_gender.strip() in x)]
    
    # Filter by selected categories if not 'Alle' (all)
    if selected_categories != 'Alle':
        filtered_df = filtered_df[filtered_df['kategorie'].apply(lambda x: selected_categories.strip() in x)]
    
    # Filter by selected app names if the function is not called from get_filtered_app_names
    if stack[1].function != "get_filtered_app_names":
        if selected_apps:
            filtered_df = filtered_df[filtered_df['app_name'].isin(selected_apps)]

    return filtered_df