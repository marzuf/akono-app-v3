from settings import *
from utils_fcts import *
from dash.dependencies import ALL

def register_callbacks(app):

    ################################################################################################
    ################################ CALLBACKS SUBTAB DAHSBOARD
    ################################################################################################
    # Définir les callbacks pour mettre à jour le contenu des sous-onglets
    @app.callback(Output('subtabs-dashboard-content', 'children'),
                  [Input('subtabs-dashboard', 'value')])
    def render_subtab_dashboard_content(subtab):
        if subtab == 'subtab-minutesdata':
            return html.Div([
                html.H4("Données minutes"),
                get_period_dropdown('subminutesdashb-period-dropdown'),
                html.Button('Afficher', id='show-minutesdashb-btn', n_clicks=0),
                html.Div(id='subminutesdashb-range-info', style={'marginTop': '20px'}),
                html.Div(id='subtab-minutesdashb-content', style={'marginTop': '20px'}),
                get_modal_dashboard(id_mainDiv="graph-modal-minutesdashb",
                                    id_childDiv="modal-content-minutesdashb",
                                    id_closeBtn="close-modal-minutesdashb",
                                    id_graph="modal-graph-minutesdashb")
            ])
        elif subtab == 'subtab-dayIdata':
            return html.Div([
                html.H4("Données journalières I"),
                get_period_dropdown('subdayIdashb-period-dropdown'),
                html.Button('Afficher', id='show-dayIdashb-btn', n_clicks=0),
                html.Div(id='subdayIdashb-range-info', style={'marginTop': '20px'}),
                html.Div(id='subtab-dayIdashb-content', style={'marginTop': '20px'}),
                get_modal_dashboard(id_mainDiv="graph-modal-dayIdashb",
                                    id_childDiv="modal-content-dayIdashb",
                                    id_closeBtn="close-modal-dayIdashb",
                                    id_graph="modal-graph-dayIdashb")

            ])


    ######################################################################
    # NEW DASHBOARD minutesdata
    ######################################################################



    @app.callback(
        [Output('graph-modal-minutesdashb', 'style'),
         Output('modal-graph-minutesdashb', 'figure')],
        [Input({'type': 'dynamic-button', 'index': ALL}, 'n_clicks'),
         Input('close-modal-minutesdashb', 'n_clicks')],
        [State('graph-modal-minutesdashb', 'style'),
         State('store-summary-minutes', 'data'),
         State('store-dbTime_df', 'data')]
    )
    def toggle_modal_minutes(button_clicks, close_click, modal_style, summary_data_minutes, dbTime_df_data):
        print("BUTTON CLICKED******\n")

        ctx = dash.callback_context

        if not ctx.triggered:
            return {"display": "none"}, go.Figure()

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if 'dynamic-button' in triggered_id:
            # Trouver l'index du bouton qui a été cliqué
            triggered_index = eval(triggered_id)['index']
            column_name = summary_data_minutes[triggered_index]['Column']

            df = pd.DataFrame(dbTime_df_data)
            fig = go.Figure(
                data=[
                    go.Scatter(x=df['time'], y=df[column_name], mode='lines')
                ],
                layout=go.Layout(
                    title=f"Variation de {column_name} dans le temps",
                    xaxis_title="Time",
                    yaxis_title=column_name
                )
            )
            return {"display": "block"}, fig

        elif 'close-modal-minutesdashb' in triggered_id:
            return {"display": "none"}, go.Figure()

        return {"display": "none"}, go.Figure()

    @app.callback(
        [Output('subtab-minutesdashb-content', 'children'),
         Output('confirm-dialog-subminutes', 'displayed'),
         Output('confirm-dialog-subminutes', 'message'),
         Output('subminutesdashb-range-info', 'children'),
         Output('store-summary-minutes', 'data'),
         Output('store-dbTime_df', 'data')
         ],
        [Input('show-minutesdashb-btn', 'n_clicks')],
        [
         State('range-picker-subminutes', 'start_date'),
         State('range-picker-subminutes', 'end_date'),
            State('subminutesdashb-period-dropdown', 'value'),
            State('stored_timeDB', 'data')
        ]
    )
    def display_minutesdata_dashboard(n_clicks,start_date, end_date, selected_period, time_db):
        selected_db = dbTime_name
        dbTime_df = pd.DataFrame(time_db)
        selected_col = "FOO"
        if n_clicks is None or n_clicks == 0:
            return ["", False, "", "", None, None]

        if selected_period == "stat_perso" and (not start_date or not end_date):
            return ["", True, "Sélectionnez une période", "",None, None]

        if (not selected_db or not selected_col) :
            return ["", True, "Sélectionnez des données", "",None, None]

        if selected_period == "stat_perso":
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else :
            start_date, end_date = get_startrange_date_vLatest(dbTime_df[db_timecol], selected_period)


        date_info = f"Données du {start_date} au {end_date}"

        dbTime_df[db_timecol] = pd.to_datetime(dbTime_df[db_timecol])

        # Définir la plage complète de temps en minutes
        ## pour avoir de start date 00 et end date 2359
        start_date_minute = datetime.combine(start_date, datetime.min.time())
        end_date_minute = (datetime.combine(end_date, datetime.min.time())+
                           timedelta(days=1) - timedelta(minutes=1))

        all_minutes = pd.date_range(start=start_date_minute,
                                    end=end_date_minute, freq='min')
        missing_times = all_minutes.difference(dbTime_df[db_timecol])
        if not missing_times.empty:
            missing_data = pd.DataFrame(missing_times, columns=[db_timecol])
            dbTime_df = pd.concat([dbTime_df, missing_data],
                                  ignore_index=True).sort_values(by=db_timecol)
        ## assurer que c'est bien la colonne 'time' en position 0
        assert dbTime_df.columns[0] == db_timecol
        summary = pd.DataFrame({
            'Column': dbTime_df.columns[1:],  # Exclure la colonne 'time'
            'Minutes with Data': dbTime_df.iloc[:, 1:].notna().sum().values,
            'Minutes with Missing Data': (dbTime_df.iloc[:, 1:].isna().sum() +
                                          len(missing_times)).values
        })
        summary['Percentage Data'] = summary['Minutes with Data'] / (
                    summary['Minutes with Data'] + summary['Minutes with Missing Data']) * 100

        summary_data_minutes = summary.to_dict('records')
        dbTime_df_data = dbTime_df.to_dict('records')

        dbTime_df[db_timecol] = pd.to_datetime(dbTime_df[db_timecol])
        time_data = dbTime_df[db_timecol]

        div_container = [generate_header_row("minutes")]
        for i, row in summary.iterrows():
            sparkline_data = dbTime_df[row['Column']]
            div_container.append(
                generate_summary_row(
                    i,
                    row['Column'],
                    row['Minutes with Data'],
                    row['Minutes with Missing Data'],
                    sparkline_data,
                    time_data,
                    'dynamic-button'
                )
            )

        dbTime_df['day'] = dbTime_df[db_timecol].dt.date

        df_filtered = dbTime_df.dropna(how='all', axis=1)

        columns_to_check = df_filtered.columns.difference(['day',db_timecol])

        days_with_all_data_missing = df_filtered.groupby('day').apply(
            lambda x: x[columns_to_check].isna().all().all())

        days_with_partial_data_missing = df_filtered.groupby('day').apply(
            lambda x: x[columns_to_check].isna().any().any() and not
            x[columns_to_check].isna().all().all())

        days_with_no_data = days_with_all_data_missing[days_with_all_data_missing].index.tolist()
        days_with_no_data_df = pd.DataFrame(days_with_no_data, columns=['Days with No Data'])

        days_with_some_data_missing = days_with_partial_data_missing[days_with_partial_data_missing].index.tolist()
        days_with_some_data_missing_df = pd.DataFrame(days_with_some_data_missing,
                                                      columns=['Days with Some Data Missing'])

        div_container.append(html.H3("Days with No Data"))
        div_container.append(dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in days_with_no_data_df.columns],
            data=days_with_no_data_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'}
        ))
        div_container.append(html.H3("Days with Some Data Missing"))
        div_container.append(dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in days_with_some_data_missing_df.columns],
            data=days_with_some_data_missing_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'}
        ))
        return [div_container, False, "", date_info,summary_data_minutes, dbTime_df_data]

    ######################################################################
    # NEW DASHBOARD dayI data
    ######################################################################

    @app.callback(
        [Output('graph-modal-dayIdashb', 'style'),
         Output('modal-graph-dayIdashb', 'figure')],
        [Input({'type': 'dynamic-button-dayI', 'index': ALL}, 'n_clicks'),
         Input('close-modal-dayIdashb', 'n_clicks')],
        [State('graph-modal-dayIdashb', 'style'),
         State('store-summary-dayI', 'data'),
         # State('store-dbDayI_df', 'data'),
         State('stored_dayDB', 'data'),
         State('range-picker-subdayI', 'start_date'),
         State('range-picker-subdayI', 'end_date') ,
         State('subdayIdashb-period-dropdown', 'value'),
         ]
    )
    def toggle_modal_dayI(button_clicks, close_click, modal_style, summary_data_dayI, dayI_df_data,
                          start_date, end_date, dayI_period):

        print("BUTTON CLICKED dayI******\n")

        ctx = dash.callback_context

        if not ctx.triggered:
            return {"display": "none"}, go.Figure()

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if 'dynamic-button-dayI' in triggered_id:
            # Trouver l'index du bouton qui a été cliqué
            triggered_index = eval(triggered_id)['index']
            column_name = summary_data_dayI[triggered_index]['Column']
            print("column name = " + column_name)

            df = pd.DataFrame(dayI_df_data)


            if not dayI_period :
                return {"display": "none"}, go.Figure()

            if dayI_period == "stat_perso" and (not start_date or not end_date):
                return {"display": "none"}, go.Figure()

            if dayI_period == "stat_perso":
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                start_date, end_date = get_startrange_date_vLatest(df[db_daycol], dayI_period)


            col_lab = dayIcols_settings[column_name]['lab']

            print("all cols = " + ','.join(df.columns))
            fig = go.Figure(
                data=[
                    go.Scatter(x=df[db_daycol], y=df[column_name], mode='lines')
                ],
                layout=go.Layout(
                    title=f"{column_name} (" + col_lab + ")",
                    xaxis_title="Time",
                    yaxis_title=col_lab
                )
            )

            if start_date and end_date:
                fig.update_xaxes(range=[start_date, end_date])

            return {"display": "block"}, fig

        elif 'close-modal-dayIdashb' in triggered_id:
            return {"display": "none"}, go.Figure()

        return {"display": "none"}, go.Figure()

    @app.callback(
        [Output('subtab-dayIdashb-content', 'children'),
         Output('confirm-dialog-subdayI', 'displayed'),
         Output('confirm-dialog-subdayI', 'message'),
         Output('subdayIdashb-range-info', 'children'),
         Output('store-summary-dayI', 'data'),

         ],
        [Input('show-dayIdashb-btn', 'n_clicks')],
        [
         State('range-picker-subdayI', 'start_date'),
         State('range-picker-subdayI', 'end_date'),
            State('subdayIdashb-period-dropdown', 'value'),
            State('stored_dayDB', 'data')
        ]
    )
    def display_dayIdata_dashboard(n_clicks,start_date, end_date, selected_period, day_db):
        selected_db = dbDayI_name
        dbDayI_df=pd.DataFrame(day_db)

        selected_col = "FOO"
        if n_clicks is None or n_clicks == 0:
            return ["", False, "", "", None, None]

        if not selected_db or not selected_col:
            return ["", True, "Sélectionnez des données", "", None, None]

        if selected_period == "stat_perso" and (not start_date or not end_date):
            return ["", True, "Sélectionnez une période", "",None, None]

        if selected_period == "stat_perso":
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else :
            start_date, end_date = get_startrange_date_vLatest(dbDayI_df[db_daycol], selected_period)

        date_info = f"Données du {start_date} au {end_date}"

        # conn = sqlite3.connect(db_file)
        # dbDayI_df = pd.read_sql_query(query, conn)
        # conn.close()

        ####
        dbDayI_df[db_daycol] = pd.to_datetime(dbDayI_df[db_daycol])
        filtered_df = dbDayI_df[(dbDayI_df[db_daycol] >= pd.to_datetime(start_date)) &
                                (dbDayI_df[db_daycol] <= pd.to_datetime(end_date))]
        dbDayI_df = filtered_df

        all_days = pd.date_range(start=start_date,
                                 end=end_date)
        missing_days = all_days.difference(dbDayI_df[db_daycol])
        if not missing_days.empty:
            missing_data = pd.DataFrame(missing_days, columns=[db_daycol])
            dbDayI_df = pd.concat([dbDayI_df, missing_data],
                                  ignore_index=True).sort_values(by=db_daycol)

        ## assurer que c'est bien la colonne 'time' en position 0
        assert dbDayI_df.columns[0] == db_daycol
        # Calcul du nombre de minutes avec des données et des données manquantes pour chaque colonne
        summary = pd.DataFrame({
            'Column': dbDayI_df.columns[1:],  # Exclure la colonne 'day'
            'Jours avec données': dbDayI_df.iloc[:, 1:].notna().sum().values,
            'Jours sans données': (dbDayI_df.iloc[:, 1:].isna().sum() +
                                          len(missing_days)).values
        })

        summary['Pourcentage Data'] = summary['Jours avec données'] / (
                    summary['Jours avec données'] + summary['Jours sans données']) * 100

        summary_data_dayI = summary.to_dict('records')
        dbDayI_df_data = dbDayI_df.to_dict('records')

        dbDayI_df[db_daycol] = pd.to_datetime(dbDayI_df[db_daycol])
        time_data = dbDayI_df[db_daycol]

        div_container = [generate_header_row("jours")]
        for i, row in summary.iterrows():
            sparkline_data = dbDayI_df[row['Column']]
            div_container.append(
                generate_summary_row(
                    i,
                    row['Column'],
                    row['Jours avec données'],
                    row['Jours sans données'],
                    sparkline_data,
                    time_data,
                    'dynamic-button-dayI'
                )
            )

        dbDayI_df['day'] = dbDayI_df[db_daycol].dt.date

        df_filtered = dbDayI_df.dropna(how='all', axis=1)
        columns_to_check = df_filtered.columns.difference(['day',db_daycol])
        days_with_all_data_missing = df_filtered.groupby('day').apply(
            lambda x: x[columns_to_check].isna().all().all())
        days_with_partial_data_missing = df_filtered.groupby('day').apply(
            lambda x: x[columns_to_check].isna().any().any() and not
            x[columns_to_check].isna().all().all())

        days_with_no_data = days_with_all_data_missing[days_with_all_data_missing].index.tolist()
        days_with_no_data_df = pd.DataFrame(days_with_no_data, columns=['Jours sans données'])

        days_with_some_data_missing = days_with_partial_data_missing[days_with_partial_data_missing].index.tolist()
        days_with_some_data_missing_df = pd.DataFrame(days_with_some_data_missing,
                                                      columns=['Jours avec données partielles'])

        div_container.append(html.H3("Jours sans données"))
        div_container.append(dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in days_with_no_data_df.columns],
            data=days_with_no_data_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'}
        ))
        div_container.append(html.H3("Jours avec données partielles"))
        div_container.append(dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in days_with_some_data_missing_df.columns],
            data=days_with_some_data_missing_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'}
        ))
        return [div_container, False, "", date_info,summary_data_dayI, dbDayI_df_data]
