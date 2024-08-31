from dash.dependencies import Input, Output, State
import dash
import pandas as pd
from utils_fcts import *
def register_callbacks(app):

    # @app.callback(
    #     [Output('upload-stored-container', 'style')
    #      # Output('stored_timeDB', 'data'),
    #      # Output('stored_dayDB', 'data')
    #      ],
    #     [Input('default-data-checkbox', 'value')]
    # )
    # def toggle_upload_visibility(default_data_checkbox):
    #     print(default_data_checkbox)
    #     if 'default' in default_data_checkbox :
    #         # Utiliser les données par défaut
    #         # et cacher le bouton
    #         return {'display': 'none'}
    #     else:
    #         return {'display': 'block'}

    @app.callback(
        [Output('upload-stored-container', 'style'),
         Output('stored_timeDB', 'data'),
         Output('stored_dayDB', 'data'),
         Output("stored-data-content", "children")],
        [Input('default-data-checkbox', 'value'),
         Input('upload-stored-data', 'contents'),
         Input('stored_timeDB', 'data')],
        [State('upload-stored-data', 'filename'),
         State('defaut_stored_timeDB', 'data'),
         State('defaut_stored_dayDB', 'data'),
         # State('stored_timeDB', 'data'),
         State('stored_dayDB', 'data')
         ]
    )
    def toggle_upload_visibility(default_data_checkbox, upload_contents,
                                 stored_timeDB_data,
                                 filename, defaut_timeDB_data, defaut_dayDB_data,
                                  stored_dayDB_data):
        # return dcc.Markdown(txt,
        #                     dangerously_allow_html=True)
        current_time_df = pd.DataFrame(stored_timeDB_data)
        current_day_df = pd.DataFrame(stored_dayDB_data)
        print(type(current_time_df[db_timecol][0]))
        print(type(current_day_df[db_daycol][0]))
        txt = "current time DB : " + str(current_time_df.shape[0]) + " x " + str(current_time_df.shape[1]) + "\n"
        txt += "current day DB : " + str(current_day_df.shape[0]) + " x " + str(current_day_df.shape[1])
        outtxt = dcc.Markdown(txt,dangerously_allow_html=True)
        print(default_data_checkbox)
        if 'default' in default_data_checkbox :
            # si je veux Utiliser les données par défaut
            # -> je cache l'upload de fichier et je store les données défaut
            return ({'display': 'none'},
                    pd.DataFrame(defaut_timeDB_data).to_dict(),
                    pd.DataFrame(defaut_dayDB_data).to_dict(),outtxt)
        ## si j arrive à ce stade c'est que je n'ai pas coché la checkbox

        # si j arrive ici c'est que je n'ai pas cohcé la checkbox et que je n'ai pas chargé de contenu
        # Afficher le bouton d'upload si "données par défaut" est décoché
        if not upload_contents:
            print("JE SUIS ARRIVEE ICI")
            return {'display': 'block'}, stored_timeDB_data, stored_dayDB_data, outtxt
        else:
            new_data = [parse_table(c, n) for c, n in zip(upload_contents, filename)]
            time_df_uploaded = pd.concat([x['time_data'] for x in new_data],
                                         ignore_index=True)
            print("données time loadées : " + str(time_df_uploaded.shape[0]))
            day_df_uploaded = pd.concat([x['dayI_data'] for x in new_data],
                                        ignore_index=True)
            print("données day loadées : " + str(day_df_uploaded.shape[0]))
            txt = "current time DB : " + str(time_df_uploaded.shape[0]) + " x " + str(time_df_uploaded.shape[1]) + "\n"
            txt += "current day DB : " + str(day_df_uploaded.shape[0]) + " x " + str(day_df_uploaded.shape[1])
            newtxt = dcc.Markdown(txt, dangerously_allow_html=True)
            return ({'display': 'block'}, time_df_uploaded.to_dict(),
                    day_df_uploaded.to_dict(), newtxt)

