from settings import *
from datetime import timedelta
import numpy as np
import dash_daq as daq
from data_processing_v3 import *
from app_settings import *

def get_var_desc(col, db):
    if db == dbTime_name:
        if isinstance(col, str) :
            desc_txt = "<b>" + col + "</b> : " + \
                       showcols_settings[col]['description']
        elif isinstance(col, list) :
            desc_txt = '<br>'.join(["<b>" + selcol + "</b> : " +
                                    showcols_settings[selcol]['description']
                                    for selcol in col])
        else:
            return None

    elif db == dbDayP_name:
        if isinstance(col, str):
            desc_txt = "<b>" + col + "</b> : " + \
                       dayPcols_settings[col]['description']
        elif isinstance(col, list):
            desc_txt = '<br>'.join(["<b>" + selcol + "</b> : " +
                                dayPcols_settings[selcol]['description']
                                for selcol in col])
        else:
            return None


    elif db == dbDayI_name:
        if isinstance(col, str):
            desc_txt = "<b>" + col + "</b> : " + \
                       dayIcols_settings[col]['description']
        elif isinstance(col, list):
            desc_txt = '<br>'.join(["<b>" + selcol + "</b> : " +
                                dayIcols_settings[selcol]['description']
                                for selcol in col])
        else:
            return None
    else:
        return None
    return desc_txt


# # récupérer toutes les colonnes de la table "donnees" sauf "time"
# def get_timedata_columns():
#     conn = sqlite3.connect(db_file)
#     query = f"PRAGMA table_info({dbTime_name})"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return [col for col in df['name'] if col != db_timecol]
#
# def get_daydata_columns(dayType):
#     conn = sqlite3.connect(db_file)
#     if dayType == "P":
#         query = f"PRAGMA table_info({dbDayP_name})"
#     elif dayType == "I":
#         query = f"PRAGMA table_info({dbDayI_name})"
#     else:
#         exit(1)
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return [col for col in df['name'] if col != db_daycol]
#





# # lire les 10 premières lignes de la base de données
# def fetch_timedata(date=None):
#     conn = sqlite3.connect(db_file)
#     if date:
#         # query = f"SELECT * FROM {dbTime_name} WHERE DATE({db_timecol}) = '{date}' LIMIT 10"
#         query = f"SELECT * FROM {dbTime_name} WHERE DATE({db_timecol}) = '{date}'"
#     else:
#         # query = f"SELECT * FROM {dbTime_name}"
#         query = f"SELECT * FROM {dbTime_name} LIMIT 10"
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df
#

# def fetch_timedata_dates():
#     conn = sqlite3.connect(db_file)
#     query = "SELECT DISTINCT " + time_txt_cols[0] + " FROM " + dbTime_name
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df[db_timecol].tolist()
#

# def fetch_dayPdata_dates(day_type):
#     conn = sqlite3.connect(db_file)
#     query = "SELECT DISTINCT " + day_txt_cols[0] + " FROM " + day_type#day_type=dbDayP_name
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df[db_daycol].tolist()


def parse_table(contents, filename):
    # print(contents)
    # print("****")
    # print(content_string)
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:

        print("Try reading file : " + filename)
        file_obj = io.StringIO(decoded.decode(enc))

        try:
            prepdata_output = file2tables(file_obj)
            print(prepdata_output['error'])
            print(prepdata_output['success'])
            print(":-) data reading success for " + filename)
        except:
            print("!!! data reading failed for " + filename)
    except:
        print("!!! reading data failed for " + filename)

    return prepdata_output


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:

        print("Try reading file : " + filename)
        file_obj = io.StringIO(decoded.decode(enc))

        try:
            prepdata_output = file2tables(file_obj)
            print(prepdata_output['error'])
            print(prepdata_output['success'])
            print(":-) data reading success for " + filename)
        except:
            print("!!! data reading failed for " + filename)

        try:
            print("... start inserting in DB " + filename)
            create_and_insert(timeData=prepdata_output['time_data'],
                              # daypData=prepdata_output['dayP_data'],
                              dayiData=prepdata_output['dayI_data'])
            print(":-) inserting in DB success for " + filename)


        except:
            print("!!! inserting in DB failed for " + filename)


        print("données ajoutées à la DB")

        return html.Div([
            'Successfully uploaded and inserted: {}'.format(filename)
        ])

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing the file : ' + filename
        ])


def parse_contents_vConcat(contents, filename, timedb, daydb):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:

        print("Try reading file : " + filename)
        file_obj = io.StringIO(decoded.decode(enc))

        try:
            prepdata_output = file2tables(file_obj)
            print(prepdata_output['error'])
            print(prepdata_output['success'])
            print(":-) data reading success for " + filename)
        except:
            print("!!! data reading failed for " + filename)

        try:
            print("... start inserting in DB " + filename)
            concat_out = create_and_concat(timeData=prepdata_output['time_data'],
                              # daypData=prepdata_output['dayP_data'],
                              dayiData=prepdata_output['dayI_data'],
                              currentTimeData=timedb,
                                currentDayData = daydb)
            print(":-) inserting in DB success for " + filename)

        # return {"new_dayI_data": newDayiData,
        #         "new_time_data": newTimeData
        #         msg}

            print("données ajoutées à la DB")

            return [concat_out, html.Div([
                'Successfully uploaded and inserted: {}'.format(filename)
            ])]

        except Exception as e:
            print(e)
            print("!!! inserting in DB failed for " + filename)
            return html.Div([
                'There was an error while inserting the file : ' + filename
            ])

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing the file : ' + filename
        ])



def get_db_dropdown(id) :
    return dcc.Dropdown(
                    id=id,
                    options=[
                        {'label': 'Données minutes', 'value': dbTime_name},
                        # {'label': 'Données journalières P', 'value': dbDayP_name},
                        {'label': 'Données journalières I', 'value': dbDayI_name}
                    ],
                    placeholder="Choisissez la table de données"
                )




# def get_query_extractInterval(dbname, startday, endday):
#     print("start get query")
#     if not endday and not startday:
#         return f"SELECT * FROM {dbname}"
#     if dbname==dbTime_name:
#         if startday and endday:
#             return f"SELECT * FROM {dbname} WHERE DATE({db_timecol}) >= DATE('{startday}') AND DATE({db_timecol}) <= DATE('{endday}')"
#         elif startday and not endday:
#             return f"SELECT * FROM {dbname} WHERE DATE({db_timecol}) >= DATE('{startday}')')"
#         elif endday and not startday:
#             return f"SELECT * FROM {dbname} WHERE DATE({db_timecol}) <= DATE('{endday}')"
#         return "ERREUR"
#     else :
#         if startday and endday:
#             return f"SELECT * FROM {dbname} WHERE {db_daycol} >= '{startday}' AND {db_daycol} <= '{endday}'"
#             # if startday == endday :
#             #     return f"SELECT * FROM {dbname} WHERE {db_daycol} = '{startday}'"
#             # else:
#             #     return f"SELECT * FROM {dbname} WHERE {db_daycol} >= '{startday}' AND {db_daycol} <= '{endday}'"
#         elif startday and not endday:
#             return f"SELECT * FROM {dbname} WHERE {db_daycol} >= '{startday}'"
#         elif endday and not startday:
#             return f"SELECT * FROM {dbname} WHERE {db_daycol} <= '{endday}'"
#         return "ERREUR"


def update_layout_cols(selcols):
    if len(selcols) > 0:
        yaxis_layout['title'] = selcols[0]
    if len(selcols) > 1:
        yaxis2_layout['title'] = selcols[1]
    if len(selcols) > 2:
        yaxis3_layout['title'] = selcols[2]
    if len(selcols) > 3:
        yaxis4_layout['title'] = selcols[3]

def get_range_picker(id,dates):
    return dcc.DatePickerRange(
        id=id,
        # date=None,
        display_format='DD.MM.YYYY',  ## prend les dates seulement dayP -> assume partt les mm !!
        min_date_allowed=min(dates),
        max_date_allowed=max(dates),
        disabled_days=[pd.to_datetime(date).date() for date in
                       pd.date_range(start=min(dates),
                                     end=max(dates)).
                       difference(pd.to_datetime(dates))],
        minimum_nights=0,
        style={'display': 'none'}  # Initialement caché
    )


# def get_range_picker(id):
#     return dcc.DatePickerRange(
#         id=id,
#         # date=None,
#         display_format='DD.MM.YYYY',  ## prend les dates seulement dayP -> assume partt les mm !!
#         min_date_allowed=min(fetch_dayPdata_dates(dbDayI_name)),
#         max_date_allowed=max(fetch_dayPdata_dates(dbDayI_name)),
#         disabled_days=[pd.to_datetime(date).date() for date in
#                        pd.date_range(start=min(fetch_dayPdata_dates(dbDayI_name)),
#                                      end=max(fetch_dayPdata_dates(dbDayI_name))).
#                        difference(pd.to_datetime(fetch_dayPdata_dates(dbDayI_name)))],
#         minimum_nights=0,
#         style={'display': 'none'}  # Initialement caché
#     )
#

def get_period_dropdown(id):
    return dcc.Dropdown(
        id=id,
        options=[
            {'label': 'Jour', 'value': 'stat_day'},
            {'label': 'Semaine', 'value': 'stat_week'},
            {'label': 'Mois', 'value': 'stat_month'},
            {'label': 'Année', 'value': 'stat_year'},
            {'label': 'Tout', 'value': 'stat_all'},
            {'label': 'Personnalisé', 'value': 'stat_perso'}
        ],
        value='stat_day',
        placeholder="Période"
    )

#
# def get_startrange_date(endd, period):
#     if period == 'stat_week':
#         return endd - timedelta(days=7)
#     elif period == "stat_day":
#         return endd
#     elif period == 'stat_month':
#         return endd - timedelta(days=30)
#     elif period == 'stat_year':
#         return endd - timedelta(days=365)
#     return exit(1)

def get_plotdesc(col1, col2=None, db = dbTime_name, htmlFormat=True, settingsdict=None):
    if not settingsdict:
        if db == dbTime_name:
            settingsdict = showcols_settings
        elif db == dbDayI_name:
            settingsdict = dayIcols_settings
        elif db == dbDayP_name:
            settingsdict = dayPcols_settings
        else:
            exit(1)
    print("col1 in get_plotdesc = " + col1)
    col1_txt = settingsdict[col1]['description']
    if col2 :
        col2_txt = settingsdict[col2]['description']
    if htmlFormat:
        if col2:
            if col1_txt == col2_txt :
                fig_desc = "<u>" + col1 + "</u> et  <u>" + col2 + "</u> : " + col2_txt
            else :
                col1_desc = "<u>" + col1 + "</u> : " + col1_txt
                col2_desc = "<u>" + col2 + "</u> : " + col2_txt
                fig_desc = col1_desc + "<br>" + col2_desc
        else :
            fig_desc = "<u>" + col1 + "</u> : " + col1_txt

    else :
        if col2 :
            if col1_txt == col2_txt :
                fig_desc = col1 + " et " + col2 +  " : " + col2_txt
            else :
                col1_desc = col1 + " : " + col1_txt
                col2_desc = col2 + " : " + col2_txt
                fig_desc = col1_desc + "\n" + col2_desc
        else:
            fig_desc = col1 + "  : " + col1_txt
    return fig_desc
def get_dbTime_2vargraph(df, xcol, col1, col2=None,
                         dbName = dbTime_name,
                         htmlFormat=True, withQtLines = True, stacked=False,
                         settingsdict=None, startDate=None, endDate=None):
    fig_desc = get_plotdesc(col1, col2, db = dbName,
                            htmlFormat=htmlFormat,settingsdict=settingsdict)
    fig1 = go.Figure()
    if stacked:
        fig1.add_trace(go.Scatter(x=df[xcol], y=df[col1],
                                  mode='lines', name=col1, stackgroup='one'))
        if col2 :
            fig1.add_trace(go.Scatter(x=df[xcol], y=df[col2],
                                      mode='lines', name=col2, stackgroup='one'))
    else:
        fig1.add_trace(go.Scatter(x=df[xcol], y=df[col1],
                                 mode='lines', name=col1))
        if col2:
            fig1.add_trace(go.Scatter(x=df[xcol], y=df[col2],
                                     mode='lines', name=col2, yaxis='y2'))


    if col2:
        fig1.update_layout(
            # title=f'{col1} et {col2}',
        title=f'<b>{col1}</b> et <b>{col2}</b>',
        title_font=dict(size=20),
            xaxis_title=xcol,
            yaxis_title=col1,
            yaxis2=dict(
                title=col2,
                overlaying='y',
                side='right'
            ))
        qtcols = {col1 : "limegreen", col2 : "darkgreen"}
        all_cols = [col1,col2]
    else:
        fig1.update_layout(
            # title=f'{col1} et {col2}',
        title=f'<b>{col1}</b>',
        title_font=dict(size=20),
            xaxis_title=xcol,
            yaxis_title=col1)
        qtcols = {col1: "limegreen"}
        all_cols=[col1]

    if withQtLines:
        for icol in all_cols :
            q1 = df[icol].quantile(0.1)
            q9 = df[icol].quantile(0.9)
            # fig1.add_hline(y=q1, line=dict(color='green', width=2, dash='dash'), name='0.1-Qt ' +icol)
            # fig1.add_hline(y=q9, line=dict(color='green', width=2, dash='dash'), name='0.9-Qt ' + icol)
            fig1.add_trace(go.Scatter(
                x=[df[xcol].min(), df[xcol].max()],
                y=[q1, q1],
                mode="lines",
                line=dict(color=qtcols[icol], width=2, dash='dash'),
                name=f'0.1-0.9 Qt {icol}',
                showlegend=True
            ))
            fig1.add_trace(go.Scatter(
                x=[df[xcol].min(), df[xcol].max()],
                y=[q9, q9],
                mode="lines",
                line=dict(color=qtcols[icol], width=2, dash='dash'),
                name=f'0.9-Qt {icol}',
                showlegend=False
            ))

        if endDate and startDate:
            fig1.update_xaxes(range=[startDate, endDate])

    return [fig1, fig_desc]

    # Fonction pour trouver les points d'intersection exacts
def find_intersections(df, col1, col2):
    intersections = []
    for i in range(len(df) - 1):
        if (df[col1][i] - df[col2][i]) * (df[col1][i + 1] - df[col2][i + 1]) < 0:
            x1, x2 = df.index[i], df.index[i + 1]
            y1_1, y2_1 = df[col1][i], df[col1][i + 1]
            y1_2, y2_2 = df[col2][i], df[col2][i + 1]

            # Calcul de l'intersection linéaire
            slope_1 = (y2_1 - y1_1) / (x2 - x1).total_seconds()
            slope_2 = (y2_2 - y1_2) / (x2 - x1).total_seconds()
            intersect_seconds = (y1_2 - y1_1) / (slope_1 - slope_2)
            intersect_day = x1 + pd.Timedelta(seconds=intersect_seconds)
            intersect_value = y1_1 + slope_1 * intersect_seconds
            intersections.append((intersect_day, intersect_value))
    return intersections

def get_intersectLines_plot(data, indexcol, col1, col2, startDate=None, endDate=None):
    # Trouver les points d'intersection
    intersections = find_intersections(data, col1=col1, col2=col2)

    # Ajouter les points d'intersection aux données
    intersect_df = pd.DataFrame(intersections, columns=[indexcol, col1])
    intersect_df[col2] = intersect_df[col1]
    intersect_df.set_index(indexcol, inplace=True)

    df = pd.concat([data, intersect_df]).sort_values(indexcol)

    # Créer la figure Plotly
    fig = go.Figure()

    # Tracer les lignes
    fig.add_trace(go.Scatter(x=df.index, y=df[col1],
                             mode='lines', name=col1, line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=df[col2],
                             mode='lines', name=col2, line=dict(color='red')))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[col1],
        fill=None,
        mode='lines',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=df.index,
        y=np.where(df[col1] > df[col2], df[col2], df[col1]),
        fill='tonexty',
        mode='none',
        line=dict(color='rgba(0,0,0,0)'),
        fillcolor='rgba(0,0,255,0.3)',
        showlegend=False
    ))

    # Zone rouge où I7008_1 est au-dessus
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df[col2],
        fill=None,
        mode='lines',
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=df.index,
        y=np.where(df[col1] <= df[col2], df[col1], df[col2]),
        fill='tonexty',
        mode='none',
        line=dict(color='rgba(0,0,0,0)'),
        fillcolor='rgba(255,0,0,0.3)',
        showlegend=False
    ))

    # Configuration de la mise en page
    fig.update_layout(
         title=f'<b>{col1}</b> et <b>{col2}</b>',
                xaxis_title=indexcol,
                yaxis_title='Valeur',
                showlegend=True
    )

    if endDate and startDate:
        fig.update_xaxes(range=[startDate, endDate])

    return fig

def get_stacked_cmpgraph(initdf, xcol, col1, col2,
                         dbName = dbTime_name,
                         commoncol ='équilibre',
                         htmlFormat=True,
                         settingsdict=None,
                         startDate=None, endDate=None):
    df = initdf.copy()
    df[commoncol] = np.minimum(df[col1], df[col2])

    # Mise à jour des colonnes I7007_1 et I7008_1
    df[col1] = df[col1] - df[commoncol]
    df[col2] = df[col2] - df[commoncol]

    fig_desc = get_plotdesc(col1, col2, db = dbName,
                            htmlFormat=htmlFormat,settingsdict=settingsdict)
    fig1 = go.Figure()


    # Ajouter les barres pour 'commoncol'
    fig1.add_trace(go.Bar(x=df[xcol], y=df[commoncol],
                          name=commoncol, marker=dict(color='grey')))

    # Ajouter les barres pour col1, empilées au-dessus de commoncol
    fig1.add_trace(go.Bar(x=df[xcol], y=df[col1],
                          name=col1, base=df[commoncol], marker=dict(color='blue')))

    # Ajouter les barres pour col2, empilées au-dessus de commoncol
    fig1.add_trace(go.Bar(x=df[xcol], y=df[col2],
                          name=col2, base=df[commoncol], marker=dict(color='red')))
    fig1.update_layout(
        barmode='stack' ,
    title=f'<b>{col1}</b> et <b>{col2}</b>',
    title_font=dict(size=20),
        xaxis_title=xcol,
        yaxis_title=col1,
        yaxis2=dict(
            title=col2,
            overlaying='y',
            side='right'
        ))

    if startDate and endDate:
        fig1.update_xaxes(range=[startDate, endDate])


    return [fig1, fig_desc]



def get_modal_dashboard(id_mainDiv, id_childDiv, id_closeBtn, id_graph):
    return html.Div(
    id=id_mainDiv,
    style={"display": "none"},  # Initialement caché
    children=[
        html.Div(
            id=id_childDiv,
            children=[
                html.Button("Fermer", id=id_closeBtn ,n_clicks=0),
                dcc.Graph(id=id_graph,config= {
                                        'scrollZoom': True  # Activer le zoom avec la molette
                                    })
            ],
            style={
                "position": "fixed",
                "top": "50%",
                "left": "50%",
                "transform": "translate(-50%, -50%)",
                "background-color": "white",
                "padding": "20px",
                "box-shadow": "0px 0px 10px rgba(0, 0, 0, 0.5)",
                "z-index": "1000",
                "width": "80%",
                "height": "80%",
                "overflow": "auto"
            }
        ),
        html.Div(
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "background-color": "rgba(0, 0, 0, 0.5)",
                "z-index": "999"
            }
        )
    ]
    )

def generate_header_row(timestamp):
        return html.Div(
            className="row metric-row header-row",
            children=[
                html.Div(
                    className="one column metric-row-header",
                    children=html.Div("Mesures"),
                ),
                html.Div(
                    className="two columns metric-row-header",  # Élargi pour inclure le pourcentage
                    children=html.Div("# " + timestamp + " avec valeurs"),
                ),
                html.Div(
                    className="two columns metric-row-header",  # Élargi pour inclure le pourcentage
                    children=html.Div("# " + timestamp + " sans données"),
                ),
                html.Div(
                    className="four columns metric-row-header",
                    children=html.Div("Tendance"),
                ),
                html.Div(
                    className="four columns metric-row-header",
                    children=html.Div("Dispo. des données"),
                ),
            ],
        )


def generate_summary_row(id_suffix, column_name, minutes_with_data,
                             minutes_with_missing_data, sparkline_data,
                             time_data, btn_type):
        ooc_graph_id = f"ooc_graph_{id_suffix}"

        total_minutes = minutes_with_data + minutes_with_missing_data
        percentage_with_data = (minutes_with_data / total_minutes) * 100
        percentage_missing_data = (minutes_with_missing_data / total_minutes) * 100

        minutes_with_data_text = f"{minutes_with_data} ({percentage_with_data:.0f}%)"
        minutes_with_missing_data_text = f"{minutes_with_missing_data} ({percentage_missing_data:.0f}%)"

        sparkline_figure = go.Figure(
            {
                "data": [
                    {
                        "x": time_data,
                        "y": sparkline_data,
                        "mode": "lines",
                        "line": {"color": "#f4d44d"},
                        "name": column_name,
                    }
                ],
                "layout": {
                    "margin": dict(l=0, r=0, t=0, b=0, pad=0),
                    "xaxis": dict(showline=False, showgrid=False,
                                  zeroline=False, showticklabels=False),
                    "yaxis": dict(showline=False, showgrid=False,
                                  zeroline=False, showticklabels=False),
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)",
                },
            }
        )

        return html.Div(
            className="row metric-row",
            children=[
                html.Div(
                    className="one column metric-row-button-text",
                    children=html.Button(
                        children=column_name,
                        id={'type': btn_type, 'index': id_suffix},
                        n_clicks=0,
                    ),

                ),
                html.Div(
                    className="two columns",
                    children=html.Div(
                        children=minutes_with_data_text,
                    ),
                ),
                html.Div(
                    className="two columns",
                    children=html.Div(
                        children=minutes_with_missing_data_text,
                    ),
                ),
                html.Div(
                    className="four columns",
                    children=dcc.Graph(
                        id=f"sparkline_{id_suffix}",
                        figure=sparkline_figure,
                        style={"width": "100%", "height": "50px"},
                        config={"staticPlot": True,   'scrollZoom': True ,
                                "displayModeBar": False},
                    ),
                ),
                html.Div(
                    className="four columns",
                    children=daq.GraduatedBar(
                        id=ooc_graph_id,
                        color={
                            "ranges": {
                                "#f45060": [0, 3],
                                "#f4d44d": [3, 7],
                                "#13aa13": [7, 10],
                            }
                        },
                        showCurrentValue=False,
                        max=10,
                        value=percentage_with_data / 10,
                        size=250,
                    ),
                ),
            ],
        )



    # Fonction pour diviser une liste en N parties égales
def split_list(lst, n):
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    # Organiser les données en sections avec trois colonnes
def create_section(title, data):
        items = [html.P([html.U(col), f": {mean:.2f}"]) for col, mean in data.items()]
        columns = split_list(items, 3)
        return html.Div([
            html.H5(title, style={'font-weight': 'bold'}),
            html.Div([html.Div(col, className='col') for col in columns], className='row')
        ])



###### FONCTIONS POUR LA PAGE DE ACUEIL
def get_navbtn(id, lab):
    return html.Div(
      dbc.Button([
          html.I(className="fas fa-paper-plane"),
          " " + lab
      ],
          id=id,
          **navbtn_style),
                className="d-flex justify-content-center"
            )


def get_nav_link(id, lab):
    return html.A(lab, id=id, href="#",
                  style={"color": "#2507cf", "cursor": "pointer"})


def get_startrange_date_vLatest(timecol, period):
    endd = max(pd.to_datetime(timecol).dt.date)
    if period == 'stat_week':
        startd =endd - timedelta(days=7)
    elif period == "stat_day":
        startd =endd
    elif period == 'stat_month':
        startd =endd - timedelta(days=30)
    elif period == 'stat_year':
        startd =endd - timedelta(days=365)
    elif period == 'stat_all':
        startd = min(pd.to_datetime(timecol).dt.date)
    else :
        return exit(1)
    return [startd, endd]
#
# def get_startrange_date_vDT(dt,tcolname ,period):
#
#     endd = max(pd.to_datetime(dt[tcolname]).dt.date)
#
#     if period == 'stat_week':
#         startd = endd - timedelta(days=7)
#     elif period == "stat_day":
#         startd = endd
#     elif period == 'stat_month':
#         startd = endd - timedelta(days=30)
#     elif   period == 'stat_year':
#         startd = endd - timedelta(days=365)
#
#
#
#     return exit(1)



def print_df_shape(df):
    if df :
        return str(df.shape[0]) + " x " + str(df.shape[1])
    else :
        return "data frame is None"
