import sys

from dash.dependencies import Input, Output
from settings import *
from utils_fcts import *
import plotly.express as px

def register_callbacks(app):

    # dayPdata_columns = get_daydata_columns("P")
    # dayIdata_columns = get_daydata_columns("I")
    # timedata_columns = get_timedata_columns()
    timecols2show = list(showcols_settings.keys())#x for x in timedata_columns if not showcols_settings[x] == "NA"]
    # dayPcols2show = [x for x in dayPdata_columns if not x == db_daycol]
    dayIcols2show = list(dayIcols_settings.keys())#[x for x in dayIdata_columns if not x == db_daycol]


    ################################################################################################
    ################################ CALLBACKS - TAB EVOTIME - VISUALISATIONS   tab-evotime
    ################################################################################################

    # callback pour vérifier le nombre de variables sélectionnées et afficher la pop-up :
    @app.callback(
        [Output('confirm-dialog-evotime', 'displayed'),
         Output('evotimeTimeDB-graph-col', 'value')],
        [Input('evotimeTimeDB-graph-col', 'value')]
    )
    def limit_selection_evotimedata(selected_columns):
        if selected_columns :
            if len(selected_columns) > maxTimePlotVar:
                return True, selected_columns[:maxTimePlotVar]  # Afficher la pop-up et limiter la sélection à 2
        return False, selected_columns  # Ne pas afficher la pop-up


    @app.callback(
        Output('evotimeTimeDB-graph-varinfo', 'children'),
        [Input('evotimeTimeDB-graph-col', 'value')]
    )
    def update_evotimevarinfo(selected_col, selected_db=dbTime_name):
        if selected_col and selected_db:
            desc_txt = get_var_desc(selected_col, selected_db)
        else:
            return None
        return html.Div([dcc.Markdown(desc_txt,
                                      dangerously_allow_html=True)])

    # Callback pour afficher le graphique en fonction de la sélection :
    @app.callback(
        [Output('evotimeTimeDB-graph', 'figure'),
         Output('confirm-dialog-evoTimeDBgraph', 'displayed'),
         Output('confirm-dialog-evoTimeDBgraph', 'message')],
        [Input('show-evotimeTimeDBgraph-btn', 'n_clicks')],
        [State('evotimeTimeDB-db', 'value'),
         State('evotimeTimeDB-graph-col', 'value'),
         State('evotimeTimeDB-graph-viz', 'value'),
         State('evotimeperiod-dropdown', 'value'),
         State('range-picker-evotime', 'start_date'),
         State('range-picker-evotime', 'end_date'),
         State('stored_timeDB', 'data'),
         State('stored_dayDB', 'data')]
    )
    def display_timeevolution_graph(n_clicks, selected_db, selected_col, selected_viz,
                           selected_period, start_date, end_date, time_db, day_db):
        if n_clicks is None or n_clicks == 0:
            return [go.Figure(), False, ""]

        if (not selected_db or not selected_col or not selected_viz) :
            return [go.Figure(), True, "Sélectionnez des données"]

        if selected_db == dbTime_name:
            df = pd.DataFrame(time_db)
            dfcol = db_timecol
        elif selected_db == dbDayI_name:
            df = pd.DataFrame(day_db)
            dfcol = db_daycol
        else:
            sys.exit(1)

        if selected_period == "stat_perso" and (not start_date or not end_date):
          return [go.Figure(), True, "Sélectionnez une date de début et fin"]

        if selected_period == "stat_perso":
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start_date, end_date = get_startrange_date_vLatest(df[dfcol], selected_period)


        if selected_db == dbTime_name:
            xcol = db_timecol
            assert db_daycol != db_timecol
            df[db_daycol] = pd.to_datetime(df[xcol]).dt.date
            colsettings = showcols_settings
        else:
            xcol = db_daycol
            if selected_db == dbDayI_name:
                colsettings = dayIcols_settings
                for col in dayI_cols:
                    df[col] = df[col + "_1"].fillna(0) + df[col + "_2"].fillna(0)

        if selected_viz == "boxplot" and isinstance(selected_col, list) and len(selected_col) > 1:
            df_melted = pd.melt(df, id_vars=[db_daycol], value_vars=selected_col,
                                var_name='variable', value_name='valeur')



            # Créer le boxplot avec des couleurs différentes pour chaque variable
            fig = px.box(df_melted, x=db_daycol, y='valeur', color='variable',
                         title=f'Box Plot par jour pour {selected_col}',
                         labels={'valeur': 'Nouvelle Étiquette Y'} )

        # if selected_db == dbTime_name and selected_viz == 'boxplot':
        #     fig = px.box(df, x='date', y=selected_col, title=f'{selected_col} Box Plot par jour')
        else:
            if selected_viz == 'lineplot':
                # fig = px.line(df, x=xcol, y=selected_col, title=f'{selected_col} Line Plot')

                # Lire toutes les données de la base de données
                # df = fetch_timedata()
                fig = go.Figure()
                for i, col in enumerate(selected_col):
                    # Ajout de chaque variable sur un axe y différent
                    fig.add_trace(
                        go.Scatter(
                            x=df[xcol],
                            y=df[col],
                            mode='lines',
                            name=col,
                            yaxis=f'y{i + 1}'

                        )
                    )
                update_layout_cols(selected_col)
                yaxis_layout['title'] = colsettings[selected_col[0]]['lab']
                fig.update_layout(
                    xaxis=dict(domain=[0.25, 0.75], showline=True, linewidth=2, linecolor='black'),
                    yaxis=yaxis_layout,
                    yaxis2=yaxis2_layout,
                    yaxis3=yaxis3_layout,
                    yaxis4=yaxis4_layout,
                    title_text="",  ## titre en-haut à gauche
                    margin=dict(l=40, r=40, t=40, b=30)
                )

            elif selected_viz == 'barplot':
                fig = px.bar(df, x=xcol, y=selected_col, title=f'{selected_col} Bar Plot')
                fig.update_layout(barmode='group')
            elif selected_viz == 'boxplot':
                fig = px.box(df, x=xcol, y=selected_col, title=f'{selected_col} Box Plot')

        fig.update_layout(xaxis=xaxis_settings)

        if start_date and end_date:
            fig.update_xaxes(range=[start_date, end_date])

        return [fig, False, ""]



    @app.callback(
        Output('evotimeTimeDB-graph-viz', 'options'),
        [Input('evotimeTimeDB-db', 'value')]
    )
    def update_evotimeviz_options(selected_db):
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

    ################################ CALLBACKS - TAB STAT - VISUALISATION
    # Callback pour mettre à jour les colonnes disponibles en fonction de la table sélectionnée :
    @app.callback(
        Output('evotimeTimeDB-graph-col', 'options'),
        [Input('evotimeTimeDB-db', 'value')]
    )
    def update_evotime_columns(selected_db):
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




    ##################################################################################
    ####################### Callback pour actualiser les DatePickerRange #############
    ##################################################################################

    # [Output('evotimeTimeDB-graph', 'figure'),
    #  Output('confirm-dialog-evoTimeDBgraph', 'displayed'),
    #  Output('confirm-dialog-evoTimeDBgraph', 'message')],
    # [Input('show-evotimeTimeDBgraph-btn', 'n_clicks')],
    # [State('evotimeTimeDB-db', 'value'),
    #  State('evotimeTimeDB-graph-col', 'value'),
    #  State('evotimeTimeDB-graph-viz', 'value'),
    #  State('evotimeperiod-dropdown', 'value'),
    #  State('range-picker-evotime', 'start_date'),
    #  State('range-picker-evotime', 'end_date'),
    #  State('stored_timeDB', 'data'),
    #  State('stored_dayDB', 'data')]

    # my_pickers=['range-picker-evotime']
    # @app.callback(
    #     [Output(picker_id, 'min_date_allowed') for picker_id in my_pickers] +
    #     [Output(picker_id, 'max_date_allowed') for picker_id in my_pickers] +
    #     [Output(picker_id, 'disabled_days') for picker_id in my_pickers],
    #     [Input('stored_timeDB', 'data'),
    #      Input('stored_dayDB', 'data')],
    #      [State('evotimeTimeDB-db', 'value')]
    # )
    # def update_date_picker_ranges(stored_timeDB_data, stored_dayDB_data, selected_db):
    #     if selected_db == dbTime_name :
    #         if  stored_timeDB_data:
    #             time_df = pd.DataFrame(stored_timeDB_data)
    #             min_date = time_df[dbTime_name].min()
    #             max_date = time_df[dbTime_name].max()
    #             disabled_days = pd.date_range(min_date, max_date).difference(
    #                 time_df[dbTime_name]).to_list()
    #         else:
    #             min_date, max_date, disabled_days = None, None, []
    #
    #     elif selected_db == dbDayI_name:
    #         if stored_dayDB_data:
    #             day_df = pd.DataFrame(stored_dayDB_data)
    #             min_date = day_df[db_daycol].min()
    #             max_date = day_df[db_daycol].max()
    #             disabled_days = pd.date_range(min_date, max_date).difference(
    #                 day_df[db_daycol]).to_list()
    #         else:
    #             min_date, max_date, disabled_day_days = None, None, []
    #     else:
    #         sys.exit(1)
    #     # Renvoie les valeurs mises à jour pour tous les DatePickerRange
    #     return (
    #         [min_date] * len(my_pickers),  # Min date for all pickers
    #         [max_date] * len(my_pickers),  # Max date for all pickers
    #         [disabled_days] * len(my_pickers)  # Disabled days for all pickers
    #     )