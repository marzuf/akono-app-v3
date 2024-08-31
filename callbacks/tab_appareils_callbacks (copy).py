import sys

import pandas as pd
from dash.dependencies import Input, Output
from settings import *
from utils_fcts import *
from app_settings import *
from plotly.subplots import make_subplots
import plotly.express as px


def register_callbacks(app):

    ################################################################################################
    ################################ CALLBACKS SUBTAB PAR APPAREIL
    ################################################################################################
    # Définir les callbacks pour mettre à jour le contenu des sous-onglets
    @app.callback(Output('subtabs-appareils-content', 'children'),
                  [Input('subtabs-appareils', 'value')])
    def render_subtab_appareils_content(subtab):
        if subtab == 'subtab-variotrack':
            return html.Div([
                html.H4("Données de l'appareil VarioTrack"),
                get_period_dropdown('subvariotrack-period-dropdown'),
                html.Button('Afficher', id='show-variotrack-btn', n_clicks=0),
                html.Div(id='subvariotrack-range-info', style={'marginTop': '20px'}),
                html.Div(id='subtab-variotrack-content', style={'marginTop': '20px'}),
            ])
        elif subtab == 'subtab-xtender':
            return html.Div([
                html.H4("Données de l'appareil XTender"),
                get_period_dropdown('subxtender-period-dropdown'),
                html.Button('Afficher', id='show-xtender-btn', n_clicks=0),
                html.Div(id='subxtender-range-info', style={'marginTop': '20px'}),
                html.Div(id='subtab-xtender-content', style={'marginTop': '20px'}),
            ])
        elif subtab == 'subtab-bsp':
            return html.Div([
                html.H4("Données de l'appareil BSP"),
                get_period_dropdown('subbsp-period-dropdown'),
                html.Button('Afficher', id='show-bsp-btn', n_clicks=0),
                html.Div(id='subbsp-range-info', style={'marginTop': '20px'}),
                html.Div(id='subtab-bsp-content', style={'marginTop': '20px'}),
            ])





    ######################################################################
    # graphes variotrack
    ######################################################################
    @app.callback(
        [Output('subtab-variotrack-content', 'children'),
         Output('confirm-dialog-subvariotrack', 'displayed'),
         Output('confirm-dialog-subvariotrack', 'message'),
         Output('subvariotrack-range-info', 'children')],
        [Input('show-variotrack-btn', 'n_clicks')],
        [
         State('range-picker-subvariotrack', 'start_date'),
         State('range-picker-subvariotrack', 'end_date'),
            State('subvariotrack-period-dropdown', 'value'),
            State('stored_timeDB', 'data'),
            State('stored_dayDB', 'data')
        ]
    )
    def display_variotrack_graph(n_clicks,start_date, end_date, selected_period,
                                 time_db, day_db):
        selected_col = "FOO"
        selected_db = dbTime_name
        df = pd.DataFrame(time_db)

        if n_clicks is None or n_clicks == 0:
            return ["", False, "", ""]

        if not selected_db or not selected_col:
            return ["", True, "Sélectionnez des données", ""]

        if selected_period == "stat_perso" and (start_date or not end_date):
            return ["", True, "Sélectionnez une période", ""]

        if selected_period == "stat_perso" :
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else :
            start_date, end_date = get_startrange_date_vLatest(df[db_timecol], selected_period)

        date_info = f"Données du {start_date} au {end_date}"


        if selected_db == dbTime_name:
            xcol = db_timecol
        else:
            xcol = db_daycol
            if selected_db == dbDayI_name:
                for col in dayI_cols:
                    df[col] = df[col + "_1"].fillna(0) + df[col + "_2"].fillna(0)


        div_container = []
        ##** GRAPHE 1 - VT PSo
        plot1 = get_dbTime_2vargraph(df, xcol,"VT_PsoM_kW_I11043_1", "VT_PsoM_kW_I11043_ALL")
        div_container.append(dcc.Graph(id='graph-VT_PsoM', figure=plot1[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot1[1],
                                          dangerously_allow_html=True))
        # ##** GRAPHE 2 - XT Uin
        plot2 = get_dbTime_2vargraph(df, xcol,"VT_IbaM_Adc_I11040_1")
        div_container.append(dcc.Graph(id='graph-VT_IbaM', figure=plot2[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot2[1],
                                          dangerously_allow_html=True))
    #### ajouter les variables I
        selected_db = dbDayI_name
        # queryI = get_query_extractInterval(selected_db, start_date, end_date)
        # conn = sqlite3.connect(db_file)
        # print(queryI)
        # dayI_df = pd.read_sql_query(queryI, conn)
        # conn.close()
        dayI_df = day_db

        if selected_period == "stat_perso" :
            start_date, end_date = get_startrange_date_vLatest(dayI_df[db_daycol], selected_period)

        print(" nrow " + str(dayI_df.shape[0]))
        print('show first days dayI: ' + ','.join(dayI_df['day']))

        IvarsVT = [x for x in dayIcols_settings.keys() if
                        dayIcols_settings[x]["source"] == "VarioTrack" and
                                    x in dayI_df.columns ]
        ### I11006 et I11007 ; seulement valeur dans colonne 1
        emptycols = [x for x in IvarsVT if "_2" in x]
        assert dayI_df[emptycols].isna().all().all()
        IvarsVT_toplot = [x for x in IvarsVT if "_1" in x]
        dayI_df = dayI_df[[db_daycol]+IvarsVT_toplot]

        # # Reshape le DataFrame en long format
        dayI_df_long = dayI_df.melt(id_vars=['day'],
                                    value_vars=IvarsVT_toplot,
                                    var_name='variable', value_name='value')
        assert len(IvarsVT_toplot)==2#
        colors = {'green': IvarsVT_toplot[0], 'red': IvarsVT_toplot[1]}

        ## grpahe 3
        plot3= get_dbTime_2vargraph(dayI_df, db_daycol,col1=IvarsVT_toplot[0],
                                    col2 = IvarsVT_toplot[1],
                                    dbName = dbDayI_name,
                                    startDate=start_date, endDate=end_date)
        div_container.append(dcc.Graph(id='graph-VT_dayIprod', figure=plot3[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot3[1],
                                          dangerously_allow_html=True))

        return [div_container, False, "", date_info]

    ######################################################################
    # graphes BSP
    ######################################################################
    @app.callback(
        [Output('subtab-bsp-content', 'children'),
         Output('confirm-dialog-subbsp', 'displayed'),
         Output('confirm-dialog-subbsp', 'message'),
         Output('subbsp-range-info', 'children')],
        [Input('show-bsp-btn', 'n_clicks')],
        [
         State('range-picker-subbsp', 'start_date'),
         State('range-picker-subbsp', 'end_date'),
            State('subbsp-period-dropdown', 'value'),
            State('stored_timeDB', 'data'),
            State('stored_dayDB', 'data')
        ]
    )
    def display_bsp_graph(n_clicks,start_date, end_date, selected_period, time_db, day_db):
        selected_db = dbTime_name
        selected_col = "FOO"
        df = pd.DataFrame(time_db)

        if n_clicks is None or n_clicks == 0:
            return ["", False, "", ""]

        if not selected_db or not selected_col :
            return [ "", True, "Sélectionnez des données", ""]

        if selected_period == "stat_perso" and (not start_date or not end_date):
            return ["", True, "Sélectionnez une période", ""]

        if selected_period == "stat_perso":
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start_date, end_date = get_startrange_date_vLatest(df[db_timecol], selected_period)


        date_info = f"Données du {start_date} au {end_date}"


        if selected_db == dbTime_name:
            xcol = db_timecol
        else:
            xcol = db_daycol
            if selected_db == dbDayI_name:
                for col in dayI_cols:
                    df[col] = df[col + "_1"].fillna(0) + df[col + "_2"].fillna(0)
        div_container = []

        ##** GRAPHE 1 - ubat
        plot1 = get_dbTime_2vargraph(df, xcol,"BSP_Ubat_Vdc_I7030_1", startDate=start_date,
                                     endDate = end_date)
        div_container.append(dcc.Graph(id='graph-BSP_ubat', figure=plot1[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot1[1],
                                          dangerously_allow_html=True))
        # ##** GRAPHE 2 - ibat
        plot2 = get_dbTime_2vargraph(df, xcol,"BSP_Ibat_Adc_I7031_1",
                                     startDate=start_date,
                                     endDate = end_date)
        div_container.append(dcc.Graph(id='graph-BSP_ibat', figure=plot2[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot2[1],
                                          dangerously_allow_html=True))

        # ##** GRAPHE 3 - tbat ### température moyenne  !!!
        ### ajouter une colonne -> ou je remplacer chaque valeur par al moyenne
        df[db_timecol] = pd.to_datetime(df[db_timecol])
        curr_var = 'BSP_Tbat_C_I7033_1'
        func = "mean"
        new_var = curr_var+'_day'+func.title()
        df[new_var] = df.groupby(df[db_timecol].dt.date)[curr_var].transform(func)
    # La température moyenne de la batterie (I7033 BSP) (plutôt graph colonnes)
        varsettingsdict = {}
        varsettingsdict[curr_var] = {'description' : showcols_settings[curr_var]['description']}
        varsettingsdict[new_var] = {'description' : "moyenne journalière de " + curr_var}
        plot3 = get_dbTime_2vargraph(df, xcol, curr_var,
                                     col2=new_var,
                                     settingsdict=varsettingsdict,
                                     startDate=start_date,
                                     endDate=end_date)
        div_container.append(dcc.Graph(id='graph-BSP_tbat', figure=plot3[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot3[1],
                                          dangerously_allow_html=True))

        #### ajouter les variables I
        ### TODO : LOADER LA TABLE
        ## FILTER LES IVARS_TOPLOT QUI SONT DANS COLNAMES
        selected_db = dbDayI_name
        # if selected_period == "stat_all":
        #     queryI = get_query_extractInterval(selected_db, None, None)
        # else:
        #     queryI = get_query_extractInterval(selected_db, start_date, end_date)
        #
        # conn = sqlite3.connect(db_file)
        # print(queryI)
        # dayI_df = pd.read_sql_query(queryI, conn)
        # conn.close()

        dayI_df = pd.DataFrame(day_db)
        start_date, end_date = get_startrange_date_vLatest(dayI_df[db_daycol], selected_period)

        print(" nrow " + str(dayI_df.shape[0]))
        print('show first days dayI: ' + ','.join(dayI_df['day']))
        print(dayI_df['I7008_1'])
        print(dayI_df['I7007_1'])
        ##  le "throughput energy" journalier I7007 [AH]  BSP
        # Le bilan des Ah chargé et déchargé du jour I7008-I7007 BSP
        # 	Pour la Batterie : champs fixe sans lien avec le segment temporel affiché
        #  le "throughput energy" total: Somme I7007 [AH] BSP
        # Rendement de batterie:( I7008/I7007) *100 BSP
        # Nombre de cycle (à 50%) tot I7007/90 arrondi 0BSP
        IvarBSP = [x for x in dayIcols_settings.keys() if
                        dayIcols_settings[x]["source"] == "BSP" and
                                    x in dayI_df.columns ]
        ### I7007 et I7008 ; seulement valeur dans colonne 1
        emptycols = [x for x in IvarBSP if "_2" in x]
        assert dayI_df[emptycols].isna().all().all()
        IvarBSP_toplot = [x for x in IvarBSP if "_1" in x]
        assert len(IvarBSP_toplot) == 2

        dayI_df = dayI_df[[db_daycol]+IvarBSP_toplot]

        ## grpahe 5 différence entre 7007 et 7008
        # Calcul des zones colorées
        df=dayI_df.copy()
        df['day'] = pd.to_datetime(df['day'])
        df.set_index('day', inplace=True)
        plot5 = get_intersectLines_plot(df, db_daycol,
                                        col1=IvarBSP_toplot[0],
                                        col2=IvarBSP_toplot[1],
                                        startDate= start_date, endDate=end_date)
        div_container.append(dcc.Graph(id = "ivarbsp_intersectarea",
                                       figure=plot5,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        plot5_desc = get_plotdesc(IvarBSP_toplot[0], col2=IvarBSP_toplot[1], db=dbDayI_name)
        div_container.append(dcc.Markdown(plot5_desc,
                                          dangerously_allow_html=True))
        df = dayI_df.copy()
        plot6 = get_stacked_cmpgraph(df, db_daycol, IvarBSP_toplot[0],IvarBSP_toplot[1],
                                     settingsdict=dayIcols_settings,
                                     startDate = start_date, endDate = end_date)

        fig6 = plot6[0]
        fig6.update_layout(
            title = "Bilan des Ah chargés et déchargés " +
                                    f'(<b>{IvarBSP_toplot[0]}</b> et <b>{IvarBSP_toplot[1]}</b>)',
            yaxis_title="Valeur"
        )

        div_container.append(dcc.Graph(id='ivarbsp_area', figure=fig6,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot6[1],
                                          dangerously_allow_html=True))

    # # Rendement de batterie:( I7008/I7007) *100 BSP
        df=dayI_df.copy()
        df['delta'] = df["I7008_1"] - df["I7007_1"]
        df['rendement'] = (df["I7008_1"] / df["I7007_1"]) * 100
        df['rendement_pos'] = df['rendement'] - 100
        df['rendement_neg'] = df['rendement'] - 100

        # Créer les sous-graphiques
        figRel = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            subplot_titles=("Delta", "Rendement"))

        # Tracer 'delta' (graphique du haut)
        figRel.add_trace(go.Scatter(x=df.index, y=df['delta'],
                                 mode='lines', name='Delta',
                                 line=dict(color='black')), row=1, col=1)

        # Ajouter les zones de fond pour 'delta'
        figRel.add_shape(type="rect", xref="x", yref="y",
                      x0=df.index.min(), y0=0, x1=df.index.max(), y1=df['delta'].max(),
                      fillcolor="rgba(255, 0, 0, 0.2)", layer="below", row=1, col=1)
        figRel.add_shape(type="rect", xref="x", yref="y",
                      x0=df.index.min(), y0=df['delta'].min(), x1=df.index.max(), y1=0,
                      fillcolor="rgba(0, 0, 255, 0.2)", layer="below", row=1, col=1)

        # Tracer les barres de 'rendement' (graphique du bas)
        figRel.add_trace(go.Bar(x=df.index, y=np.where(df['rendement'] >= 100, df['rendement_pos'], 0),
                             name='Rendement > 100', marker=dict(color='red')), row=2, col=1)
        figRel.add_trace(go.Bar(x=df.index, y=np.where(df['rendement'] < 100, df['rendement_neg'], 0),
                             name='Rendement < 100', marker=dict(color='blue')), row=2, col=1)

        # Mise à jour de la mise en page
        figRel.update_layout(
            title_text="<b>Delta (I7008_1-I7007_1) et Rendement (100*I7008_1/I7007_1)</b>",
            height=1000,
            xaxis=dict(title=db_daycol.title()),
            yaxis=dict(title='Delta', zerolinecolor='gray'),
            yaxis2=dict(title='Rendement', zerolinecolor='gray', zerolinewidth=2),
            barmode='overlay'  # Superposer les barres
        )

        figRel.update_xaxes(range=[start_date, end_date])

        figRel_desc = get_plotdesc("I7007_1" ,"I7008_1",db=dbDayI_name)
        # Ajouter le graphique à l'application Dash
        div_container.append(dcc.Graph(id='ivarbsp_rendement', figure=figRel,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(figRel_desc,
                                          dangerously_allow_html=True))

        # Nombre de cycle (à 50%) tot I7007/90 arrondi 0BSP
        df=dayI_df.copy()
        df['cycles'] = round(df["I7007_1"]/90)

        figCycles = go.Figure()

        figCycles.add_trace(go.Bar(x=df[db_daycol], y=df['cycles'],
                              name='Cycles', marker=dict(color='darkblue')))

        figCycles.update_layout(
        title="<b>Nombre de cycles à 50% I7007_1/90</b>",
        title_font=dict(size=20),
            xaxis_title=db_daycol.title(),
            yaxis_title="I7007_1/90")

        figCycles.update_xaxes(range=[start_date, end_date])


        figCycles_desc = get_plotdesc("I7007_1" ,db=dbDayI_name)
        # Ajouter le graphique à l'application Dash
        div_container.append(dcc.Graph(id='ivarbsp_nbcycles', figure=figCycles,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(figCycles_desc,
                                          dangerously_allow_html=True))


        return [div_container, False, "", date_info]

    ######################################################################
    # graphes xtender
    ######################################################################
    # Callback pour afficher le graphique en fonction de la sélection :
    @app.callback(
        [Output('subtab-xtender-content', 'children'),
         Output('confirm-dialog-subxtender', 'displayed'),
         Output('confirm-dialog-subxtender', 'message'),
         Output('subxtender-range-info', 'children'),],
        [Input('show-xtender-btn', 'n_clicks')],
        [
         State('range-picker-subxtender', 'start_date'),
         State('range-picker-subxtender', 'end_date'),
        State('subxtender-period-dropdown', 'value'),
            State('stored_timeDB', 'data'),
            State('stored_dayDB', 'data')
        ]
    )
    def display_xtender_graph(n_clicks,start_date, end_date, selected_period, time_db, day_db):
        selected_db = dbTime_name
        selected_col = "FOO"

        df = pd.DataFrame(time_db)

        if n_clicks is None or n_clicks == 0:
            return ["", False, "", ""]

        if not selected_db or not selected_col:
            return ["", True, "Sélectionnez des données", ""]


        if selected_period == "stat_perso" and (not start_date or not end_date):
                return ["", True, "Sélectionnez une date de début et fin", ""]
        if selected_period == "stat_perso" :
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else :
            start_date, end_date = get_startrange_date_vLatest(df[db_timecol], selected_period)

        date_info = f"Données du {start_date} au {end_date}"

        # conn = sqlite3.connect(db_file)
        # df = pd.read_sql_query(query, conn)
        # conn.close()

        if selected_db == dbTime_name:
            df = time_db
        elif selected_db == dbDayI_name:
            df = day_db
        else:
            sys.exit(1)


        if selected_db == dbTime_name:
            xcol = db_timecol
        else:
            xcol = db_daycol
            if selected_db == dbDayI_name:
                for col in dayI_cols:
                    df[col] = df[col + "_1"].fillna(0) + df[col + "_2"].fillna(0)
        # xt fin discriminer Fréquence du réseau ou de la génératrice.
        # Les 2 sources peuvent être disciminée par leurs valeur:
        # Le réseau à une fréquence très stable <49,5Hz-50,5Hz>.
        # La generatrice est moin stable est a une fréquence généralement supérieure a 51Hz.
        # Une valeur nule indique l''absence de la source réseau/génératrice
        # XT-Phase []
        # Phase de charge de batterie.Dan ce système seule 3 phase devraient apparaitre:
        # Charge de masse,(1 rouge), Absorbtion, (2 orange), et Mintient (4 Jaune)
        # XT-Transfert []
        # Cette info pourrait être exploitée pour signaler la présence du réseau su les entrées.
        # Elle Vaut 1 lorsqu'une source est présente et 0 lorsque la source est absent est que les
        # 2 appareix foncctionnet en mode onduleur
        div_container = []
        ##** GRAPHE 1 - XT UBAT
        plot1 = get_dbTime_2vargraph(df, xcol,"XT_Ubat_MIN_Vdc_I3090_L1",
                                     "XT_Ubat_MIN_Vdc_I3090_L2",
                                     endDate=end_date, startDate=start_date)
        div_container.append(dcc.Graph(id='graph-XT_Ubat', figure=plot1[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot1[1],
                                          dangerously_allow_html=True))
        ##** GRAPHE 2 - XT Uin
        plot2 = get_dbTime_2vargraph(df, xcol,"XT_Uin_Vac_I3113_L1",
                                     "XT_Uin_Vac_I3113_L2", endDate=end_date, startDate=start_date)
        div_container.append(dcc.Graph(id='graph-XT_Uin', figure=plot2[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot2[1],
                                          dangerously_allow_html=True))

        ##** GRAPHE 3 - XT-Pout
        plot3 = get_dbTime_2vargraph(df, xcol,"XT_Pout_kVA_I3097_L1", "XT_Pout_kVA_I3097_L2",
                                     withQtLines = False, stacked = True,
                                     endDate=end_date, startDate=start_date)
        div_container.append(dcc.Graph(id='graph-XT_Pout', figure=plot3[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot3[1],
                                          dangerously_allow_html=True))
        ##** GRAPHE 4 - XT-Iin
        plot4 = get_dbTime_2vargraph(df, xcol,"XT_Iin_Aac_I3116_L1", "XT_Iin_Aac_I3116_L2",
                                     withQtLines = False, stacked = True)
        div_container.append(dcc.Graph(id='graph-XT_Iin', figure=plot4[0],config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(plot4[1],
                                          dangerously_allow_html=True))

        ###** graphe 5 : XT Fin - a) valeurs minutes
        # Rescaler les valeurs pour que l'axe des x soit à y=51
        col1 = "XT_Fin_Hz_I3122_L1"
        col2 = "XT_Fin_Hz_I3122_L2"
        df['source'] = np.where(df[col1] == 0, 'Absence de source',
                                np.where(df[col1].between(49.5, 50.5), 'Réseau',
                                         np.where(df[col1] > 51, 'Génératrice', 'Incertain')))

        df['source2'] = np.where(df[col2] == 0, 'Absence de source',
                                np.where(df[col2].between(49.5, 50.5), 'Réseau',
                                         np.where(df[col2] > 51, 'Génératrice', 'Incertain')))

        colors = freq_colors
        unique_sources = set(df['source'].unique()).union(df['source2'].unique())
        figBarMin = make_subplots(rows=len(unique_sources), cols=1,
                            shared_xaxes=True, vertical_spacing=0.02)
        source_list = list(unique_sources)
        inosource = None
        for i, source in enumerate(source_list):
            source_df1 = df[df['source'] == source]
            source_df2 = df[df['source2'] == source]

            if source == "Absence de source":
                inosource = i
                assert np.all(source_df1[col1] == 0)
                assert np.all(source_df2[col2] == 0)
                source_df1[col1] = 1
                source_df1[col2] = 1

            figBarMin.add_trace(go.Bar(
                x=source_df1[db_timecol],
                y=source_df1[col1],
                name=f'{source} {col1}',
                marker_color=colors.get(source, 'grey'),
                showlegend=True if i == 0 else False
            ), row=i + 1, col=1)

            figBarMin.add_trace(go.Bar(
                x=source_df2[db_timecol],
                y=source_df2[col2],
                name=f'{source} {col2}',
                marker_color=colors.get(source, 'grey'),
                showlegend=True if i == 0 else False
            ), row=i + 1, col=1)

        figBarMin.update_layout(
            title='<b>Répartition des sources par jour</b>',
            yaxis=dict(title='Valeurs'),
            barmode='group',
            legend_title='Source',
            hovermode='x unified'
            # ,
            # height=800
        )
        # enlever les yaxis labels pour aucune source = 0
        # fig.update_yaxes(showticklabels=False, row=3, col=1)
        # ou :
        if inosource:
            figBarMin.update_yaxes(tickvals=[0, 0.5, 1], ticktext=["","0", ""],
                         row=inosource+1, col=1)

        # Mise à jour des axes y de chaque subplot
        for i in range(1, len(unique_sources) + 1):
            figBarMin.update_yaxes(title_text="Valeurs", row=i, col=1)
            if i != len(unique_sources):  # Remove x-axis labels for all but the bottom subplot
                figBarMin.update_xaxes(showticklabels=False, row=i, col=1)

        figBarMin.update_xaxes(range=[start_date, end_date])

        div_container.append(dcc.Graph(id='graph-XT_FinMin', figure=figBarMin,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(get_plotdesc(col1, col2),
                                          dangerously_allow_html=True))

        ###** graphe 5 : XT Fin - b) valeurs journalières

        df['day'] = pd.to_datetime(df[db_timecol]).dt.date
        #### barplot idem précédent mais par jour
        agg_df = df.groupby(['day', 'source']).size()
        wagg_df = agg_df.unstack(fill_value=0)
        pct_df = wagg_df.div(wagg_df.sum(axis=1), axis=0) * 100

        figBarDay = make_subplots(rows=2, cols=1, vertical_spacing=0.04,
                                  shared_xaxes=True)

        max_mean_col = pct_df.mean().idxmax()

        # s il n'y a qu un type -> np.min ne va pas marcher
        cut_int = [10,np.min(pct_df[max_mean_col]) - 0.5]
        # pour assurer qu elle soit plot en premier
        othercols = [x for x in colors.keys() if not x== max_mean_col]

        # Traces pour le second graphe (à partir de np.min(pct_df['Réseau']) - 10)
        for source in [max_mean_col]+othercols:
            if source in pct_df.columns:
                figBarDay.add_trace(go.Bar(
                    x=pct_df.index,
                    y=pct_df[source],
                    name=source,
                    marker_color=colors[source],
                    showlegend=False #if source == 'Réseau' else True
                ), row=2, col=1)
                figBarDay.add_trace(go.Bar(
                    x=pct_df.index,
                    y=pct_df[source],
                    name=source,
                    marker_color=colors[source],
                    showlegend=True# if source == 'Réseau' else True
                ), row=1, col=1)
        figBarDay.update_layout(
            title='<b>Répartition des sources par jour</b>',
            xaxis=dict(title='Jour'),
            barmode='stack',
            legend_title='Source',
            hovermode='x unified'
        )
        figBarDay.update_yaxes(range=[cut_int[1], 100], row=1, col=1)
        figBarDay.update_xaxes(visible=False, row=1, col=1,
                               range=[start_date, end_date]
                               )
        figBarDay.update_yaxes(range=[0, cut_int[0]], row=2, col=1)

        div_container.append(dcc.Graph(id='graph-XT_FinDay', figure=figBarDay,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(get_plotdesc(col1, col2),
                                          dangerously_allow_html=True))


    #### ajouter les variables I
        selected_db = dbDayI_name
        # queryI = get_query_extractInterval(selected_db, start_date, end_date)
        # conn = sqlite3.connect(db_file)
        # dayI_df = pd.read_sql_query(queryI, conn)
        # conn.close()

        dayI_df = day_db

        if selected_period != 'stat_perso':
            start_date, end_date = get_startrange_date_vLatest(dayI_df[db_daycol], selected_period)

        print(" nrow " + str(dayI_df.shape[0]))
        print('show first days dayI: ' + ','.join(dayI_df['day']))


        Ivars_toplot = [x for x in dayIcols_settings.keys() if
                        dayIcols_settings[x]["source"] == "XTender" and
                                    x in dayI_df.columns and
                                re.sub("_1|_2","" ,x) in IvarsOfInterset]

        dayI_df = dayI_df[[db_daycol] +Ivars_toplot]
        togroup = set([re.sub("_1|_2", "", x) for x in
                       dayI_df.columns if not x ==db_daycol])


        sumI_df = dayI_df[[db_daycol]].copy()
        for prefix in togroup:
            columns_to_sum = dayI_df.filter(like=prefix).columns
            sumI_df[prefix] = dayI_df[columns_to_sum].sum(axis=1)
        # Energie (bilan) sur l'entrée des 2 XT  (somme L1 * L2 I3081)
        # Energie (bilan) sur les sorties des 2 XT (somme L1 * L2 I3083)
        assert set(sumI_df.columns) == set( ['day', 'I3081', 'I3083'])
        data=sumI_df
        # Reshape le DataFrame en long format
        sumI_df_long = sumI_df.melt(id_vars=['day'], value_vars=['I3081', 'I3083'], var_name='variable', value_name='value')

        sumI_df_long['color'] = sumI_df_long['variable'].map(I_colors)

        # Créer le barplot
        fig = px.bar(sumI_df_long, x='day', y='value',
                     color='variable', barmode='group',
                     color_discrete_map=I_colors)

        fig.update_layout(
            title='<b>Comparaison des valeurs I3081 et I3083 par jour</b>',
            xaxis_title='Jour',
            yaxis_title='Valeurs (somme L1+L2)',
            hovermode='x unified'
        )
        fig.update_xaxes(range=[start_date, end_date])

        text_desc81 = get_plotdesc('I3081_1', col2='I3081_2',
                                 db=dbDayI_name, htmlFormat=True)
        text_desc83 = get_plotdesc('I3083_1', col2='I3083_2',
                                 db=dbDayI_name, htmlFormat=True)

        div_container.append(dcc.Graph(id='graph-XT_Ivars', figure=fig,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }))
        div_container.append(dcc.Markdown(text_desc81,
                                          dangerously_allow_html=True))
        div_container.append(dcc.Markdown(text_desc83,
                                          dangerously_allow_html=True))

        return [div_container, False, "", date_info]
