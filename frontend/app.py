import shinyswatch
from shiny import App, render, ui, reactive
import requests
import pandas as pd
import matplotlib.pyplot as plt
from frontend.schedule import Schedule

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
                        ui.output_data_frame("euribor"),
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
    ui.nav("Schedule",
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.input_date("effectiveDate", "Effective Date Input"), 
                ui.input_select("tenor", "Select Tenor", {
                    "1Y": "1 Year", "2Y": "2 Years",
                    "3Y": "3 Years", "4Y": "4 Years", 
                    "5Y": "5 Years", "6Y": "6 Years", 
                    "7Y": "7 Years", "8Y": "8 Years", 
                    "9Y": "9 Years", "10Y": "10 Years"}
                ),
                ui.input_select("frequency", "Select Frequency", {
                    "1M": "1 Month", "2M": "2 Months",
                    "3M": "3 Months", "4M": "4 Months",
                    "1Y": "1 Year", "2Y": "2 Years",
                    "3Y": "3 Years", "4Y": "4 Years", 
                    "5Y": "5 Years", "6Y": "6 Years", 
                    "7Y": "7 Years", "8Y": "8 Years", 
                    "9Y": "9 Years", "10Y": "10 Years"}
                ),
                ui.input_select("calendar", "Select Calendar", {
                    "GER": "Germany", "USA": "USA",
                    "UK": "United Kingdom", "AUS": "Australia",
                    "BRA": "Brazil", "CAN": "Canada",
                    "SK": "South Korea", "FRA": "France"}
                ),
                ui.input_select("holidayConvention", "Select Holiday Convention", {
                    "cP": "Preceding", "cF": "Following",
                    "cMF": "Modified Following", "cMP": "Modified Preceding",
                    "cU": "Unadjusted", "cN": "Null Calendar"}
                ),
                ui.input_select("terminationDateConvention", "Termination Date Convention", {
                    "tP": "Preceding", "tF": "Following",
                    "tMF": "Modified Following", "tMP": "Modified Preceding",
                    "tU": "Unadjusted", "tN": "Null Calendar"}
                ),
                ui.input_select("dateGenerationRule", "Date Generation Rule", {
                    "dForward": "Forward",
                    "dBackward": "Backward",
                    "dZero": "Zero",
                    "dThirdWednesday": "Third Wednesday",
                    "dTwentieth": "Twentieth",
                    "dTwentiethIMM": "Twentieth IMM",
                    "dOldCDS": "Old CDS",
                    "dCDS": "CDS"}
                ),
                ui.input_select("dayCountConvention", "Day Count Convention", {
                    "dcActual360": "Actual 360",
                    "dcActual365Fixed": "Actual 365 (Fixed)",
                    "dcActualActualISDA": "Actual Actual (ISDA)",
                    "dcActualActualAFB": "Actual Actual (AFB)",
                    "dcActualActualISMA": "Actual Actual (ISMA)",
                    "dcBusiness252": "Business 252"}
                ),
                ui.input_switch("endOfMonthRule", "End of Month Rule"),
                ui.input_action_button("make_schedule", "Make Schedule!"),
            ),
            ui.panel_main(
                ui.tags.h4("Schedule"),
                ui.output_data_frame("schedule"),
            ),
        ),
    ),
    ui.nav("Ratings",
        ui.layout_sidebar(
            ui.panel_sidebar(
                ui.input_text("companyName", "Search by Company Name", placeholder="Company Name"),
                ui.input_action_button("searchCompanyName", "Search Company"),
                ui.input_text("legalEntity", "Search by Legal Entity", placeholder="Legal Entity Number"),
                ui.input_action_button("searchCompanyEntity", "Search Company"),
                ui.input_select("companyNameSuggestion", "Company Name Suggestion", []),
                ui.input_action_button("showRating", "Show Rating", class_="btn-primary"),
            ),
            ui.panel_main(
                ui.tags.h4("Ratings"),
                ui.output_text("ratingOutput"),
            ),
        ),
        
    ),
    title="Loan Pricing",
)


def server(input, output, session):

    @reactive.Effect
    @reactive.event(input.legalEntity)
    def _():
        entity = input.legalEntity()
        url = f'http://localhost:8000/get-rating-by-entity-identifier/{entity}'

        try:
            response = requests.get(url)

            if response.status_code == 200:
                if response.json() == {"message": f"No entries found for entity identifier"}:
                    suggestions = ["No suggestions found"]
                else:
                    suggestions = pd.json_normalize(response.json())
                    suggestions = list(suggestions['Issuer'])
                ui.update_select(
                    "companyNameSuggestion",
                    label="Select Company",
                    choices=suggestions,
                )
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    @reactive.Effect
    @reactive.event(input.searchCompanyName)
    def _():
        companyName = input.companyName()
        url = f'http://localhost:8000/get-rating-by-issuer/{companyName}'

        try:
            response = requests.get(url)

            if response.status_code == 200:
                if response.json() == {"message": f"No entries found for issuer"}:
                    suggestions = ["No suggestions found"]
                else:
                    suggestions = pd.json_normalize(response.json())
                    suggestions = list(suggestions['Issuer'])

                

                ui.update_select(
                    "companyNameSuggestion",
                    label="Select Company",
                    choices=suggestions,
                )
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

    @output
    @render.text
    @reactive.event(input.showRating)
    def ratingOutput():
        companyName = input.companyNameSuggestion()
        rating = ""
        url = f'http://localhost:8000/get-rating-by-issuer/{companyName}'
        try:
            response = requests.get(url)

            if response.status_code == 200:
                if response.json() != {"message": f"No entries found for issuer"}:
                    suggestions = pd.json_normalize(response.json())
                    rating = suggestions['Rating'].iloc[0]

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        
        return f"{companyName}: {rating}"
    
    @output
    @render.data_frame
    @reactive.event(input.make_schedule)
    async def schedule():
        user_input = {
            "effectiveDate": str(input.effectiveDate()),
            "tenor": input.tenor(),
            "frequency": input.frequency(),
            "calendar": input.calendar(),
            "holidayConvention": input.holidayConvention(),
            "terminationDateConvention": input.terminationDateConvention(),
            "dateGenerationRule": input.dateGenerationRule(),
            "endOfMonthRule": input.endOfMonthRule(),
            "dayCountConvention": input.dayCountConvention(),
        }
        height = 350
        width = "100%"
        df = pd.DataFrame(Schedule.init_with_ql(user_input))
        df['StartDate'] = df['StartDate'].apply(lambda x: x.ISO())
        df['EndDate'] = df['EndDate'].apply(lambda x: x.ISO())
        df['MidDate'] = df['MidDate'].apply(lambda x: x.ISO())
        return render.DataGrid(
                df,
                row_selection_mode="single",
                height=height,
                width=width,
                filters=True,
            )
    
    @output
    @render.data_frame
    async def euribor():
        url = "http://localhost:8000/get-euribor-entries-all"

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
        url = f"http://localhost:8000/get-euribor-entries/{str(start_date)}/{str(end_date)}"

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
        url = f"http://localhost:8000/get-euribor-entries/{str(start_date)}/{str(end_date)}"

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
