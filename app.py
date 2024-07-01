from shiny import App, ui, render, reactive
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from filtering import filter_data, get_filtered_app_names, convert_age_group_to_interval, combine_intervals
from data_loading import diga_df, patiente_df, score_df, all_names, all_app_names, all_genders, df_excel, all_categories
from plotting import plot_data, plot_summary, create_pie_chart, plt, empty_plot, go
from ui_components import create_ui
import inspect

from shinywidgets import output_widget, render_widget  

# Define Shiny UI and server function
app_ui = create_ui(all_names, all_genders)

def server(input, output, session):
    selected_diga_id = reactive.Value(None) # Reactive variable to store the selected DiGA ID

    @reactive.Calc
    def filtered_app_names():
        return get_filtered_app_names(input, diga_df) # Calculates the filtered app names based on user input

    @output
    @render.ui
    def dynamic_search_app_name():
        return ui.input_selectize("search_app_name", "Suche App Name:", choices=filtered_app_names(), multiple=True)   # Dynamic search bar for app names

    @reactive.Effect
    def update_selected_diga_id():
        clicked_item = input.clicked_item()
        if clicked_item:
            selected_diga_id.set(clicked_item)  # Updates the selected DiGA ID based on user clicks

    @reactive.Effect
    def update_sort_by():
        clicked_item = input.clicked_item()
        if clicked_item:
            row = diga_df[diga_df['diga_id'] == clicked_item].iloc[0]
            patientengruppe_full = row['patientengruppe_full'].split(';')
            if patientengruppe_full:
                session.send_input_message("sort_by", {"selected": patientengruppe_full[0].strip()})  # Updates sorting based on the patient group

    @output
    @render.ui
    def selected_item_list():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = diga_df[diga_df['diga_id'] == diga_id].iloc[0]
            patientengruppen = row['patientengruppe_full'].split(';')
            bubbles = [ui.span(group, class_="bubble selected") for group in patientengruppen]
            return ui.div(*bubbles)  # Creates a list of selected items
        return ui.HTML("Keine Daten verfügbar")

    @output
    @render.ui
    def selected_data_text():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = diga_df[diga_df['diga_id'] == diga_id].iloc[0]
            return ui.HTML(f"""
                <h1>{row['app_name']}</h1>
                <a><strong>Diga ID:</strong> {row['diga_id']}</a>
                <a>({row['app_type']})</a>
            """)  # Displays the name and ID of the selected DiGA
        return ui.HTML("Keine Daten verfügbar")

    @output
    @render.ui
    def selected_data_des():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = diga_df[diga_df['diga_id'] == diga_id].iloc[0]
            return ui.HTML(f"""
              <a>{row['diga_description']}</a>
            """)   # Displays the description of the selected DiGA
        return ui.HTML("Keine Daten verfügbar")

    @output
    @render.ui
    def data_list():
        filtered_df = filter_data(input, diga_df)
        # Erzeugen der klickbaren Liste
        links = []
        for _, row in filtered_df.iterrows():
            link_text = f"{row['app_name']}"
            class_name = "bubble selected" if row['diga_id'] == selected_diga_id.get() else "bubble"
            link = f'<a href="#" class="{class_name}" onclick=\'Shiny.setInputValue("clicked_item", "{row["diga_id"]}", {{priority: "event"}})\'>{link_text}</a>'
            links.append(link)
        return ui.HTML(''.join(links))  # Creates an HTML list of filtered apps

    """
    @output
    @render.text
    def selected_count():
        filtered_df = filter_data(input, diga_df)
        count = len(filtered_df)
        return f"Anzahl der ausgewählten Elemente: {count}"  # Displays the count of filtered apps
    """

    @output
    @render.text
    def alter():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = diga_df[diga_df['diga_id'] == diga_id].iloc[0]
            altersgruppen = row['geeignete_altersgruppen']
            if altersgruppen:
                intervals = [convert_age_group_to_interval(group) for group in altersgruppen]
                combined_interval = combine_intervals(intervals)
                return combined_interval  # Displays the age group of the selected DiGA
        return "Keine Altersgruppen verfügbar"
    
    @render_widget
    def pie_chart_combined():
        diga_id = selected_diga_id.get()
        if diga_id:
            labels = ['Kontrollgruppe (KG)', 'Interventionsgruppe (IG)'] 
            colors = ['#e0e0e0', '#007bff']
            return create_pie_chart(diga_id, labels=labels, colors=colors, show_labels=True)  # Creates a pie chart for the selected DiGA
        #return empty_plot()

    @output
    @render.ui
    def zugang_intervention():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = diga_df[diga_df['diga_id'] == diga_id].iloc[0]
            return ui.HTML(f'<ul><li>{row["app_name"]}</li><li>Standardversorgung</li></ul>')  # Displays access to the intervention
        return ui.HTML("Keine Daten verfügbar")

    @output
    @render.ui
    def zugang_comparison():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = diga_df[diga_df['diga_id'] == diga_id].iloc[0]
            return ui.HTML(f'<ul><li>Standardversorgung</li></ul>')  # Displays access to the comparison group
        return ui.HTML("Keine Daten verfügbar")

    @output
    @render.ui
    def geschlecht():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = diga_df[diga_df['diga_id'] == diga_id].iloc[0]
            geschlechter = row['geeignete_geschlechter']
            if geschlechter:
                icons = {
                    'Männlich': ('<span class="mdi mdi-gender-male icon"></span>', 'Männlich'),
                    'Weiblich': ('<span class="mdi mdi-gender-female icon"></span>', 'Weiblich'),
                    'Nichtbinäre Geschlechtsidentität': ('<span class="mdi mdi-gender-non-binary icon"></span>', 'Geschlechtsidentität')
                } # Quelle vom Icon : https://pictogrammers.com/
                gender_list = geschlechter if isinstance(geschlechter, list) else geschlechter.split(';')
                rendered_icons = ''.join(f'<div class="icon-container">{icons.get(gender.strip(), (gender, gender))[0]}<div class="icon-subtitle">{icons.get(gender.strip(), (gender, gender))[1]}</div></div>' for gender in gender_list)
                return ui.HTML(rendered_icons)   # Displays the suitable genders for the selected DiGA
        return ui.HTML("Keine Geschlechter verfügbar")
       
    @output
    @render.ui
    def diagnosen_bubbles():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = diga_df[diga_df['diga_id'] == diga_id].iloc[0]
            patientengruppe = row['patientengruppe']
            if patientengruppe:
                bubbles = [ui.span(group, class_="bubble") for group in patientengruppe]
                return ui.div(*bubbles)  # Displays the diagnoses for the selected DiGA
        return ui.HTML("Keine Diagnosen verfügbar")

    def get_description(index):
        diga_id = selected_diga_id.get()
        if diga_id:
            row = df_excel[df_excel['diga_id'] == int(diga_id)].iloc[0]
            keys = row['keys'].split('; ') if pd.notna(row['keys']) else []
            if keys and len(keys) > index:
                key = keys[index]
                description = score_df[score_df['abk'] == key]['short_des'].values[0] if not score_df[score_df['abk'] == key].empty else "Keine Beschreibung verfügbar"
                long_description = score_df[score_df['abk'] == key]['short_long'].values[0] if not score_df[score_df['abk'] == key].empty else "Keine ausführliche Beschreibung verfügbar"
                return description, long_description # Fetches the description based on the index
        return "Keine Beschreibung verfügbar", "Keine ausführliche Beschreibung verfügbar"

    @output
    @render.ui
    def tabs_output():
        diga_id = selected_diga_id.get()
        if diga_id:
            row = df_excel[df_excel['diga_id'] == int(diga_id)].iloc[0]
            keys = row['keys'].split('; ') if pd.notna(row['keys']) else []
            if keys:
                tabs = [
                    ui.nav_panel(
                        key,
                        ui.row(ui.output_text(f'description_{i+1}'), ui.input_action_button(f'show_long_des_{i+1}', "Mehr anzeigen")),
                        ui.output_plot(f'diagram_outputt_{i+1}')
                    )
                    for i, key in enumerate(keys)
                ]
                tabs.append(ui.nav_panel('Zusammenfassung', output_widget('summary_plot')))
                return ui.navset_card_tab(*tabs)   # Creates tabs based on the keys
        return ui.HTML('<div>Keine Daten verfügbar</div>')

    @output
    @render.text
    def description_1():
        return get_description(0)[0]  # Fetches the description

    @output
    @render.text
    def description_2():
        return get_description(1)[0]   

    @output
    @render.text
    def description_3():
        return get_description(2)[0]  

    @reactive.Effect
    @reactive.event(input.show_long_des_1)
    def show_long_des_1():
        long_des = get_description(0)[1]
        ui.notification_show(long_des, type="info", duration=10) # Shows a notification with the detailed description for the first key

    @reactive.Effect
    @reactive.event(input.show_long_des_2)
    def show_long_des_2():
        long_des = get_description(1)[1]
        ui.notification_show(long_des, type="info", duration=10) 

    @reactive.Effect
    @reactive.event(input.show_long_des_3)
    def show_long_des_3():
        long_des = get_description(2)[1]
        ui.notification_show(long_des, type="info", duration=10)  

    def generate_plot(pattern):
        diga_id = selected_diga_id.get()
        if diga_id:
            return plot_data(diga_id, pattern)  # Generates a plot based on the pattern
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Keine Daten verfügbar', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off')
        return fig  # Returns an empty plot if no data is selected or available

    @output
    @render.plot
    def diagram_outputt_1():
        return generate_plot('pattern_1')  # Generates the plot

    @output
    @render.plot
    def diagram_outputt_2():
        return generate_plot('pattern_2') 

    @output
    @render.plot
    def diagram_outputt_3():
        return generate_plot('pattern_3')  

    @render_widget  
    def summary_plot():
        diga_id = selected_diga_id.get()
        if diga_id:
            return plot_summary(diga_id)  # Generates the summary forest plot
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, 'Keine Daten verfügbar', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off')
        return fig # Returns an empty plot if no data is selected or available

# Start Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()  # Starts the Shiny app
