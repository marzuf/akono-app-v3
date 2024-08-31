from dash.dependencies import Input, Output
from settings import *
from utils_fcts import *

def register_callbacks(app):
    # timedata_columns = get_timedata_columns()
    # timecols2show = [x for x in timedata_columns if not showcols_settings[x] == "NA"]

    timedata_columns = time_real_cols + time_added_cols
    timecols2show = time_real_cols + time_added_cols

    ############################################## MAIN CALLBACK RENDER_CONTENT

    # Callback pour mettre à jour le contenu des onglets
    # NB : component_property ne peut pas être choisi librement !!
    @app.callback(
        Output('tabs-content', 'children'),
        [Input('tabs-example', 'value'),
         Input('date-picker-dbdata', 'date')
         ]
    )
    def render_content(tab, picked_date):
        if tab == 'tab-dashboard':
            return html.Div([
                html.Div(id='subtabs-dashboard-content')
            ])
        elif tab == "tab-data":
            return html.Div([
                html.Div(id='subtabs-data-content')
            ])
        elif tab == 'tab-evotime':
            return html.Div([
                html.H3('Aperçu dans le temps'),

                get_period_dropdown('evotimeperiod-dropdown'),

                get_db_dropdown(id='evotimeTimeDB-db'),

               # html.Button('Afficher', id='show-evotime-btn', n_clicks=0),
                html.Div(id='evotime-range-info', style={'marginTop': '20px'}),

                dcc.Dropdown(
                    id='evotimeTimeDB-graph-col',
                    placeholder="Choisissez la colonne de données",
                    multi=True,
                    options=[{'label': col, 'value': col} for col in timecols2show]
                ),
                html.Div(id='evotimeTimeDB-graph-varinfo', style={'marginTop': '20px'}),
                dcc.Dropdown(
                    id='evotimeTimeDB-graph-viz',
                    options=[
                        {'label': 'Line Plot', 'value': 'lineplot'},
                        {'label': 'Bar Plot', 'value': 'barplot'},
                        {'label': 'Box Plot', 'value': 'boxplot'}
                    ],
                    placeholder="Choisissez le type de visualisation"
                ),
                html.Button('Visualiser', id='show-evotimeTimeDBgraph-btn',
                            n_clicks=0),
                dcc.Graph(id='evotimeTimeDB-graph',config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    })
            ])
        elif tab == 'tab-stat':
            return html.Div([
                html.H3('Valeur moyenne de chacune des variables'),
                get_period_dropdown('statperiod-dropdown'),
                html.Button('Afficher', id='show-stat-btn', n_clicks=0),
                html.Div(id='stat-range-info', style={'marginTop': '20px'}),
                html.Div(id='stat-means-info', style={'marginTop': '20px'}),
                html.H3('Visualisation des données'),
                get_db_dropdown(id='tabstatgraph-db'),

                dcc.Dropdown(
                    id='tabstatgraph-col',
                    placeholder="Choisissez la colonne de données"
                ),
                html.Div(id='tabstatgraph-varinfo', style={'marginTop': '20px'}),
                dcc.Dropdown(
                    id='tabstatgraph-viz',
                    options=[
                        {'label': 'Line Plot', 'value': 'lineplot'},
                        {'label': 'Bar Plot', 'value': 'barplot'},
                        {'label': 'Box Plot', 'value': 'boxplot'}
                    ],
                    placeholder="Choisissez le type de visualisation"
                ),
                html.Button('Visualiser', id='show-statgraph-btn', n_clicks=0),
                dcc.Graph(id='stat-graph', config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    })
            ])
        elif tab == 'tab-analyseGraph':
            return html.Div([
                html.H3('Analyse (graphiques)'),
                get_period_dropdown('asGraphPeriod-dropdown'),
                html.Div(id='analyseGraph-period-subtit', children=""),
                html.H4('Répartition des fréquences '),
                dcc.Dropdown(
                    id='asL-dropdown',
                    options=[
                        {'label': 'L1', 'value': 'as_L1'},
                        {'label': 'L2', 'value': 'as_L2'},
                        {'label': 'L1+L2', 'value': 'as_both'}
                    ],
                    value='as_L1',
                    placeholder="Source"
                ),
                html.Button('Afficher', id='show-asGraph-btn', n_clicks=0),
                html.Div(id='analyseGraph-pie-chart-tit', children=""),
                html.Div([
                    html.Div(id='analyseGraph-pie-chart-global', children="", className="col"),
                    html.Div(id='analyseGraph-pie-chart-day', children="", className="col"),
                    html.Div(id='analyseGraph-pie-chart-night', children="", className="col")
                ], className='row'),
                html.H4('Température batterie'),
                html.Div([
                    html.Div(id='analyseGraph-tempbat-barplot', children="", className="col")
                ], className='row')
            ])
        elif tab == 'tab-appareils':
            return html.Div([
                html.Div(id='subtabs-appareils-content')
            ])
        elif tab == 'tab-fonctions':
            return html.Div([
                html.Div(id='subtabs-fonctions-content')
            ])

