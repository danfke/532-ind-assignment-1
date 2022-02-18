import pandas as pd
import altair as alt
from dash import Dash, html, dcc, Input, Output

# Data wrangling
colony = pd.read_csv(
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-01-11/colony.csv",
)

colony["start_month"] = colony["months"].str.split('-', 1, expand=True)[0]
colony["year"] = colony["year"].astype("str")
colony["time"] = colony[['year', 'start_month']].agg('-'.join, axis=1)
colony["time"] = pd.to_datetime(colony["time"])
colony = colony.drop(["year", "months", "start_month"], axis=1)
colony["period"] = pd.PeriodIndex(pd.to_datetime(colony["time"]), freq='Q').astype("str")

# Dash app
app = Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Iframe(
            id='ncolony_chart',
            style={"border-width": "0", "width": "100%", "height": "400px"}
        ),
        dcc.Dropdown(
            id='state-widget',
            value="Alabama",
            options=[
                {'label': state, 'value': state} for state in colony['state'].unique()
            ],
            # multi=True,
            placeholder="Select a state..."
        )
    ]
)

@app.callback(
    Output("ncolony_chart", "srcDoc"),
    Input("state-widget", "value"))
def plot_altair(state_arg):
    colony_chart = (
        alt.Chart(colony[colony["state"].isin([state_arg])])
        .mark_line()
        .encode(
            x=alt.X("time", title="Time period"),
            y=alt.Y("colony_n", title="Number of colonies", axis=alt.Axis(format="s")),
            color=alt.Color("state", title="State"),
        )
        .configure_axis(titleFontSize=20, labelFontSize=14, grid=False)
        .configure_legend(titleFontSize=20, labelFontSize=14)
        .properties(width=500)
    )
    return colony_chart.to_html()


if __name__ == '__main__':
    app.run_server(
        port = 8070,
        debug=True)