
import sys
from dash.dependencies import Input, Output
from settings import *
from utils_fcts import *
from app_settings import *

def register_callbacks(app):


    ################################################################################################
    ################################ CALLBACKS SUBTAB data
    ################################################################################################
    # Définir les callbacks pour mettre à jour le contenu des sous-onglets
    @app.callback(Output('subtabs-data-content', 'children'),
                  [Input('subtabs-data', 'value'),
                   Input('date-picker-dbdata', 'date'),
                   # State('stored_dayDB', 'data'),
                   State('stored_timeDB', 'data'),
                   State('stored_dayDB', 'data')
                   ])
    def render_subtab_data_content(subtab, picked_date, time_db, day_db):
        all_dates = list(set(day_db[db_daycol]))

        if subtab == 'subtab-updateDB':
            return html.Div([
                html.H3('Gérer les données'),
                html.H4('Ajout de données à partir de fichier(s)'),
                dcc.Upload(
                    id='upload-data',
                    children=html.Button('Upload Files'),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=True  # Allow multiple files to be uploaded
                ),
                html.Div(id='output-upload'),
                html.H4('Suppression de données'),
                dcc.DatePickerSingle(
                    id='date-picker-delete',
                    date=None,
                    display_format='DD.MM.YYYY',
                    # min_date_allowed=min(fetch_timedata_dates()),
                    # min_date_allowed=min(all_dates),
                    # max_date_allowed=max(all_dates),
                    # disabled_days=[pd.to_datetime(date).date() for date in
                    #                pd.date_range(start=min(all_dates),
                    #                              end=max(all_dates)).
                    #                difference(pd.to_datetime(all_dates))]
                ),
                html.Button('Supprimer les données', id='delete-button', n_clicks=0),
                html.Div(id='output-delete')
            ])

        elif subtab == 'subtab-showDB':
            df = time_db
            if picked_date:
                picked_df = df
            else:
                picked_df = pd.DataFrame(columns=["Aucun jour sélectionné"])
            # Convertir les données en tableau interactif DataTable
            data_table_all = dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': col, 'id': col} for col in df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
            data_table_selected = dash_table.DataTable(
                data=picked_df.to_dict('records'),
                columns=[{'name': col, 'id': col} for col in picked_df.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
            # Nouvelle section pour afficher le nombre de jours disponibles
            all_entries = time_db[db_timecol]
            num_entries = len(all_entries)
            print(all_entries[0])
            all_days = set([datetime.strptime(x,
                                              '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') for
                            x in all_entries])

            num_days = len(all_days)
            nb_entries = html.Div([
                html.H6(f'Nombre d\'entrées dans la base de données : {num_entries}')
            ])
            nb_days = html.Div([
                html.H6(f'Nombre de jours dans la base de données : {num_days}')
            ])
            return html.Div([
                html.Div(id='datepicker-container'),
                html.H3('Données pour le jour sélectionné'),
                data_table_selected,
                html.H3('Aperçu de la base de données'),
                data_table_all,
                nb_entries,
                nb_days
            ])
        elif subtab == 'subtab-exportDB':
            return html.Div([
                html.H3('Exporter des données'),
                html.H4('Exporter tableaux de données pour une certaine période'),
                get_period_dropdown('exportdata-period-dropdown'),
                get_db_dropdown(id='exportdata-db'),
                html.Button('Exporter', id='exportdata-btn', n_clicks=0),
                dcc.Download(id='dwd-exportdata-xlsx'),
                html.Div(id='exportdata-info', style={'marginTop': '20px'}),
                html.H4('Exporter la base de données (fichier .db)'),
                html.Div([
                    dbc.Button("Télécharger la base de données", id="download-button", color="primary",
                               className="mr-2",
                               href="https://huggingface.co/spaces/mzuer/akono-app/resolve/main/"+db_file,
                               #ttps: // huggingface.co / spaces / mzuer / akono - app / resolve / main / data / akonolinga_database_v2.db
                               download=db_file)
                ], style={'textAlign': 'center', 'marginTop': '50px'})
                ])
    ### exporter les données
    # Callback pour afficher le graphique en fonction de la sélection :
    @app.callback(
        [Output('dwd-exportdata-xlsx', 'data'),
               # Output('exportdata-info', 'figure'),
         Output('confirm-dialog-exportdata', 'displayed'),
         Output('confirm-dialog-exportdata', 'message')],
        [Input('exportdata-btn', 'n_clicks')],
        [State('exportdata-db', 'value'),
        State('exportdata-period-dropdown', 'value'),
         State('range-picker-exportdata', 'start_date'),
         State('range-picker-exportdata', 'end_date'),
         State('stored_timeDB', 'data'),
         State('stored_dayDB', 'data')
         ]
    )
    def dwd_exportdata(n_clicks, selected_db,
                      selected_period, start_date, end_date, time_db, day_db):

        def txtOut(txt):
            return dcc.Markdown(txt,
                     dangerously_allow_html=True)

        if n_clicks is None or n_clicks == 0:
            return [dash.no_update, False, ""]
        if selected_period == "stat_all":
            query_time = None#get_query_extractInterval(dbTime_name, None, None)
        else :
            if ((not selected_db ) and
                            (not start_date or not end_date)):
                return [txtOut("ERREUR"), True, "Sélectionnez des données et une période"]

            if not selected_db :
                return [ txtOut("ERREUR"), True, "Sélectionnez des données"]

            if not start_date or not end_date:
                return [ txtOut("ERREUR"), True, "Sélectionnez une période"]



            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            print("Start Date:", start_date)
            print("End Date:", end_date)

            if selected_period in ['stat_day', 'stat_week', 'stat_month', 'stat_year']:
                if start_date != end_date:
                    return [txtOut("ERREUR"), True, "Choisir une seule date"]
                else:
                    start_date = get_startrange_date(end_date, selected_period)

            if selected_period == 'stat_perso' and start_date == end_date:
                return [ txtOut("ERREUR"), True, "Choisir une date différente"]

            query_time = None#get_query_extractInterval(selected_db, start_date, end_date)
            print("query = " + query_time)


        # conn = sqlite3.connect(db_file)
        # df = pd.read_sql_query(query_time, conn)
        # conn.close()
        if selected_db == dbTime_name:
            df = time_db
        elif selected_db == dbDayI_name:
            df = day_db
        else:
            sys.exit(1)

        print("n row df : " + str(df.shape[0]))

        # Exporter au format XLSX
        out= dcc.send_data_frame(df.to_excel,
                                 f"{selected_db}_export_{start_date}_to_{end_date}.xlsx",
                                 sheet_name='Données', index=False)


        return [out, False, ""]



    ################################################################################################################################
    ################################ CALLBACKS - TAB update & show DB - màj datepicker upload/delete
    ################################################################################################################################
    # Callback pour mettre à jour la liste des dates après l'upload
    # ou la suppression de données
    @app.callback(
        [
            Output('date-picker-dbdata', 'min_date_allowed'),
            Output('date-picker-dbdata', 'max_date_allowed'),
            Output('date-picker-dbdata', 'disabled_days'),
            Output('date-picker-delete', 'min_date_allowed'),
            Output('date-picker-delete', 'max_date_allowed'),
            Output('date-picker-delete', 'disabled_days'),
        ],
        [Input('output-upload', 'children'),
         Input('output-delete', 'children'),
         State('stored_dayDB', 'data')
         ]
    )
    # *_ : convention pour indiquer que la fonction peut accepter un nombre arbitraire
    # d'arguments, mais que ces arguments ne seront pas utilisés dans la fonction.
    # comme *args pour ombre variable d'arguments positionnels (ici nom de variable _)

    def update_all_dates(upbut, delbut, day_db):
        all_dates = list(set(day_db[db_daycol]))
        min_date_allowed = min(all_dates)
        max_date_allowed = max(all_dates)
        disabled_days = [pd.to_datetime(date).date() for date in
                         pd.date_range(start=min_date_allowed, end=max_date_allowed).
                         difference(pd.to_datetime(all_dates))]
        return (min_date_allowed, max_date_allowed,
                disabled_days, min_date_allowed,
                max_date_allowed, disabled_days)





    # Callback pour mettre à jour les dates après upload/suppression
    @app.callback(
        [Output(picker_id, 'min_date_allowed') for picker_id in all_range_pickers] +
        [Output(picker_id, 'max_date_allowed') for picker_id in all_range_pickers] +
        [Output(picker_id, 'disabled_days') for picker_id in all_range_pickers],
        [Input('output-upload', 'children'),
         Input('output-delete', 'children'),
         State('stored_dayDB', 'data')]
    )
    def update_all_rangepickerdates(updb, deldb, day_db):
        # all_dates = fetch_timedata_dates()
        all_dates = list(set(day_db[db_daycol]))
        min_date_allowed = min(all_dates)
        max_date_allowed = max(all_dates)
        disabled_days = [pd.to_datetime(date).date() for date in
                         pd.date_range(start=min_date_allowed, end=max_date_allowed).
                         difference(pd.to_datetime(all_dates))]

        # Retourner les valeurs mises à jour pour tous les DatePickers
        return ([min_date_allowed] * len(all_range_pickers) +
                [max_date_allowed] * len(all_range_pickers) +
                [disabled_days] * len(all_range_pickers))

    ################################ CALLBACKS - TAB 3 - GESTION DES DONNÉEs
    ### callback pour l'upload de nouvelles données
    @app.callback(
        Output('output-upload', 'children'),
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'),
         State('upload-data', 'last_modified')]
    )
    def update_output(list_of_contents, list_of_names, list_of_dates):
        if list_of_contents is not None:
            children = [
                parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)
            ]
            return children


    # callback pour supprimer les données en fonction de la date
    @app.callback(
        Output('output-delete', 'children'),
        [Input('delete-button', 'n_clicks')],
        [State('date-picker-delete', 'date')]
    )
    def delete_data(n_clicks, date):
        if n_clicks and date:
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute("DELETE FROM " + dbTime_name + " WHERE " + db_timecol + f" LIKE '{date}%'")
            nrows_del = c.rowcount
            conn.commit()
            conn.close()
            return html.Div(["Successfully deleted " + str(nrows_del) +" data for date: {}".format(date)])
        return html.Div()
