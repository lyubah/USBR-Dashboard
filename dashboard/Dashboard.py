
from flask import Flask
from dash import Dash, dcc, html, dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State, ALL
from flask import Flask
from dash import Dash, dcc, html, dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from flask import Flask
from dash import Dash, dcc, html, dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import dash
from station_meta_data import get_stations_metadata
# from report_dataset_generator import generate_report_data

# Define the Flask server
server = Flask(__name__)

# Load the CSV file
owy_stations_data = pd.read_csv('../data/owy_stations_data.csv')

# Define the Dash app
app = Dash(__name__, server=server, routes_pathname_prefix='/')

# Define the list of basins
basins = [
    "Boise River Basin, ID",
    "Crab Creek Basin, WA",
    "Crooked River Basin, OR",
    "Deschutes River Basin, OR",
    "Flathead River Basin, MT",
    "Lewiston Orchards, ID",
    "Malheur River Basin, OR",
    "Owyhee River Basin, OR-NV",
    "Payette River Basin, ID",
    "Powder River Basin, OR",
    "Rogue River Basin, OR",
    "Snake River abv Idaho Falls, ID-WY",
    "Snake abv Milner, bel Idaho Falls, ID",
    "Tualatin River Basin, OR",
    "Umatilla River Basin, OR"
]

basin_stations = {
    "Owyhee River Basin, OR-NV": ['336:NV:SNTL', '1262:NV:SNTL', '548:NV:SNTL', '573:NV:SNTL', '654:ID:SNTL', '774:ID:SNTL', '811:NV:SNTL', '1136:NV:SNTL'],
    # Add other basins and their stations here later
}

stations_triplets = get_stations_metadata()

# Define the map bounds based on the provided coordinates
map_bounds = {
    "north": 49.0,
    "south": 31.0,
    "west": -125.0,
    "east": -96.0
}

# Calculate the center of the map
map_center = {
    "lat": (map_bounds["north"] + map_bounds["south"]) / 2,
    "lon": (map_bounds["west"] + map_bounds["east"]) / 2
}

# Create the map
fig = px.scatter_mapbox(
    owy_stations_data,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    zoom=4,
    height=600,
    center=map_center
)

# Update map layout
fig.update_layout(
    mapbox_style="open-street-map",
    mapbox=dict(
        center={"lat": 40.0, "lon": -110.0},
        zoom=4
    )
)

# Define the layout of the Dash app
app.layout = html.Div([  # Main container
    dcc.Store(id='visible-graphs', data=[]),  # Store to keep track of visible graphs
    html.H1(
        "USBR Operational Ranges Dashboard",
        style={
            'textAlign': 'center',
            'color': '#2c3e50',
            'marginBottom': '30px'
        }
    ),
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Home', children=[
            html.Div([
                html.H2(
                    "Operational Range Summary",
                    style={
                        'textAlign': 'center',
                        'color': '#2c3e50'
                    }
                ),
                html.Div([  # Container for widgets
                    html.Label("Select Basin:", style={'marginTop': '20px'}),
                    dcc.Dropdown(
                        id='basin-dropdown',
                        options=[{'label': basin, 'value': basin} for basin in basins],
                        value=basins[0],  # Default value
                        style={
                            'width': '80%',  # Width of the dropdown
                            'margin': '0 auto',  # Center the dropdown
                            'marginBottom': '10px'  # Space below the dropdown
                        }
                    ),
                    html.Label("Select Stations:", style={'marginTop': '20px'}),
                    dcc.Dropdown(
                        id='stations-dropdown',
                        options=[{'label': triplet, 'value': triplet} for triplet in stations_triplets],
                        value=[stations_triplets[0]],  # Default value
                        multi=True,
                        style={
                            'width': '80%',  # Width of the dropdown
                            'margin': '0 auto',  # Center the dropdown
                            'marginBottom': '10px'  # Space below the dropdown
                        }
                    ),
                    html.Div([  # Flexbox container for Select Date
                        html.Label("Select Date:", style={'marginRight': '10px', 'fontSize': '16px'}),
                        dcc.DatePickerSingle(
                            id='date-picker',
                            date=pd.to_datetime('today').date(),  # Default to today's date
                            style={
                                'width': '150px',  # Width of the date picker
                                'marginBottom': '10px',  # Space below the date picker
                                'fontSize': '16px'  # Font size for the date picker text
                            }
                        )
                    ], style={
                        'display': 'flex',  # Use flexbox layout
                        'justifyContent': 'center',  # Center align the items
                        'alignItems': 'center',  # Center align vertically
                        'padding': '10px 0'  # Padding inside the flexbox container
                    }),
                    html.Button(
                        'Submit',
                        id='submit-button',
                        n_clicks=0,
                        style={
                            'display': 'block',  # Make button a block element
                            'margin': '0 auto',  # Center the button
                            'backgroundColor': '#3498db',
                            'color': 'white',
                            'padding': '5px 10px',  # Padding inside the button
                            'fontSize': '14px'  # Font size for the button text
                        }
                    ),
                ], style={
                    'padding': '10px',  # Padding inside the container
                    'borderRadius': '10px',  # Rounded corners
                    'width': '80%',  # Adjust width for the container
                    'margin': 'auto',  # Center align the container
                    'backgroundColor': '#ffffff',  # White background for the container
                    'boxShadow': '0px 0px 15px rgba(0, 0, 0, 0.1)'  # Slight box shadow for the container
                }),
                html.Hr(style={'width': '100%', 'borderColor': '#ccc', 'margin': '40px 0'}),  # Styled divider
                html.Div(
                    [
                        html.Div(id='output-table', style={'width': '60%', 'float': 'left'}),
                        html.Div(id='visualization-widget', style={'width': '40%', 'float': 'right'}),
                    ],
                    style={'marginTop': '30px', 'display': 'flex', 'width': '100%'}
                )
            ], style={
                'display': 'flex',  # Use flexbox layout
                'flexDirection': 'column',  # Column direction
                'alignItems': 'center',  # Center align items
                'width': '90%',  # Width of the container
                'margin': 'auto'  # Center align the container
            })
        ]),
        dcc.Tab(label='SNOTEL and USGS Data', children=[
            html.Div([
                html.H2(
                    "SNOTEL Stations and USGS Streams",
                    style={
                        'textAlign': 'center',
                        'color': '#2c3e50'
                    }
                ),
                html.Div(id='graph-container', children=[
                    html.Button('Close Graph', id='close-graph-button', n_clicks=0),
                    dcc.Graph(figure=fig)  # Add the map here
                ], style={
                    'width': '90%',  # Width of the container
                    'margin': 'auto',  # Center align the container
                    # 'marginTop': '30px'  # Margin on top of the container
                })
            ])
        ]),
    ])
], style={
    'backgroundColor': '#f9f9f9',  # Background color of the main container
    'padding': '50px 0',  # Padding on top and bottom
    'minHeight': '100vh'  # Minimum height for the container
})

@app.callback(
    Output('stations-dropdown', 'options'),
    Input('basin-dropdown', 'value')
)
def update_stations_dropdown(selected_basin):
    if selected_basin in basin_stations:
        stations = basin_stations[selected_basin]
        return [{'label': station, 'value': station} for station in stations]
    return []    

# Callback to toggle graph visibility
@app.callback(
    Output('graph-container', 'children'),
    Input('close-graph-button', 'n_clicks')
)
def close_graph(n_clicks):
    if n_clicks > 0:
        return []  # Return an empty list to hide the graph
    return [
        html.Button('Close Graph', id='close-graph-button', n_clicks=0),
        dcc.Graph(figure=fig)
    ]  # Default to showing the graph

# Callback to update the table
@app.callback(
    Output('output-table', 'children'),
    Input('submit-button', 'n_clicks'),
    State('basin-dropdown', 'value'),
    State('date-picker', 'date')
)
def update_table(n_clicks, selected_basin, selected_date):
    if n_clicks > 0:
        # Mock data for demonstration purposes
        # data = {
        #     'Year': ['2020', '2019', '2018'],
        #     'Data Point 1': [100, 200, 300],
        #     'Data Point 2': [400, 500, 600],
        #     'Data Point 3': [700, 800, 900]  # Add more columns as needed
        # }
        # df = pd.DataFrame(data)
        
        report_data = generate_report_data(selected_basin, selected_date)


        return dash_table.DataTable(
            id='data-table',
            data= report_data.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={
                'margin': 'auto',
                'width': '100%',
                'overflowX': 'auto',  # Horizontal scrolling
                'maxHeight': '300px',  # Maximum height for vertical scrolling
                'overflowY': 'auto'  # Vertical scrolling
            },
            style_cell={'textAlign': 'center'},  # Center align text in table cells
            style_header={
                'backgroundColor': '#3498db',
                'color': 'white',
                'fontWeight': 'bold'
            },
            style_data={
                'backgroundColor': '#f9f9f9',
                'color': '#2c3e50'
            }
        )
    return None

# Callback to update the visualization widget
@app.callback(
    Output('visualization-widget', 'children'),
    Output('visible-graphs', 'data'),
    Input('data-table', 'active_cell'),
    State('data-table', 'data'),
    [Input({'type': 'close-button', 'index': ALL}, 'n_clicks')],
    State('visible-graphs', 'data')
)
def update_visualization_widget(active_cell, table_data, close_clicks, visible_graphs):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if isinstance(triggered_id, str) and triggered_id.startswith("{"):
        triggered_id = eval(triggered_id)

    if active_cell and 'index' not in triggered_id:
        row = active_cell['row']
        col = active_cell['column_id']
        cell_id = f"{row}-{col}"
        selected_data = table_data[row]

        if cell_id not in visible_graphs:
            visible_graphs.append(cell_id)

        figs = []
        for cell_id in visible_graphs:
            row, col = cell_id.split('-')
            row = int(row)
            selected_data = table_data[row]
            if col != 'Year':
                fig = px.line(
                    x=['Q1', 'Q2', 'Q3', 'Q4'],
                    y=[selected_data[col], selected_data[col], selected_data[col], selected_data[col]],
                    title=f"{col} for Year {selected_data['Year']}"
                )
                figs.append(html.Div([
                    html.Button('Close', id={'type': 'close-button', 'index': cell_id}, n_clicks=0),
                    dcc.Graph(figure=fig)
                ], id={'type': 'graph-widget', 'index': cell_id}))

        return html.Div(figs), visible_graphs

    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'close-button':
        cell_to_close = triggered_id['index']
        if cell_to_close in visible_graphs:
            visible_graphs.remove(cell_to_close)

        figs = []
        for cell_id in visible_graphs:
            row, col = cell_id.split('-')
            row = int(row)
            selected_data = table_data[row]
            if col != 'Year':
                fig = px.line(
                    x=['Q1', 'Q2', 'Q3', 'Q4'],
                    y=[selected_data[col], selected_data[col], selected_data[col], selected_data[col]],
                    title=f"{col} for Year {selected_data['Year']}"
                )
                figs.append(html.Div([
                    html.Button('Close', id={'type': 'close-button', 'index': cell_id}, n_clicks=0),
                    dcc.Graph(figure=fig)
                ], id={'type': 'graph-widget', 'index': cell_id}))

        return html.Div(figs), visible_graphs

    return dash.no_update

@app.callback(
    Output('stations-dropdown', 'options'),
    Input('basin-dropdown', 'value')
)
def update_stations_dropdown(selected_basin):
    # For now, we only have stations for Owyhee River Basin
    return [{'label': triplet, 'value': triplet} for triplet in stations_triplets]


if __name__ == '__main__':
    server.run(debug=True, port=5000)