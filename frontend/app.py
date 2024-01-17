import shinyswatch
from shiny import App, render, ui, reactive
import requests
import pandas as pd
import matplotlib.pyplot as plt

app_ui = ui.page_navbar(

    shinyswatch.theme.superhero(),
    ui.nav(
        "EURIBOR Daten",
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.input_text("start_date", "Startdatum", placeholder="YYYY-MM"),
                ui.input_text("end_date", "Enddatum", placeholder="YYYY-MM"),
                ui.input_action_button("make_plot", "Make plot!"),
            ),
            ui.panel_main(
                ui.navset_tab(
                    ui.nav(
                        "Euribor Monatswerte",
                        ui.tags.h4("Euribor vs Time"),
                        ui.output_plot("plot_euribor"),
                    ),
                    ui.nav(
                        "Euribor Monatswerte Differenz",
                        ui.tags.h4("Euribor Diff vs Time"),
                        ui.output_plot("plot_euribor_diff"),
                    ),
                    ui.nav(
                        "Euribor Tabelle",
                        ui.tags.h4("Euribor Diff vs Time"),
                        ui.output_data_frame("grid"),
                        ui.panel_fixed(
                        ui.output_text_verbatim("detail"),
                        right="10px",
                        bottom="10px",
                        ),
                    ),
                )
            ),
        ),
    ),
    ui.nav("Test"),
    title="Loan Pricing",
)


def server(input, output, session):
    @output
    @render.data_frame
    async def grid():
        url = "http://localhost:8000/get-entries-all"

        try:
            response = requests.get(url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Print the response content
                
                df = pd.json_normalize(response.json())  # Assuming the response is in JSON format
            else:
                print(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        height = 350
        width = "100%"
        return render.DataGrid(
                df,
                row_selection_mode="single",
                height=height,
                width=width,
                filters=True,
            )

        
    @output
    @render.plot(alt="Euribor Diff vs Time")
    @reactive.event(input.make_plot)
    async def plot_euribor_diff():
        start_date = input.start_date()
        end_date = input.end_date()
        url = f"http://localhost:8000/get-entries/{str(start_date)}/{str(end_date)}"

        try:
            response = requests.get(url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Print the response content
                
                df = pd.json_normalize(response.json())  # Assuming the response is in JSON format
            else:
                print(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        # Create subplots
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plotting
        ax.plot(df['TimePeriod'], df['BbkDiff'], marker='o', linestyle='-', color='b')

        # Customize the plot
        ax.set_title('BbkDiff versus Time')
        ax.set_xlabel('TimePeriod')
        ax.set_ylabel('BbkDiff')
        ax.grid(True)

        # Set custom x-axis ticks every 12 units
        custom_ticks = df['TimePeriod'][::12]
        ax.set_xticks(custom_ticks)

        return fig
    
    @output
    @render.plot(alt="Euribor vs Time")
    @reactive.event(input.make_plot)
    async def plot_euribor():
        start_date = input.start_date()
        end_date = input.end_date()
        url = f"http://localhost:8000/get-entries/{str(start_date)}/{str(end_date)}"

        try:
            response = requests.get(url)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Print the response content
                
                df = pd.json_normalize(response.json())  # Assuming the response is in JSON format
            else:
                print(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        # Create subplots
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plotting
        ax.plot(df['TimePeriod'], df['ObsVal'], marker='o', linestyle='-', color='b')

        # Customize the plot
        ax.set_title('ObsVal versus Time')
        ax.set_xlabel('TimePeriod')
        ax.set_ylabel('ObsVal')
        ax.grid(True)

        # Set custom x-axis ticks every 12 units
        custom_ticks = df['TimePeriod'][::12]
        ax.set_xticks(custom_ticks)

        return fig


app = App(app_ui, server)
