import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import plotly.colors as pc
import dash_bootstrap_components as dbc

# Load and transform data
df_wdd = pd.read_csv('world_development_data_imputed.csv')
df = df_wdd[df_wdd.Year > 1999]
df['GDPPerCap']=df['GDP']/df['PopTotal']
df = df.set_index('Year').reset_index()
df.Year = df.Year.astype(int)
df=df.replace('Turkiye','Turkey')

years = df.Year.unique()
country_name = []


data = {
    "Acronym": sorted(df.columns[5:]),
    "Description": [
    "Adolescent Fertility Rate - The number of births per 1,000 women ages 15-19.",
    "Agriculture Value Added as a Percentage of GDP - The contribution of agriculture to the Gross Domestic Product.",
    "Exports as a Percentage of GDP - The value of goods and services exported expressed as a percentage of Gross Domestic Product.",
    "Foreign Direct Investment, Net Balance of Payments - The net inflow of investment to acquire a lasting management interest in an enterprise operating in an economy other than that of the investor.",
    "Fertility Rate - The average number of children a woman would have during her lifetime.",
    "Gross Domestic Product - The total value of goods produced and services provided in a country during one year.",
    "GDP Growth Percentage - The annual percentage growth rate of Gross Domestic Product.",
    "GDP Per Capita - The Gross Domestic Product divided by the total population of the country.",
    "Gross National Income per Capita, Atlas Method - The gross national income divided by the midyear population, converted to international dollars using the Atlas method.",
    "Gross National Income, Atlas Method - The total domestic and foreign output claimed by residents of a country, converted to international dollars using the Atlas method.",
    "Imports as a Percentage of GDP - The value of goods and services imported expressed as a percentage of Gross Domestic Product.",
    "Industry Value Added as a Percentage of GDP - The contribution of the industrial sector to the Gross Domestic Product.",
    "Inflation, Consumer Prices Percentage - The annual percentage change in the cost to the average consumer of acquiring a basket of goods and services.",
    "Life Expectancy at Birth - The average number of years a newborn is expected to live if current mortality rates continue to apply.",
    "Merchandise Trade as a Percentage of GDP - The sum of merchandise exports and imports divided by the value of Gross Domestic Product.",
    "Mobile Subscriptions per 100 People - The number of mobile cellular subscriptions per 100 people.",
    "Under-Five Mortality Rate - The number of deaths of children under five years of age per 1,000 live births.",
    "Net Migration - The net total of migrants during a period, the total number of immigrants minus the annual number of emigrants.",
    "Population Density - The number of people living per unit of area (e.g., per square kilometer).",
    "Population Growth Percentage - The annual percentage increase in a population.",
    "Total Population - The total number of people inhabiting a particular area or country.",
    "Surface Area in Square Kilometers - The total area of a country or region, including land and water surfaces.",
    "Urban Population Growth Percentage - The annual percentage growth rate of the urban population."
]

}

# Initialize the app
app = Dash(__name__, 
           meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
           external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'])

# Define the app layout
app.layout = html.Div(children=[
    html.Div(children=[
        html.H1(className='title', children=['World Development Indicators']),
        dbc.Button(html.I(className="fas fa-info-circle"), id="info-button", color="info", style={"fontSize": "20px"}),
        dcc.Store(id='table-visible', data=False),  # Hidden div to store table visibility state
        html.Div(id="table-container", style={"margin-top": "20px"})
    ], className='title-container'),

    html.Div(
        className='container1',
        children=[
            html.Div(id='hidden-div', style={'display':'none'}), #dummy div
            html.Div(
                className='left-panel', 
                children=[
                    dcc.Dropdown(
                        options=[
                            {'label': 'GDP (Billions $)', 'value': 'GDP'},
                            {'label': 'GDP Per Capita', 'value': 'GDPPerCap'},
                            {'label': 'Population Density', 'value': 'PopDens'},
                            {'label': 'Population', 'value': 'PopTotal'},
                            {'label': 'Life Expectancy', 'value': 'LifeExpBirth'},
                        ], value='GDP', id='map_ind', className="map-drop"
                    ),
                    dcc.Graph(
                        id='indicator-map'
                    )
                ]
            ),
            html.Div(
                className='plot-container',
                children=[
                    html.Div(
                        className='inline-dropdowns',
                        children=[
                            dcc.Dropdown(
                                df.Country.unique(),
                                multi = True,
                                id='dropdown-country',
                                className='dropdown1'
                            ),
                            dcc.Dropdown(
                                df.columns[5:],
                                'GDP',
                                id='indicator',
                                className='dropdown2'
                            ),
                        ]
                    ),
                    html.Div(
                        dcc.Graph(
                            id='country',
                        ),className='country-line'),
                ]
            )
        ]
    ),
    html.Div(className='cont-row2', children=[ #diw drugi rząd
        
        html.Div(className='sec-row',children=[
            
            html.Div(
                className="container2",
                children=[
                    dcc.RadioItems(
                         value='Mean', className="radio-toolbar", id='stat_type'
                    ),
                    dcc.Graph(id='region_bar')
                ]
            ),
            html.Div(className='container3', children =[
                html.Div(className='bar-menu', children =[
                    dcc.RadioItems(
                            [
                                {'label':'Top', 'value':'Top'},
                                {'label':'Bottom', 'value':'Bottom'}
                            ], 'Top', className="topbot-toolbar", id='top-bot'
                        ),
                    dcc.Input(
                                id="input_range_2", type="number", placeholder="number of countries",
                                min=3, max=30, step=1, value=10, className="num-input"
                            ),
                ]),
                dcc.Graph(id='country_bar', className="bar-container"),
            ]),
        ]
        ),
        dcc.Slider(
                min=years[0],
                max=years[-1],
                step=1,
                value=years[0],
                id="year_slider",
                marks=None,
                tooltip={"placement": "bottom", "always_visible": True}, className="yslider",
            ),
    ]),

    html.Div(className="third-row", children=[
        dcc.RadioItems(
                        [
                            {'label': 'World', 'value': 'world'},
                            {'label': 'Americas', 'value': 'Americas'},
                            {'label': 'Europe', 'value': 'Europe'},
                            {'label': 'Africa', 'value': 'Africa'},
                            {'label': 'Asia', 'value': 'Asia'},
                            {'label': 'Oceania', 'value': 'Oceania'},
                        ], 'world', id='region_name_bubble', className="radio-toolbar"
                    ),
        dcc.Graph(id='bubble'),
        dcc.RangeSlider(min=1, max=13, step = None,marks={
            1:'0',
            2: '1k$',
            3: '10k$',
            4: '20k$',
            5: '30k$',
            6: '40k$',
            7: '50k$',
            8: '60k$',
            9: '70k$',
            10: '80k$',
            11: '90k$',
            12: '100k$',
            13: '135k$',
        }, value=[1, 13],id='gdp_range')
    ])

])

# Define callbacks
@app.callback(
    Output("table-container", "children"),
    Output('table-visible', 'data'),
    Input("info-button", "n_clicks"),
    State('table-visible', 'data'),
    prevent_initial_call=True
)
def toggle_table(n_clicks, visible):
    # Toggle visibility state
    if visible:
        return None, False
    else:
        # Create a table
        table_header = [
            html.Thead(html.Tr([html.Th("Acronym"), html.Th("Description")]))
        ]
        rows = [html.Tr([html.Td(data["Acronym"][i]), html.Td(data["Description"][i])]) for i in range(len(data["Acronym"]))]
        table_body = [html.Tbody(rows)]
        
        table = dbc.Table(table_header + table_body, bordered=True, dark=True, hover=True, responsive=True, striped=True)
        return html.Div(table, className="hover-table"), True




@callback(
    Output('indicator-map', 'figure'),
    Input('map_ind', 'value')
)
def plot_map(map_ind):
    #colors pallete log scaling:
    colors = px.colors.sequential.Blues
    if map_ind not in  ['LifeExpBirth']:
        df[map_ind+'log'] = np.log1p(df[map_ind])

        edges = pd.cut(df[map_ind+'log'], bins=len(colors)-1, retbins=True)[1]
        edges = edges[:-1] / edges[-1]
        
        edges = np.maximum(edges, np.full(len(edges), 0))

        cc_scale = (
            [(0, colors[0])]
            + [(e, colors[(i + 1) // 2]) for i, e in enumerate(np.repeat(edges, 2))]
            + [(1, colors[-1])]
        )

        ticks = np.linspace(df[map_ind+'log'].min(), df[map_ind+'log'].max(), len(colors))[1:-1]

        #plot:
        fig = px.choropleth(df, locations='Country', locationmode='country names', color=map_ind+'log',
                        hover_name='Country',hover_data= ['Country', 'Year', 'Region', map_ind],color_continuous_scale=cc_scale,
                        title='', projection='equirectangular', animation_frame='Year',template='plotly_dark')
        fig.update_layout(
            autosize=True,
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=4,
                autoexpand=True
            ),
            width=800,
        )
        fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
          'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
                                    
        if map_ind == 'GDP': 
            tick_label = (np.expm1(ticks)/10**9).round(0) #GDP in billions
        else:
            tick_label = np.expm1(ticks).round(0)
        fig.update_layout(
            coloraxis={
                "colorbar": {
                    "title" : map_ind,
                    "tickmode": "array",
                    "tickvals": ticks,
                    "ticktext": tick_label,
                }
            })
                
    else:
        fig = px.choropleth(df, locations='Country', locationmode='country names', color=map_ind,
                            hover_name='Country', color_continuous_scale=colors,
                            title='', projection='equirectangular', animation_frame='Year', template='plotly_dark')
        fig.update_layout(
            autosize=True,
            margin=dict(
                l=0,
                r=0,
                b=0,
                t=0,
                pad=4,
                autoexpand=True
            ),
            width=800,
        )
        fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
          'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    return fig


# dropdown reset:
@callback(
    Output('hidden-div','value'),
    Input('dropdown-country','value')
)
def reset(dropdown):
    global country_name
    global dropdown_list
    if len(dropdown)<1:
        country_name = []


@callback(
    [
        
        Output('dropdown-country', component_property='value')],
    [
        Input('indicator-map', 'clickData'),
        Input('indicator', 'value')]
)

def update_country(country, indicator):
    global country_name
    global dropdown_list
    if country is not None:
        country_name.append(country["points"][0]['hovertext'])
    country_name = list(set(country_name)) #unique values in country_name global list
    return [country_name]

@callback(
    Output('country', 'figure', allow_duplicate=True),
    Input('dropdown-country', 'value'),
    Input('indicator', 'value'),
    prevent_initial_call=True
)
def updateScatter(drop_country, indicator):
    global country_name
    country_name = drop_country
    fig = px.line(df[df['Country'].isin(drop_country)], x='Year', y=indicator, color='Country', markers=True, template='plotly_dark')

    fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
          'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    
    return fig

#callback and function blockin sum option for indicators other than GDP and PopTotal:
@callback(
    Output('stat_type', 'options'),
    Output('stat_type', 'value'),
    Input('indicator', 'value'),
    State('stat_type', 'value')
)
def update_stat_options(indicator, current_stat_value):
    if indicator in ['GDP', 'PopTotal']:
        options = [{'label': 'Sum', 'value': 'Sum'},
                   {'label': 'Mean', 'value': 'Mean'}]
        value = current_stat_value
    else:
        options = [{'label': 'Sum', 'value': 'Sum', 'disabled': True},
                   {'label': 'Mean', 'value': 'Mean'}]
        value = 'Mean'
    return options, value


#wykres słupkowy grupowany po regionie
@callback(
    Output('region_bar', 'figure'),
    Input('stat_type', 'value'),
    Input('year_slider', 'value'),
    Input('indicator', 'value'),
)

def update_region_bar(stat_type, year_slider, indicator):
    if (stat_type == 'Mean'):
        df_bar=df.groupby(by=['Region','Year'])[indicator].mean().to_frame()
        df_bar = df_bar.reset_index()
        df_bar = df_bar[df_bar['Year']==year_slider]
        fig = px.bar(df_bar,x='Region', y=indicator,template='plotly_dark')
    else:
        df_bar=df.groupby(by=['Region','Year'])[indicator].sum().to_frame()
        df_bar = df_bar.reset_index()
        df_bar = df_bar[df_bar['Year']==year_slider]
        fig = px.bar(df_bar,x='Region', y=indicator,template='plotly_dark')
    fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
          'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_traces(marker_color='#478ecc')
    return fig


#wykres słupkowy krajów:
@callback(
    Output('country_bar', 'figure'),
    Input('region_bar', 'clickData'),
    Input('year_slider', 'value'),
    Input('top-bot', 'value'),
    Input('input_range_2', 'value'),
    Input('indicator', 'value'),
)

def update_country_bar(region_bar, year_slider, top_bot, num_input, indicator):
    if region_bar == None:
        region_name = 'Europe'
    else: region_name=region_bar["points"][0]['label']
    if top_bot == 'Top':
        df_bar = df[(df['Region']==region_name)&(df['Year']==year_slider)].sort_values(by=indicator, ascending=False).iloc[:num_input]
    else: df_bar = df[(df['Region']==region_name)&(df['Year']==year_slider)].sort_values(by=indicator).iloc[:num_input]
    fig = px.bar(df_bar, x='Country', y=indicator, title='', template='plotly_dark')
    fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
          'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    fig.update_traces(marker_color='#478ecc')
    return fig


#Bubble plot:
@callback(
    Output('bubble', 'figure'),
    Input('region_name_bubble', 'value'),
    Input('gdp_range', 'value'),
    Input('year_slider','value'),
)

def update_bubble(region_name, gdp_range, year_slider):
    '''
    W range-slider są opcje 1 do 10 zapewniając równomierne rozłożenie wartości na osi
    Instrukcje match case przypisują nowe wartości aby filtrować odpowiednie wartości z ramki danych
    '''
    match gdp_range[0]:
        case 1:
            gdp_range[0] = 0
        case 2:
            gdp_range[0] = 10**3
        case 3:
            gdp_range[0] = 10**4
        case 4:
            gdp_range[0] = 2*10**4
        case 5:
            gdp_range[0] = 3*10**4
        case 6:
            gdp_range[0] = 4*10**4
        case 7:
            gdp_range[0] = 5*10**4
        case 8:
            gdp_range[0] = 6*10**4
        case 9:
            gdp_range[0] = 7*10**4
        case 10:
            gdp_range[0] = 8*10**4
        case 11:
            gdp_range[0] = 9*10**4
        case 12:
            gdp_range[0] = 10*10**4
        case 13:
            gdp_range[0] = 13.5*10**4

    match gdp_range[1]:
        case 1:
            gdp_range[1] = 0
        case 2:
            gdp_range[1] = 10**3
        case 3:
            gdp_range[1] = 10**4
        case 4:
            gdp_range[1] = 2*10**4
        case 5:
            gdp_range[1] = 3*10**4
        case 6:
            gdp_range[1] = 4*10**4
        case 7:
            gdp_range[1] = 5*10**4
        case 8:
            gdp_range[1] = 6*10**4
        case 9:
            gdp_range[1] = 7*10**4
        case 10:
            gdp_range[1] = 8*10**4
        case 11:
            gdp_range[1] = 9*10**4
        case 12:
            gdp_range[1] = 10*10**4
        case 13:
            gdp_range[1] = 13.5*10**4



    df_bub = df[(df.Year==year_slider)]
    df_bub = df_bub[(df_bub.GDPPerCap>=gdp_range[0])&(df_bub.GDPPerCap<=gdp_range[1])]
    min_bubble_size = 3
    max_bubble_size = 70
    if region_name == 'world':
        color_mapping = {
            "Asia": "#c73636",
            "Europe": "#4789bf",
            "Africa": "#49bf47",
            "Americas": "#d6892b",
            "Oceania": "#8f32d1"
        }
        region_order = ["Africa", "Americas", "Asia", "Europe", "Oceania"]
        

        fig = px.scatter(df_bub, x="GDPPerCap", y="LifeExpBirth",
	         size="PopTotal", color="Region",
                 hover_name="Country", log_x=True, size_max=max_bubble_size, color_discrete_map=color_mapping,
                 category_orders={"Region": region_order},template='plotly_dark')
        fig.update_traces(marker=dict(sizemin=min_bubble_size))
    else:
        unique_countries = df['Country'].unique()

        fig = px.scatter(df_bub[df_bub.Region == region_name], x="GDPPerCap", y="LifeExpBirth",
	         size="PopTotal", color="Country",
                 hover_name="Country", log_x=True, size_max=max_bubble_size,
                 category_orders={"Country": unique_countries},template='plotly_dark')
        fig.update_traces(marker=dict(sizemin=min_bubble_size))
    fig.update_layout(
        {'plot_bgcolor': 'rgba(0, 0, 0, 0)',
          'paper_bgcolor': 'rgba(0, 0, 0, 0)'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=False)