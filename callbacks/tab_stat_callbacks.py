import sys

import pandas as pd
from dash.dependencies import Input, Output
from settings import *
from utils_fcts import *
from app_settings import *
import plotly.express as px



def register_callbacks(app):
    ############################### ###############################
    ############################### CALL BACKS STAT tab-stat
    ############################### ###############################
    #
    # dayPdata_columns = get_daydata_columns("P")
    # dayIdata_columns = get_daydata_columns("I")
    # timedata_columns = get_timedata_columns()
    # timecols2show = [x for x in timedata_columns if not showcols_settings[x] == "NA"]
    # dayPcols2show = [x for x in dayPdata_columns if not x == db_daycol]
    # dayIcols2show = [x for x in dayIdata_columns if not x == db_daycol]

    timecols2show = list(showcols_settings.keys())#x for x in timedata_columns if not showcols_settings[x] == "NA"]
    dayIcols2show = list(dayIcols_settings.keys())#[x for x in dayIdata_columns if not x == db_daycol]



    @app.callback(
        [
            Output('stat-range-info', 'children'),
            Output('confirm-dialog-stat', 'displayed'),
            Output('confirm-dialog-stat', 'message'),
            Output('stat-means-info', 'children')
        ],
        [Input('show-stat-btn', 'n_clicks')],
        [
            State('statperiod-dropdown', 'value'),
            State('range-picker-stat', 'start_date'),
            State('range-picker-stat', 'end_date'),
            State('stored_timeDB', 'data'),
            State('stored_dayDB', 'data')
        ]
    )
    def update_stat_values(n_clicks, selected_period, start_date, end_date, time_db, day_db):
        if n_clicks is None or n_clicks == 0:
            return ["", False, "", ""]

        if selected_period == "stat_perso" and (not start_date or not end_date):
            return ["", True, "Sélectionnez une période", ""]

        df_time = pd.DataFrame(time_db)
        df_dayI = pd.DataFrame(day_db)

        if selected_period == "stat_perso":
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else :
            start_date1, end_date1 = get_startrange_date_vLatest(df_time[db_timecol], selected_period)
            start_date2, end_date2 = get_startrange_date_vLatest(df_dayI[db_daycol], selected_period)
            start_date= min(start_date1,start_date2)
            end_date = max(end_date1, end_date2)


        means_html = html.Div([
            create_section("Moyennes des données minutes",
                           df_time.mean(numeric_only=True)),
            # create_section("Moyennes des données journalières (P)",
            #                df_dayP.mean(numeric_only=True)),
            create_section("Moyennes des données journalières (I)",
                           df_dayI.mean(numeric_only=True))
        ])
        date_info = f"Données du {start_date} au {end_date}"
        return [date_info, False, "", means_html]




    ################################ CALLBACKS - TAB STAT - VISUALISATION
    # Callback pour mettre à jour les colonnes disponibles en fonction de la table sélectionnée :
    @app.callback(
        Output('tabstatgraph-col', 'options'),
        [Input('tabstatgraph-db', 'value')]
    )
    def update_stat_columns(selected_db):
        if selected_db:
            if selected_db == dbTime_name:
                columns = [{'label': col, 'value': col} for col in timecols2show]
            # elif selected_db == dbDayP_name:
            #     columns = [{'label': col, 'value': col} for col in dayPcols2show]
            elif selected_db == dbDayI_name:
                columns = [{'label': col, 'value': col} for col in dayI_cols + dayIcols2show]
            else:
                sys.exit(1)
            return columns
        return []


    # Callback pour mettre à jour texte info var

    @app.callback(
        Output('tabstatgraph-varinfo', 'children'),
        [Input('tabstatgraph-col', 'value')],
        [State('tabstatgraph-db', 'value')]
    )
    def update_statvarinfo(selected_col, selected_db):
        if selected_col and selected_db:
            if selected_db == dbTime_name:
                desc_txt = "<b>" + selected_col + "</b> : " + \
                           showcols_settings[selected_col]['description']
            # elif selected_db == dbDayP_name:
            #     desc_txt = "<b>" + selected_col + "</b> : " + \
            #                dayPcols_settings[selected_col]['description']
            elif selected_db == dbDayI_name:
                desc_txt = "<b>" + selected_col + "</b> : " + \
                           dayIcols_settings[selected_col]['description']
            else:
                sys.exit(1)
                return None
            return html.Div([dcc.Markdown(desc_txt,
                                          dangerously_allow_html=True)])
        return None



    # Callback pour gérer l'ouverture et la fermeture de la modale, et l'affichage du graphique
    @app.callback(
        [Output('stat-modal-graph-modal', 'is_open'),
         Output('stat-modal-graph', 'figure')],
        [Input('stat-graph', 'clickData'),
         Input('close-modal-stat', 'n_clicks')],
        [State('stat-modal-graph-modal', 'is_open'),
         State('stat-graph', 'figure')],
        prevent_initial_call=True
    )
    def toggle_modal_stat(clickData, n_clicks, is_open, myfig):
        ctx = dash.callback_context

        if ctx.triggered and ctx.triggered[0]['prop_id'] == 'close-modal.n_clicks':
            return False, go.Figure()  # Fermer la modale

        if clickData:
            return True, myfig  # Ouvrir la modale avec le graphique

        return is_open, go.Figure()  # Ne change rien si aucun événement n'est détecté

    # Callback pour afficher le graphique en fonction de la sélection :
    @app.callback(
        [Output('stat-graph', 'figure'),
         Output('confirm-dialog-statgraph', 'displayed'),
         Output('confirm-dialog-statgraph', 'message')],
        [Input('show-statgraph-btn', 'n_clicks')],
        [State('tabstatgraph-db', 'value'),
         State('tabstatgraph-col', 'value'),
         State('tabstatgraph-viz', 'value'),
    State('statperiod-dropdown', 'value'),
         State('range-picker-stat', 'start_date'),
         State('range-picker-stat', 'end_date'),
         State('stored_timeDB', 'data'),
         State('stored_dayDB', 'data')
         ]
    )
    def display_stat_graph(n_clicks, selected_db, selected_col, selected_viz,
                      selected_period, start_date, end_date, time_db, day_db):
        if n_clicks is None or n_clicks == 0:
            return [go.Figure(), False, ""]

        if not selected_db or not selected_col or not selected_viz:
            return [go.Figure(), True, "Sélectionnez des données et une période"]

        if selected_period == "stat_perso" and (not start_date or not end_date):
            return [go.Figure(), True, "Sélectionnez une période"]

        if selected_db == dbTime_name:
            df = pd.DataFrame(time_db)
        elif selected_db == dbDayI_name:
            df = pd.DataFrame(day_db)
        else:
            sys.exit(1)

        if selected_period == "stat_perso" :
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start_date, end_date = get_startrange_date_vLatest(df[db_timecol], selected_period)

        if selected_db == dbTime_name:
            xcol = db_timecol
        else:
            xcol = db_daycol
            if selected_db == dbDayI_name:
                for col in dayI_cols:
                    df[col] = df[col + "_1"].fillna(0) + df[col + "_2"].fillna(0)

        if selected_db == dbTime_name and selected_viz == 'boxplot':
            df['date'] = pd.to_datetime(df[xcol]).dt.date
            fig = px.box(df, x='date', y=selected_col, title=f'{selected_col} Box Plot par jour')
        else:
            if selected_viz == 'lineplot':
                fig = px.line(df, x=xcol, y=selected_col, title=f'{selected_col} Line Plot')
            elif selected_viz == 'barplot':
                fig = px.bar(df, x=xcol, y=selected_col, title=f'{selected_col} Bar Plot')
            elif selected_viz == 'boxplot':
                fig = px.box(df, x=xcol, y=selected_col, title=f'{selected_col} Box Plot')

        if (selected_db == dbTime_name and selected_viz == 'boxplot') or (
                selected_db == dbDayP_name or selected_db == dbDayI_name):
            fig.update_layout(xaxis=dict(title='Date', tickformat='%Y-%m-%d', dtick="D1"))

        fig.update_layout(xaxis=xaxis_settings)


        return [fig, False, ""]

    @app.callback(
        Output('tabstatgraph-viz', 'options'),
        [Input('tabstatgraph-db', 'value')]
    )
    def update_viz_options(selected_db):
        if selected_db == dbTime_name:
            return [
                {'label': 'Line Plot', 'value': 'lineplot'},
                {'label': 'Bar Plot', 'value': 'barplot'},
                {'label': 'Box Plot', 'value': 'boxplot'}
            ]
        else:
            return [
                {'label': 'Line Plot', 'value': 'lineplot'},
                {'label': 'Bar Plot', 'value': 'barplot'}
            ]


