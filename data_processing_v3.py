import pandas as pd
import re
from settings import *
# from utils_fcts import print_df_shape

def clean_cols(myl):
    #  myl = [re.sub(r'\[.*\]', '', x) for x in myl]
    myl = [re.sub(r'[-\[\]\+ \(\)°%]', '_', x.strip()) for x in myl]
    myl = [re.sub(r'_+', '_', x) for x in myl]
    myl = [x.strip("_") for x in myl]
    return myl


def getheadercols(r1, r2, r3):
    # les headers ont un champ de moins que les valeurs
    l1 = r1.split(';') #+ ["missing"]
    l2 = r2.split(';') #+ [""]
    l3 = r3.split(';') #+ [""]
    assert len(l1) == len(l2)
    assert len(l1) == len(l3)
    for i in range(1, len(l1)):
        if l1[i] == '':
            l1[i] = l1[i - 1]
    # enlever caractères spéciaux et unité
    l1 = clean_cols(l1)
    # Concatenate the first three rows to form new column names
    new_columns = [f'{l1[i]}_{l2[i]}_{l3[i]}' for i in range(len(l1))]
    new_columns = [re.sub(r'_+', '_', x) for x in new_columns]
    new_columns[0] = db_timecol
    return clean_cols(new_columns)




def file2tables(file_path):
    error_msg = ""
    ok_msg = ""

    # Détection du type d'entrée : fichier ou chemin de fichier
    if isinstance(file_path, str):  # Si c'est un chemin de fichier
        is_file_obj = False
        f = open(file_path, encoding='latin1')
        filepathlab = file_path

    elif isinstance(file_path, io.StringIO):  # Si c'est un objet fichier
        is_file_obj = True
        f = file_path  # Utiliser l'objet de fichier directement
        filepathlab = "file content"

    else:
        raise ValueError("file_input must be either a file path or an io.StringIO object.")

    print("> START processing " + filepathlab)

    time_pattern = re.compile(r'^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$')
    dayP_pattern = re.compile(r'^P\d.+')
    dayI_pattern = re.compile(r'^I\d.+')



    #with open(file_path, encoding='latin1') as f:
    try:
        print(">>> start reading content")
        # Lire les 3 lignes du header
        header_lines = [f.readline().strip().rstrip(";") for _ in range(3)]
        new_columns = getheadercols(header_lines[0], header_lines[1], header_lines[2])
        time_lines_init = [f.readline().strip().rstrip(";").split(";") for _ in
                           range(60 * 24)]
        curr_day = time_lines_init[0][0].split(' ')[0]
        # pas nécessaire de mettre range(3, 3 + 60 * 24)] ! _ est le pointeur
        time_lines = [x for x in time_lines_init if len(x) == len(new_columns) and
                      time_pattern.match(x[0]) and
                      re.compile(curr_day).match(x[0])]
        maxTime_idx = max(i for i, x in enumerate(time_lines_init) if len(x) ==
                          len(new_columns) and time_pattern.match(x[0]))
        dayPstart_idx = maxTime_idx + nHeaderSkip + 1
        # repositionner le pointeur
        f.seek(0)
        for _ in range(dayPstart_idx):
            f.readline()

        dayP_lines_init = [f.readline().strip().rstrip(";").split(";") for _ in
                           range(nRowsDayP)]
        # pas nécessaire dayPstart_idx,(dayPstart_idx+nRowsDayP))
        dayP_lines = [x for x in dayP_lines_init if dayP_pattern.match(x[0])]
        maxDayP_idx = max(i for i, x in enumerate(dayP_lines_init) if
                          dayP_pattern.match(x[0]))

        dayIstart_idx = maxDayP_idx + dayPstart_idx + 1

        # repositionner le pointeur
        f.seek(0)
        for _ in range(dayIstart_idx):
            f.readline()

        dayI_lines_init = [f.readline().strip().rstrip(";").split(";") for _ in
                           range(nRowsDayI)]
        # pas nécessaire range(dayIstart_idx,(dayIstart_idx+nRowsDayI)
        dayI_lines = [x for x in dayI_lines_init if dayI_pattern.match(x[0])]

    finally:
        if not is_file_obj:
            f.close()  # Ne fermer que si nous avons ouvert le fichier
    ###############################################################
    ##################### EXTRAIRE LES DONNÉES TIME
    ###############################################################
    time_data = pd.DataFrame(time_lines)#, columns=new_columns)

    time_data.loc[:, 0] = pd.to_datetime(time_data.iloc[:, 0],
                        format='%d.%m.%Y %H:%M').dt.strftime('%Y-%m-%d %H:%M:%S')
    ntime, ncols = time_data.shape
    time_data.columns = new_columns

    if ntime < 60 * 24:
        error_msg += filepathlab + " - WARNING : missing 'time' data (available : " + str(ntime) + "/" + str(60 * 24)
    elif ntime == 60 * 24:
        ok_msg += filepathlab + " - SUCCESS reading 'time' data "
    print(','.join(list(set(time_real_cols + time_txt_cols)-set(time_data.columns))))
    assert time_data.columns.isin(time_real_cols + time_txt_cols).all()
    time_missingcols = list(set(time_real_cols + time_txt_cols) -
                            set(time_data.columns))

    if len(time_missingcols) > 0:
        error_msg += "\n"+ filepathlab + " - WARNING : missing 'time' data columns (" + ','.join(time_missingcols) + ")\n"
    else:
        ok_msg += "\n"+ filepathlab + " - SUCCESS found all 'time' data columns\n"

    date_day = pd.to_datetime(curr_day, format='%d.%m.%Y').strftime('%Y-%m-%d')
    ###############################################################
    ##################### EXTRAIRE LES DONNÉES DAY P
    ###############################################################
    dayP_dataL = pd.DataFrame(dayP_lines)
    dayP_datam = dayP_dataL.melt(id_vars=[0],
                                 value_vars=list(dayP_dataL.columns),
                                 var_name='variable',
                                 value_name='value')
    dayP_datam.iloc[:, 0] = dayP_datam.iloc[:, 0] + "_" + dayP_datam.iloc[:, 1].astype(str)
    dayP_datam.drop(columns=['variable'], inplace=True)
    dayP_data = dayP_datam.T
    dayP_data.columns = dayP_data.iloc[0]
    dayP_data = dayP_data[1:]
    dayP_data.insert(0, day_txt_cols[0], date_day)

    ndayP, ndayPcols = dayP_data.shape
    assert ndayP <= 1
    if ndayP == 0:
        error_msg += "\n"+ filepathlab + " - WARNING : no 'dayP' data found"
    else :
        ok_msg += filepathlab + " - SUCCESS reading 'dayP' data "

    assert ndayPcols <= len(dayP_real_cols) + len(day_txt_cols)

    dayP_missingcols = list(set(dayP_real_cols + day_txt_cols) - set(dayP_data.columns))
    if len(dayP_missingcols) > 0:
        error_msg += "\n"+ filepathlab + " - WARNING : missing 'dayP' data columns (" + \
                     ','.join(dayP_missingcols) + ")\n"
    else:
        ok_msg += "\n"+ filepathlab + " - SUCCESS found all 'dayP' data columns\n"

    ###############################################################
    ##################### EXTRAIRE LES DONNÉES DAY I
    ###############################################################

    dayI_dataL = pd.DataFrame(dayI_lines)

    dayI_datam = dayI_dataL.melt(id_vars=[0],
                                 value_vars=list(dayI_dataL.columns),
                                 var_name='variable',
                                 value_name='value')
    dayI_datam.iloc[:, 0] = dayI_datam.iloc[:, 0] + "_" + dayI_datam.iloc[:, 1].astype(str)
    dayI_datam.drop(columns=['variable'], inplace=True)
    dayI_data = dayI_datam.T
    dayI_data.columns = dayI_data.iloc[0]
    dayI_data = dayI_data[1:]
    dayI_data.insert(0, day_txt_cols[0], date_day)

    ndayI, ndayIcols = dayI_data.shape

    assert ndayI <= 1
    if ndayI == 0:
        error_msg += "\n"+ filepathlab + " - WARNING : no 'dayI' data found\n"
    else :
        ok_msg += filepathlab + " - SUCCESS reading 'dayI' data\n"

    assert ndayIcols <= len(dayI_real_cols) + len(day_txt_cols)

    dayI_missingcols = list(set(dayI_real_cols + day_txt_cols) - set(dayI_data.columns))

    if len(dayI_missingcols) > 0:
        error_msg += "\n"+ filepathlab + " - WARNING : missing 'dayI' data columns (" + \
                     ','.join(dayI_missingcols) + ")\n"
    else:
        ok_msg += "\n"+ filepathlab + " - SUCCESS found all 'dayI' data columns\n"

    for col in time_data.columns:
        if col.endswith('_L1'):
            col_l2 = col.replace('_L1', '_L2')
            if col_l2 in time_data.columns:
                new_col = col.replace('_L1', '_L1_L2')
                if not new_col in time_data.columns:
                    time_data[new_col] = time_data[col] + time_data[col_l2]

    return {"time_data" : time_data,
            "dayP_data" : dayP_data,
            "dayI_data" : dayI_data,
            "error" : error_msg,
            "success" : ok_msg}


def create_and_insert(timeData, dayiData, daypData=None):
    # Connexion à la base de données SQLite
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Créer les tables si pas existant
    c.execute('''CREATE TABLE IF NOT EXISTS ''' + dbTime_name + "(" +
              ','.join([x + " TEXT" for x in time_txt_cols]) + "," +
              ','.join([x + " REAL" for x in time_real_cols + time_added_cols]) + '''
        )''')

    if daypData:
        c.execute('''CREATE TABLE IF NOT EXISTS ''' + dbDayP_name + "(" +
                  ','.join([x + " TEXT" for x in day_txt_cols]) + "," +
                  ','.join([x + " REAL" for x in dayP_real_cols]) + '''
              )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ''' + dbDayI_name + "(" +
              ','.join([x + " TEXT" for x in day_txt_cols]) + "," +
              ','.join([x + " REAL" for x in dayI_real_cols]) + '''
          )''')
    conn.commit()

    # Insérer les données dans la base de données
    timeData.to_sql(dbTime_name, conn,
                                        if_exists='append', index=False)
    if daypData:
        daypData.to_sql(dbDayP_name, conn,
                                            if_exists='append', index=False)
    dayiData.to_sql(dbDayI_name, conn,
                                        if_exists='append', index=False)

    # Il est important de fermer la connexion une fois que toutes les opérations sont complétées
    conn.close()

def create_and_concat(timeData, dayiData,currentTimeData,
                                currentDayiData, currentDaypData = None,daypData=None):

    out_txt = ""
    out_txt += "receive time data to add : " + print_df_shape(timeData)
    out_txt += "receive dayI data to add : " + print_df_shape(dayiData)

    ### pas implémnté pour dayp
    if currentTimeData :
        newTimeData = pd.concat([timeData, currentTimeData], axis=0)
    else:
        newTimeData = timeData

    if currentDayiData:
        newDayiData = pd.concat([dayiData, currentDayiData], axis=0)
    else:
        newDayiData = dayiData

    out_txt += "return updated time data : " + print_df_shape(newTimeData)
    out_txt += "return updated dayI data : " + print_df_shape(newDayiData)

    return{"new_dayI_data" : newDayiData,
                    "new_time_data": newTimeData,
           "msg" : out_txt
                    }
