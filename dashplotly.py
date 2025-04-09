import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get the min and max payload for RangeSlider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    html.Br(),

    html.Div(children=[
        html.Div(dcc.Graph(id='all-sites-pie-chart'), style={'width': '48%', 'display': 'inline-block'}),
        html.Div(dcc.Graph(id='site-specific-pie-chart'), style={'width': '48%', 'display': 'inline-block'}),
    ]),
    
    html.Br(),
    html.P("Payload range (Kg):"),
    
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for first pie chart (All sites success)
@app.callback(
    Output('all-sites-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_all_sites_pie(_):
    df = spacex_df[spacex_df['class'] == 1]
    fig = px.pie(df, values='class', names='Launch Site', title='Total Successful Launches by Site')
    return fig

# Callback for second pie chart (Selected site success/failure)
@app.callback(
    Output('site-specific-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_site_specific_pie(selected_site):
    if selected_site == 'ALL':
        # Placeholder pie chart
        fig = px.pie(
            names=['Select a specific site to view'],
            values=[1],
            title='No Specific Site Selected'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        class_labels = {0: 'Failure', 1: 'Success'}
        site_counts['class'] = site_counts['class'].map(class_labels)
        fig = px.pie(site_counts, values='count', names='class',
                     title=f'Success vs. Failure for {selected_site}')
    return fig

# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title=f'Success by Payload for {"All Sites" if selected_site == "ALL" else selected_site}',
                     labels={'class': 'Launch Outcome'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)


