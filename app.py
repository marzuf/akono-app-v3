import dash_daq as daq
from settings import *
from utils_fcts import *
import plotly.express as px
from datetime import timedelta
import pandas as pd
import openpyxl
import numpy as np
from dash import dash_table
import pandas as pd
from datetime import datetime, timedelta
from app_settings import *
from plotly.subplots import make_subplots
from dash.dependencies import ALL


from callbacks.common_callbacks import register_callbacks as register_dashboard_common
from callbacks.tab_analyseGraphes_callbacks import register_callbacks as register_dashboard_analyseGraphes
from callbacks.render_content_callback import register_callbacks as register_render_content
from callbacks.tab_appareils_callbacks import register_callbacks as register_appareils
from callbacks.tab_timeevolution_callbacks import register_callbacks as register_timeevo
from callbacks.tab_fonctions_callbacks import register_callbacks as register_fonctions
from callbacks.tab_stat_callbacks import register_callbacks as register_stat
from callbacks.tab_dashboard_callbacks import register_callbacks as register_dashboard
from callbacks.tab_data_callbacks import register_callbacks as register_data
from callbacks.tab_accueil_callbacks import  register_callbacks as register_accueil

##################################### TODO IN PROCESS : dashboard
# https://dash.gallery/dash-manufacture-spc-dashboard/
# https://github.com/plotly/dash-sample-apps/blob/main/apps/dash-manufacture-spc-dashboard/app.py


conn = sqlite3.connect(db_file)
time_df = pd.read_sql_query(f"SELECT * FROM {dbTime_name}", conn)
day_df = pd.read_sql_query(f"SELECT * FROM {dbDayI_name}", conn)
conn.close()

time_df[db_timecol] = pd.to_datetime(time_df[db_timecol])
time_df[db_daycol] = time_df[db_timecol].dt.date
day_df[db_daycol] = pd.to_datetime(day_df[db_daycol])

# Initialiser l'application Dash avec suppression des exceptions de callback
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
                suppress_callback_exceptions=True
                )

register_dashboard_common(app)
register_dashboard_analyseGraphes(app)
register_render_content(app)
register_appareils(app)
register_timeevo(app)
register_stat(app)
register_fonctions(app)
#register_data(app)
register_dashboard(app)
register_accueil(app)

# Définir la mise en page de l'application

all_confirm_dialogs = [dcc.ConfirmDialog(id=x,message='')
                       for x in all_confirm_dialogs]

all_maxvar_dialogs = [dcc.ConfirmDialog(id=x,message=popupmsg_maxvar)
                       for x in ['confirm-dialog-evotime',
                                 'confirm-dialog-daydataP',
                                 'confirm-dialog-daydataI',
                                 ]]
all_dates = list(set(day_df[db_daycol]))
all_times = list(set(time_df[db_timecol]))

all_range_pickers = [get_range_picker(x, all_dates) for x in all_range_pickers]

app.layout = html.Div([

dcc.Store(id='stored_timeDB', data=time_df.to_dict()),
dcc.Store(id='stored_dayDB', data=day_df.to_dict()),
dcc.Store(id='defaut_stored_timeDB', data=time_df.to_dict()),
dcc.Store(id='defaut_stored_dayDB', data=day_df.to_dict()),
dcc.Store(id='stored_stat_dropdownval', data=None),
dcc.Store(id='stored_dataShowDB_dropdownval', data=None),
dcc.Store(id='stored_dataExportDB_dropdownval', data=None),
dcc.Store(id='stored_evotime_dropdownval', data=None),
dcc.Store(id='stored_analyseGraph_dropdownval', data=None),
dcc.Store(id='stored_appXT_dropdownval', data=None),
dcc.Store(id='stored_appBSP_dropdownval', data=None),
dcc.Store(id='stored_appVT_dropdownval', data=None),
dcc.Store(id='stored_fctBat_dropdownval', data=None),
dcc.Store(id='stored_dashMin_dropdownval', data=None),
dcc.Store(id='stored_dashDay_dropdownval', data=None),
                          dcc.Tabs(id="tabs-example", value='tab-accueil', children=[  # value ici définit l'onglet par défaut


        dcc.Tab(label='Accueil', value='tab-accueil',
                className='mytab', selected_className='mytab-slctd',
                children=[
                    html.Div([
                        # html.I(className="fas fa-sun") , html.H3("~ Bienvenue ~",
                        #         style={'textAlign': 'center', 'marginBottom': '20px'}),

                        html.H3([
                            html.I(className="fas fa-sun", style={"color": "#FFD700", "marginRight": "10px"}),
                            # Soleil à gauche
                            "Bienvenue",
                            html.I(className="fas fa-sun", style={"color": "#FFD700", "marginLeft": "10px"})
                            # Soleil à droite
                        ], style={"textAlign": "center", "marginTop": "20px"}),


                        html.H5("sur la plateforme de visualisation des données Akonolinga",
                                style={'textAlign': 'center', 'marginBottom': '20px'}),
                        html.Hr(),

            dcc.Checklist(
                id='default-data-checkbox',
                options=[
                    {'label': 'Données par défaut', 'value': 'default'},
                ],
                value=['default'],  # Coche par défaut
                style={'marginBottom': '20px'}
            ),

            html.Div([
                dcc.Upload(
                    id='upload-stored-data',
                    children=html.Button('Uploader des fichiers'),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'marginBottom': '20px'
                    },
                    multiple=True
                ),
            ], id='upload-stored-container', style={'display': 'none'}),  # Masqué par défaut

                html.Div(id='stored-data-content'),
                        html.Hr(),

                        dbc.Container([
                            dbc.Row([
                                dbc.Col([
                                    html.P([
                                        html.B("Dashboard"),
                                        " : vue d'ensemble des données disponibles ;  "+
                                        "cliquer sur chacune des variables pour rapidement avoir un aperçu la tendance dans le temps.",
                                        html.Ul([html.Li(["Pour les ",
                                                          get_nav_link("landpage-dashb-minutes-link", "Données minutes"),
                                                          ""]),
                                                            html.Li(["Pour les ",
                                                          get_nav_link("landpage-dashb-dayI-link", "Données journalières I"),
                                                          ""])
                                                 ]),
                                    ]),
                                    get_navbtn(lab="Dashboard", id='landpage-btn-dashboard')
                                ], width=4),

                                dbc.Col([
                                    dcc.Markdown("""
                                        **Évolution temporelle** : choisir une base de données puis une ou plusieurs (max. 4) variables ;
                                        visualisation à choix (line, bar, box).
                                    """),
                                    get_navbtn(lab="Évolution temporelle", id='landpage-btn-evotime')
                                ], width=4),

                                dbc.Col([
                                    dcc.Markdown("""
                                        **Statistiques - A SUPPRIMER ?** : choisir la table de données, une variable de cette table et le type de visualisation ;
                                        renvoie également les valeurs moyennes.
                                    """),
                                    get_navbtn(lab="Statistiques", id='landpage-btn-stat')

                                ], width=4)
                            ]),

                            html.Hr(),  # Ligne de séparation

                            dbc.Row([
                                dbc.Col([
                                    dcc.Markdown("""
                                        **Analyse (Graphes) - A SUPPRIMER ???** : visualiser la répartition des fréquences XT_Fin_Hz_I3122 (L1, L2, L1+L2 à choix) (diagramme camembert) 
                                        ainsi que la température moyenne de la batterie (barplot).
                                    """),
                                    get_navbtn(lab="Analyse (Graphes)", id='landpage-btn-analyseGraph')
                                ], width=4),

                                dbc.Col([
                                    # dcc.Markdown("""
                                    #     **Par appareil** : visualiser les principaux paramètre pour chacun des appareils.
                                    # """),
                                    # dbc.Button("Par appareil", id="landpage-btn-appareils",**navbtn_style)

                                    html.P([
                                        html.B("Par appareil"),
                                        " : visualiser les principaux paramètre pour chacun des appareils."
                                        "",
                                        html.Ul([html.Li(["Pour ",
                                                          get_nav_link("landpage-appareil-bsp-link",
                                                                       "BSP"),
                                                          """
                                                          (ligne temporelle avec qt 0.1 et 0.9 pour BSP_Ubat_Vdc_I7030_1, BSP_Ibat_Adc_I7031_1, BSP_Tbat_C_I7033_1 avec sa moyenne journalière ;
                                                          pour I7007_1 et I7008_1 : ligne temporelle avec mise en évidence des aires de différence, 
                                                                    barplot avec mise en évidence du surplus de l'un par rapport à l'autre, 
                                                                    ligne de delta I7008_1 - I7007_1, 
                                                                    barplot de rendement 100*I7008_1/I7007_1, 
                                                                    barplot nombre de cycles à 50% I7007_1/90)
                                                          """]),
                                                        html.Li(["Pour ",
                                                          get_nav_link("landpage-appareil-variotrack-link",
                                                                       "Variotrack"),
                                                          """
                                                          (ligne temporelle avec qt 0.1 et 0.9 pour VT_PsoM_kW_I11043_1 et VT_PsoM_kW_I11043_ALL,
                                                          ligne temporelle avec qt 0.1 et 0.9 pour VT_IbaM_Adc_I11040_1,
                                                          ligne temporelle avec qt 0.1 et 0.9 pour I11006_1 et I11007_1)
                                                          """]),

                                                 # html.Li(["Pour ",
                                                 #          get_nav_link("landpage-appareil-xtender-link",
                                                 #                       "Xtender"),
                                                 #          """
                                                 #          (lignes temporelles avec 0.1 et 0.9 qt pour XT_Ubat_MIN_Vdc_I3090_L1 et XT_Ubat_MIN_Vdc_I3090_L2,
                                                 #        lignes temporelles avec 0.1 et 0.9 qt pour XT_Uin_Vac_I3113_L1 et XT_Uin_Vac_I3113_L2,
                                                 #        lignes temporelles avec aires colorées pour XT_Pout_kVA_I3097_L1 et XT_Pout_kVA_I3097_L1,
                                                 #        lignes temporelles avec aires colorées pour XT_Iin_Aac_I3116_L1 et XT_Iin_Aac_I3116_L2,
                                                 #        XT_Fin_Hz_I3122_L1 et XT_Fin_Hz_I3122_L2 : barplots verticalement superposés  pour différencier la répartition des sources, stacked barplots répartition des sources par jour
                                                 #        side-by-side barplot pour I3081_1 et I3081_2)
                                                 #
                                                 #          """])
                                                 ]),
                                    ]),
                                    get_navbtn(lab="Par appareil", id='landpage-btn-appareils')

                                ], width=4),
                                dbc.Col([
                                    html.P([
                                        html.B("Par appareil (suite)"),
                                        " : visualiser les principaux paramètre pour chacun des appareils."
                                        "",
                                        html.Ul([
                                            # html.Li(["Pour ",
                                            #               get_nav_link("landpage-appareil-bsp-link",
                                            #                            "BSP"),
                                            #               """
                                            #               (ligne temporelle avec qt 0.1 et 0.9 pour BSP_Ubat_Vdc_I7030_1, BSP_Ibat_Adc_I7031_1, BSP_Tbat_C_I7033_1 avec sa moyenne journalière ;
                                            #               pour I7007_1 et I7008_1 : ligne temporelle avec mise en évidence des aires de différence,
                                            #                         barplot avec mise en évidence du surplus de l'un par rapport à l'autre,
                                            #                         ligne de delta I7008_1 - I7007_1,
                                            #                         barplot de rendement 100*I7008_1/I7007_1,
                                            #                         barplot nombre de cycles à 50% I7007_1/90)
                                            #               """]),
                                            #             html.Li(["Pour ",
                                            #               get_nav_link("landpage-appareil-variotrack-link",
                                            #                            "Variotrack"),
                                            #               """
                                            #               (ligne temporelle avec qt 0.1 et 0.9 pour VT_PsoM_kW_I11043_1 et VT_PsoM_kW_I11043_ALL,
                                            #               ligne temporelle avec qt 0.1 et 0.9 pour VT_IbaM_Adc_I11040_1,
                                            #               ligne temporelle avec qt 0.1 et 0.9 pour I11006_1 et I11007_1)
                                            #               """]),

                                                 html.Li(["Pour ",
                                                          get_nav_link("landpage-appareil-xtender-link",
                                                                       "Xtender"),
                                                          """
                                                          (lignes temporelles avec 0.1 et 0.9 qt pour XT_Ubat_MIN_Vdc_I3090_L1 et XT_Ubat_MIN_Vdc_I3090_L2,
                                                        lignes temporelles avec 0.1 et 0.9 qt pour XT_Uin_Vac_I3113_L1 et XT_Uin_Vac_I3113_L2, 
                                                        lignes temporelles avec aires colorées pour XT_Pout_kVA_I3097_L1 et XT_Pout_kVA_I3097_L1, 
                                                        lignes temporelles avec aires colorées pour XT_Iin_Aac_I3116_L1 et XT_Iin_Aac_I3116_L2,
                                                        XT_Fin_Hz_I3122_L1 et XT_Fin_Hz_I3122_L2 : barplots verticalement superposés  pour différencier la répartition des sources, stacked barplots répartition des sources par jour
                                                        side-by-side barplot pour I3081_1 et I3081_2)

                                                          """])
                                                 ]),
                                    ]),
                                    get_navbtn(lab="Par appareil", id='landpage-btn-appareils2')

                                ], width=4)

                            ]),

                            html.Hr(),  # Ligne de séparation

                            dbc.Row([
                                dbc.Col([

                                html.P([
                                    html.B("Par fonction - TODO / IN PROGRESS"),
                                    " : pour visualiser les données en fonction de leur utilisation dans le système ",
                                    html.Ul([html.Li(["Le sous-onglet ",
                                                      #        html.A("Export", id="export-link", href="#",
                                                      # style={"color": "#2507cf", "cursor": "pointer"}),
                                                      get_nav_link("landpage-fct-batterie-link", "Batterie"),
                                                      """ pour voir les données relative au fonctionnement de la batterie
                                                      (lignes temporelles avec quantiles pour XT_Ubat_Vdc_I3092_L1_1 et XT_Ubat_Vdc_I3092_L2_2 ;
                                                       lignes temporelles avec quantiles pour I7007_1 et I7008_1
                                                      """])
                                             ]),
                                ]),
                                get_navbtn(lab="Par fonction", id='landpage-btn-fonctions')       ], width=4),


                                dbc.Col([
                                    html.P([
                                        html.B("Données")," : Gérer, ajouter ou exporter des données de la base de données. ",
                                        "Obtenez un aperçu des tables disponibles. ",
                                         html.Ul([
                                             html.Li(["Le sous-onglet pour ",
                                                      get_nav_link("landpage-data-manage-link", "Gérer les données"),
                                                      " permet d'ajouter (fichier(s) csv) ou supprimer des données de la base de données."]),
                                             html.Li(["Le sous-onglet pour ",
                                                           get_nav_link("landpage-data-export-link", "Exporter des données"),
                                        " permet de télécharger les données pour une période sélectionnée (.xlsx) ou la base donnée complète (.db)."]),
                                             html.Li(["Le sous-onglet ",
                                                      get_nav_link("landpage-data-overview-link", "Aperçu"),
                                                      " permet d'afficher une partie du contenu de la base de données."])
                                                ], ),
                                    ]),
                    get_navbtn(lab="Données" ,id='landpage-btn-data')

                                ], width=4)
                            ])
                        ], fluid=True)
                    ], style={'padding': '40px', 'backgroundColor': '#f8f9fa'})
                ]),

        dcc.Tab(label='Dashboard', value='tab-dashboard',
                className='mytab', selected_className='mytab-slctd',
                children=[
                    dcc.Tabs(id="subtabs-dashboard", value='subtab-minutesdata', children=[
                        dcc.Tab(label='Données minutes', value='subtab-minutesdata',
                                className='mysubtab', selected_className='mysubtab-slctd'),
                        dcc.Tab(label='Données journalières', value='subtab-dayIdata',
                                className='mysubtab', selected_className='mysubtab-slctd'),

                    ]),                        dcc.Store(id='store-summary-minutes'),
                        dcc.Store(id='store-dbTime_df'),
                        dcc.Store(id='store-summary-dayI'),
                        dcc.Store(id='store-dbDayI_df')]),

        dcc.Tab(label='Evolution temporelle', value='tab-evotime',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Statistiques', value='tab-stat',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Analyse (graphes)', value='tab-analyseGraph',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Par appareil', value='tab-appareils',
                className='mytab', selected_className='mytab-slctd',
             children=[
            dcc.Tabs(id="subtabs-appareils", value='subtab-bsp', children=[
                dcc.Tab(label='BSP', value='subtab-bsp',
                        className='mysubtab', selected_className='mysubtab-slctd'),
                dcc.Tab(label='VarioTrack', value='subtab-variotrack',
                            className='mysubtab', selected_className='mysubtab-slctd'),
                dcc.Tab(label='Xtender', value='subtab-xtender',
                                className='mysubtab', selected_className='mysubtab-slctd')
            ])]),
        dcc.Tab(label='Par fonction', value='tab-fonctions',
                className='mytab', selected_className='mytab-slctd',
                children=[
                    dcc.Tabs(id="subtabs-fonctions", value='subtab-batterie', children=[
                        dcc.Tab(label='Batterie', value='subtab-batterie',
                                className='mysubtab', selected_className='mysubtab-slctd')
                    ])]),

        dcc.Tab(label='Données', value='tab-data',
                className='mytab', selected_className='mytab-slctd',
                children=[
                    dcc.Tabs(id="subtabs-data", value='subtab-updateDB', children=[
                        dcc.Tab(label='Gérer les données', value='subtab-updateDB',
                                className='mysubtab', selected_className='mysubtab-slctd'),
                        dcc.Tab(label='Exporter des données', value='subtab-exportDB',
                                    className='mysubtab', selected_className='mysubtab-slctd'),
                        dcc.Tab(label='Aperçu de la base de données', value='subtab-showDB',
                                className='mysubtab', selected_className='mysubtab-slctd')
                    ])])
             ]),
    dcc.DatePickerSingle(
        id='date-picker-dbdata',
        date=None,
        display_format='DD.MM.YYYY',
        min_date_allowed=min(all_times),

        max_date_allowed=max(all_times),
        disabled_days=[pd.to_datetime(date).date() for date in
                       pd.date_range(start=min(all_times),
                                     end=max(all_times)).
                       difference(pd.to_datetime(all_times))],
        style={'display': 'none'}  # Initialement caché
        # attention : pd.date_range(...).retourne un DatetimeIndex
        # pd.to_datetime pour convertir all_dates aussi en DatetimeIndex pr comparer
    )] +
                      all_range_pickers +
                      all_maxvar_dialogs +
                      all_confirm_dialogs+
    [html.Div(id='tabs-content')]

)



# Callback pour gérer la navigation vers les onglets et sous-onglets
@app.callback(
    [Output('tabs-example', 'value'),
     Output('subtabs-appareils', 'value'),
     Output('subtabs-data', 'value')],
    [Input('landpage-btn-dashboard', 'n_clicks'),
     Input('landpage-btn-evotime', 'n_clicks'),
     Input('landpage-btn-stat', 'n_clicks'),
     Input('landpage-btn-analyseGraph', 'n_clicks'),
     Input('landpage-btn-appareils', 'n_clicks'),
Input('landpage-btn-appareils2', 'n_clicks'),
     Input('landpage-appareil-variotrack-link', 'n_clicks'),
     Input('landpage-btn-fonctions', 'n_clicks'),
     Input('landpage-btn-data', 'n_clicks'),
     Input('landpage-data-export-link', 'n_clicks'),
Input('landpage-data-overview-link', 'n_clicks'),
Input('landpage-data-manage-link', 'n_clicks'),
Input('landpage-dashb-minutes-link', 'n_clicks'),
Input('landpage-dashb-dayI-link', 'n_clicks'),
Input('landpage-appareil-bsp-link', 'n_clicks'),
Input('landpage-appareil-xtender-link', 'n_clicks'),
     ],
    [State('tabs-example', 'value')]
)
def navigate_to_tabs_and_subtabs(*args):
    current_tab = args[-1]
    ctx = dash.callback_context

    # Valeurs par défaut pour les onglets et sous-onglets
    tab_value = current_tab or 'tab-accueil'
    subtab_appareils_value = 'subtab-bsp'  # Valeur par défaut pour les sous-onglets d'appareils
    subtab_data_value = 'subtab-updateDB'  # Valeur par défaut pour les sous-onglets de données

    # Si un bouton est cliqué
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Gestion de la navigation pour les onglets principaux
        if button_id in ['landpage-btn-dashboard','landpage-dashb-minutes-link',
                                            'landpage-dashb-dayI-link']:
            tab_value = 'tab-dashboard'
            if button_id == 'landpage-dashb-minutes-link':
                subtab_data_value = 'subtab-minutesdata'
            elif button_id == 'landpage-dashb-dayI-link':
                subtab_data_value = 'subtab-dayIdata'

        elif button_id == 'landpage-btn-evotime':
            tab_value = 'tab-evotime'
        elif button_id == 'landpage-btn-stat':
            tab_value = 'tab-stat'
        elif button_id == 'landpage-btn-analyseGraph':
            tab_value = 'tab-analyseGraph'
        elif button_id in ['landpage-btn-appareils','landpage-btn-appareils2', 'landpage-appareil-variotrack-link',
                           "landpage-appareil-bsp-link", "landpage-appareil-xtender-link", ]:
            tab_value = 'tab-appareils'
            if button_id == 'landpage-appareil-variotrack-link':
                subtab_appareils_value = 'subtab-variotrack'
            elif button_id == 'landpage-appareil-xtender-link':
                    subtab_appareils_value = 'subtab-xtender'
            elif button_id == 'landpage-appareil-bsp-link':
                    subtab_appareils_value = 'subtab-bsp'


        elif button_id == 'landpage-btn-fonctions':
            tab_value = 'tab-fonctions'
        elif button_id in ['landpage-btn-data',
                           'landpage-data-export-link',
                           'landpage-data-manage-link',
                           'landpage-data-overview-link']:
            tab_value = 'tab-data'
            if button_id == 'landpage-export-link':
                subtab_data_value = 'subtab-exportDB'
            elif button_id == 'landpage-data-manage-link':
                subtab_data_value = 'subtab-updateDB'
            elif button_id == 'landpage-data-overview-link':
                subtab_data_value = 'subtab-showDB'
    # Retourner les valeurs des onglets et sous-onglets
    return tab_value, subtab_appareils_value, subtab_data_value

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=True)
    # for deploy
    #     app.run(debug=True, host='0.0.0.0', port=7860)
