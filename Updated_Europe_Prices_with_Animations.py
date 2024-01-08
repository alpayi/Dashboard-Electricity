
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import json

# Load the GeoJSON file
with open('assets/europe.geojson', 'r') as file:
    europe_geojson = json.load(file)

country_names = [
    'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Czechia', 'Denmark', 'Estonia',
    'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Italy',
    'Latvia', 'Lithuania', 'Luxembourg', 'Netherlands', 'North Macedonia', 'Norway',
    'Poland', 'Portugal', 'Romania', 'Serbia', 'Slovakia', 'Slovenia', 'Spain',
    'Sweden', 'Switzerland'
]

    

# Load data for all countries and store in a dictionary
country_data = {country: pd.read_csv(f'data/{country}.csv') for country in country_names}

# Pre-process the data
for data in country_data.values():
    data['Datetime (Local)'] = pd.to_datetime(data['Datetime (Local)'])
    data['Year'] = data['Datetime (Local)'].dt.year
    data['Month'] = data['Datetime (Local)'].dt.month

app = Dash(__name__)


dcc.Interval(id='interval-component',
            interval=1000,  # Animation speed in milliseconds
            n_intervals=0
        ),
app.layout = html.Div(
    [
        html.Div([
            html.Div(html.Img(src='assets/QC.png', style={'height': '60px'}), style={'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div(html.H1("Electricity Prices in Europe", style={'textAlign': 'center'}), style={'display': 'inline-block', 'margin': '10px'}),
            html.Div([
                html.Label("Select a Year:", style={'marginRight': '10px'}),
                dcc.Slider(
                    id='year-slider',
                    min=2015,
                    max=2023,
                    value=2015,
                    marks={year: str(year) for year in range(2015, 2024)},
                    step=None
                )
            ], style={'width': '100%', 'marginBottom': '10px'}),
            html.Div([
                html.Label("Select Countries:", style={'marginRight': '10px'}),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in country_names],
                    value=country_names,  # Default selected value
                    multi=True  # Allow multiple selections
                )
            ], style={'width': '100%', 'marginBottom': '20px'}),
            dcc.Graph(id="graph")
        ], style={'padding': '20px'})
    ]
)

@app.callback(
    Output("graph", "figure"), 
    [Input("country-dropdown", "value"), Input("year-slider", "value")]
)
def update_graph(selected_countries, selected_year):
    # Prepare the data for the selected year and countries
    df_list = []
    for country in selected_countries:
        data = country_data[country]
        data = data[data['Year'] == selected_year]
        avg_price = data['Price (EUR/MWhe)'].mean()
        df_list.append({'Country': country, 'Average Price': avg_price})
    df = pd.DataFrame(df_list)

    # Create the choropleth map
    fig = px.choropleth(
        df,
        geojson=europe_geojson,
        locations='Country',  # This field should match the "NAME" property in the GeoJSON features
        featureidkey='properties.NAME',  # This is where you tell plotly to match the GeoJSON properties
        color='Average Price',
        color_continuous_scale='Viridis',  # You can choose any color scale
        title=f'Average Electricity Prices in Europe for {selected_year}'
    )
    
    fig.update_geos(fitbounds="locations", visible=False)  # Fit the map to the geojson boundary locations
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
