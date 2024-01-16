import pandas as pd
import matplotlib.pyplot as plt
import requests
from shiny import App, render, ui, reactive
from datetime import date
import asyncio

app_ui = ui.page_fluid(
    ui.input_text("start_date", "Start Date", placeholder="YYYY-MM"),
    ui.input_text("end_date", "End Date", placeholder="YYYY-MM"),
    ui.input_action_button("make_plot", "Make plot!"),
    ui.output_plot("plot"),
)


def server(input, output, session):
    @output
    @render.plot(alt="Euribor vs Time")
    @reactive.event(input.make_plot)
    async def plot():
        start_date = input.start_date()
        end_date = input.end_date()
        # print(str(start_date), type(str(end_date)))
        url = f"http://localhost:8000/get-entries/{str(start_date)}/{str(end_date)}"
        print(url)
        # url = "http://localhost:8000/get-entries/2023-01/2023-12"

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
