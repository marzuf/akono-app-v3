from dash.dependencies import Input, Output
from settings import *
from utils_fcts import *
import plotly.express as px


def register_callbacks(app):
    ##################################################################################
    ######################################### CALL BACK tab analyse GRAPH
    ##################################################################################
    # @app.callback(
    #     [Output('confirm-dialog-daydataP', 'displayed'),
    #      Output('dayPdata-column-dropdown', 'value')],
    #     [Input('dayPdata-column-dropdown', 'value')]
    # )
    # def limit_selection_dayPdata(selected_columns):
    #     if len(selected_columns) > maxTimePlotVar:
    #         return True, selected_columns[:maxTimePlotVar]  # Afficher la pop-up et limiter la sélection à 2
    #     return False, selected_columns  # Ne pas afficher la pop-up
    #
    # @app.callback(
    #     [Output('confirm-dialog-daydataI', 'displayed'),
    #      Output('dayIdata-column-dropdown', 'value')],
    #     [Input('dayIdata-column-dropdown', 'value')]
    # )
    # def limit_selection_dayIdata(selected_columns):
    #     if len(selected_columns) > maxTimePlotVar:
    #         return True, selected_columns[:maxTimePlotVar]  # Afficher la pop-up et limiter la sélection à 2
    #     return False, selected_columns  # Ne pas afficher la pop-up
    #
    # @app.callback(
    #     Output('dayPdata-column-description', 'children'),
    #     [Input('dayPdata-column-dropdown', 'value')]
    # )
    # def update_dayP_description(selected_columns):
    #     if selected_columns:
    #         desc_txt = '<br>'.join(["<b>" + selcol + "</b> : " + \
    #                                 dayPcols_settings[selcol]['description']
    #                                 for selcol in selected_columns])
    #         return html.Div([dcc.Markdown(desc_txt,
    #                                       dangerously_allow_html=True)])
    #     return html.P('No column selected')
    #
    # @app.callback(
    #     Output('dayIdata-column-description', 'children'),
    #     [Input('dayIdata-column-dropdown', 'value')]
    # )
    # def update_dayI_description(selected_columns):
    #     if selected_columns:
    #         # print(';'.join(showcols_settings.keys()))
    #         desc_txt = '<br>'.join(["<b>" + selcol + "</b> : " + \
    #                                 dayIcols_settings[selcol]['description']
    #                                 for selcol in selected_columns])
    #         return html.Div([dcc.Markdown(desc_txt,
    #                                       dangerously_allow_html=True)])
    #     return html.P('No column selected')

    @app.callback(
        [
            Output('analyseGraph-pie-chart-global', 'children'),
            Output('analyseGraph-pie-chart-day', 'children'),
            Output('analyseGraph-pie-chart-night', 'children'),
            Output('analyseGraph-period-subtit', 'children'),
            Output('analyseGraph-pie-chart-tit', 'children'),
            Output('analyseGraph-tempbat-barplot', 'children'),
            Output('confirm-dialog-analyseGraph', 'displayed'),
            Output('confirm-dialog-analyseGraph', 'message')
        ],
        [Input('show-asGraph-btn', 'n_clicks')],
        [
            State('asGraphPeriod-dropdown', 'value'),
            State('asL-dropdown', 'value'),
            State('range-picker-analyseGraph', 'start_date'),
            State('range-picker-analyseGraph', 'end_date'),
            State('stored_timeDB', 'data')
        ]
    )
    def update_analyse_pie_chart(n_clicks, selected_period, selected_L,
                                 start_date, end_date, time_db):
        if n_clicks is None or n_clicks == 0:
            return [""] * 6 + [False, ""]

        if selected_period == 'stat_perso' and (not start_date or not end_date):
            return [""] * 6 + [True, "Sélectionnez une période"]

        df = pd.DataFrame(time_db)

        if selected_period != 'stat_perso':
            start_date, end_date = get_startrange_date_vLatest(df[db_timecol], selected_period)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if selected_period == 'stat_all':
            interval_txt = " Toutes les données"
        else:
            interval_txt = ("Période : " + start_date.strftime('%d/%m/%Y') + " - " +
                            end_date.strftime('%d/%m/%Y'))

        if selected_L == "as_L1":
            df['calc_col'] = df[xtfincol + '_L1']
            calcol_txt = xtfincol + '_L1'
        elif selected_L == "as_L2":
            df['calc_col'] = df[xtfincol + '_L2']
            calcol_txt = xtfincol + '_L2'
        elif selected_L == "as_both":
            df['calc_col'] = df[xtfincol + '_L1'] + df[xtfincol + '_L2']
            calcol_txt = xtfincol + '_L1' + "+" + xtfincol + '_L2'
        else:
            exit(1)
        pie_chart_tit = html.Div([
            html.H4("Répartition fréquences (" + calcol_txt + ")"),
            html.H6("(génératrice si > " + str(xtfin_genThresh) +
                    " ; ni gén. ni rés. si = " + str(xtfin_nosource) + ")")

        ])
        period_subtit = html.H6(interval_txt)
        df['freq_type'] = np.where(df['calc_col'] > xtfin_genThresh,
                                   "génératrice", "réseau")
        df.loc[df['calc_col'] == xtfin_nosource, 'freq_type'] = "ni gén. ni rés."
        # ******* GLOBAL
        freq_counts = df['freq_type'].value_counts(normalize=True) * 100
        fig_global = px.pie(
            names=freq_counts.index,
            values=freq_counts.values,
            # title="Répartition des fréquences " + interval_txt + " (Global)"
            title="Global"
        )
        # ******* JOUR
        df_day = df[(pd.to_datetime(df[db_timecol]).dt.time >=
                     datetime.strptime("08:00", "%H:%M").time()) &
                    (pd.to_datetime(df[db_timecol]).dt.time <
                     datetime.strptime("18:00", "%H:%M").time())]
        freq_counts_day = df_day['freq_type'].value_counts(normalize=True) * 100
        fig_day = px.pie(
            names=freq_counts_day.index,
            values=freq_counts_day.values,
            # title="Répartition des fréquences "  + interval_txt + " (Jour : 08:00 - 18:00)",
            title="Jour : 08:00 - 18:00"
        )
        # ******* NUIT
        df_night = df[(pd.to_datetime(df[db_timecol]).dt.time >=
                       datetime.strptime("18:00", "%H:%M").time()) |
                      (pd.to_datetime(df[db_timecol]).dt.time <
                       datetime.strptime("08:00", "%H:%M").time())]
        assert df.shape[0] == (df_night.shape[0] + df_day.shape[0])
        freq_counts_night = df_night['freq_type'].value_counts(normalize=True) * 100
        fig_night = px.pie(
            names=freq_counts_night.index,
            values=freq_counts_night.values,
            # title="Répartition des fréquences " +  interval_txt + " (Nuit : 18:00 - 08:00)"
            title="Nuit : 18:00 - 08:00"
        )
        #### calcul des moyennes températures batterie
        barplot_data = pd.DataFrame({
            'Période': ['Global', 'Jour', 'Nuit'],
            'Moyenne Temp': [df[tempTbatcol].mean(),
                             df_day[tempTbatcol].mean(),
                             df_night[tempTbatcol].mean()]
        })
        fig_barplot = px.bar(barplot_data, x='Période', y='Moyenne Temp', title='Moyenne de TempTbatcol')

        fig_barplot.update_xaxes(range=[start_date, end_date])

        return [dcc.Graph(figure=fig_global,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }),
                dcc.Graph(figure=fig_day,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }),
                dcc.Graph(figure=fig_night,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }),
                period_subtit,
                pie_chart_tit,
                dcc.Graph(figure=fig_barplot,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    }),
                False, ""]
