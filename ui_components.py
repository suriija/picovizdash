from shiny import ui
from shinywidgets import output_widget, render_widget
from data_loading import all_categories
def create_ui(all_names, all_genders):
    return ui.page_fluid(
        ui.tags.head(
            ui.tags.link(rel="stylesheet", href="https://cdn.materialdesignicons.com/5.4.55/css/materialdesignicons.min.css")
        ),
        ui.tags.style("""
            .bubble {
                display: inline-block;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 15px;
                background-color: #e0e0e0;
                font-size: 12px;
            }
            .bubble.selected {
                background-color: #007bff;
                color: white;
            }
            .bubble a {
                color: inherit;
                text-decoration: none;
            }
            .bubble a:hover {
                text-decoration: none;
            }
            .icon-container {
                display: inline-block;
                text-align: center;
                margin: 5px;
            }
            .icon {
                font-size: 50px; /* Größe der Icons */
                display: block;
            }
            .icon-subtitle {
                font-size: 15px; /* Größe der Untertitel */
                color: #555; /* Farbe der Untertitel */
                text-align: center;
            }
        """),
        ui.h2("PICO Dashboard"),
        ui.layout_sidebar(
            ui.panel_sidebar(
                # Card for category filtering
                ui.card(
                    ui.card_header("Kategorie"),
                    ui.input_select("category_filter", "Filter nach Kategorie:", choices=all_categories, selected=['Alle']),
                ),
                # Card for Diga name filter 
                #ui.card(
                #   ui.card_header("Diga Name"),
                #   ui.input_select("sort_by", "Sortiere nach:", choices=all_names),
                #),
                # Card for gender filtering
                ui.card(
                    ui.card_header("Geschlecht"),
                    ui.input_select("gender_filter", "Filter nach Geschlecht:", choices=['Alle'] + all_genders),
                ),
                # Card for Diga names and the dynamic search bar with bumble 
                ui.card(
                    ui.card_header("Diga Name"),
                    ui.output_ui("dynamic_search_app_name"),
                    ui.output_ui("data_list"),
                    height="500px"
                )
            ),
            ui.panel_main(
                # Main area 
                # Text with DiGA Name, DiGA ID, Type
                ui.layout_columns(
                    ui.output_ui("selected_data_text"), 
                       
                ), # description, and ICD-10 
                    ui.accordion(  
                        ui.accordion_panel("Beschreibung", ui.output_ui("selected_data_des")),  
                    ui.accordion_panel("weiter Information", ui.output_ui("selected_item_list")),   
                    open="Beschreibung"
                ), 
               
                ui.layout_columns(
                    # Card Population 
                    ui.card(
                        ui.card_header("Patientengruppe"),
                       
                            ui.column(3,    ui.h4("Alter"),
                        ui.output_text("alter"),),
                              ui.column(    6,     ui.h4("Geschlecht"),
                        ui.output_ui("geschlecht"),),              
                        ui.h4("Diagnosen"),
                        ui.output_ui("diagnosen_bubbles"),
                        height="200px"
                    ),
                     # Card for intervention, comparison and pie plot
                ui.card(
                        ui.card_header("Intervention und Comparison"),
                        ui.layout_columns(
                            ui.column(
                                6,
                                ui.h4("Intervention"),
                                ui.output_ui("zugang_intervention"),
                            ),
                            ui.column(
                                6,
                                ui.h4("Comparison"),
                                ui.output_ui("zugang_comparison"),
                            ),
                        ),
                        output_widget("pie_chart_combined"),
                        width=12
                    )
                ),
                # Card for outcome display (Forest Plot)
                 ui.card(
                    ui.card_header("Outcome"),
                    ui.output_ui("tabs_output"),
                    width="300px"
                ),
            )
        )
    )
