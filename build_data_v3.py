#import pandas as pd
import os
#import re
#import sqlite3
#import datetime
#from datetime import datetime
from datetime import date
from settings import *
from data_processing_v3 import *

database_folder = "data"
os.makedirs(database_folder,exist_ok=True)

# Spécifiez le chemin vers votre fichier CSV
datafolder = '../LOG_300524'
all_files = [os.path.join(datafolder, file) for file in os.listdir(datafolder) if file.endswith('.CSV')]
all_files.sort()
datafile = all_files[0]
db_file = os.path.join(database_folder, 'akonolinga_database_v3.db')
db_file = os.path.join(database_folder, 'akonolinga_database_v3_demo.db')
all_files=all_files[:3]

# all_files=[datafolder+"/LG240421.CSV"]

if os.path.exists(db_file):
    newfile = db_file.replace('.db',
                              "_" + datetime.now().strftime('%Y%m%d%H%M')+"_OLD.db")
    assert not os.path.exists(newfile)
    os.rename(db_file, newfile)

logfile  = os.path.join(database_folder, f"logs_importInDB_{ date.today()}.txt")
if os.path.exists(logfile):
    os.remove(logfile)
if os.path.exists(db_file):
    os.remove(db_file)
if not os.path.exists(os.path.dirname(db_file)):
    os.makedirs(os.path.dirname(db_file))
datafile = all_files[0]

for datafile in all_files:
    print("***** " + datafile)
    try:
        print("... start reading " + datafile)
        prepdata_output = file2tables(datafile)
        print(prepdata_output['error'])
        print(prepdata_output['success'])
        print(":-) data reading success for " + datafile)
        with open(logfile, 'a') as file:
            file.write(f"***** START {os.path.basename(datafile)}\n")
            file.write(f"{os.path.basename(datafile)}\twhile reading :\n")
            file.write(prepdata_output['error'] + "\n")
            file.write(prepdata_output['success'] + "\n")

    except:
        print("!!! data reading failed for " + datafile)
        with open(logfile, 'a') as file:
            file.write(f"{os.path.basename(datafile)}\tfailure\n")
        continue
    try :
        print("... start inserting in DB " + datafile)
        create_and_insert(timeData=prepdata_output['time_data'],
                           # daypData=prepdata_output['dayP_data'],
                          dayiData=prepdata_output['dayI_data'])

        print(":-) inserting in DB success for " + datafile)

        with open(logfile, 'a') as file:
            file.write(f"{os.path.basename(datafile)}\tinsert in DB success\n")

    except  :
        print("!!! inserting in DB failed for " + datafile)
        with open(logfile, 'a') as file:
            file.write(f"{os.path.basename(datafile)}\tinsert in DB failure\n")
        continue

print("output file " + db_file + " exists : " + str(os.path.exists(db_file)))

