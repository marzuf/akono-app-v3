import sqlite3
import pandas as pd
import base64
import plotly.graph_objects as go
from datetime import datetime
import base64
import io
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import dash_table
# import sqlite3
# import pandas as pd
import re
import dash_bootstrap_components as dbc
#import dash_html_components as html
import plotly.graph_objects as go

## taken from LG240416
full_r1="v7.6;XT-Ubat- (MIN) [Vdc];;XT-Uin [Vac];;XT-Iin [Aac];;XT-Pout [kVA];;XT-Pout+ [kVA];;XT-Fout [Hz];;XT-Fin [Hz];;XT-Phase [];;XT-Mode [];;XT-Transfert [];;XT-E CMD [];;XT-Aux 1 [];;XT-Aux 2 [];;XT-Ubat [Vdc];;XT-Ibat [Adc];;XT-Pin a [kW];;XT-Pout a [kW];;XT-Tp1+ (MAX) [°C];;VT-PsoM [kW];;VT-Mode [];VT-Tp1M [°C];VT-UpvM [Vdc];VT-IbaM [Adc];VT-UbaM [Vdc];VT-Phase [];VT-E CMD [];VT-Aux 1 [];VT-Aux 2 [];BSP-Ubat [Vdc];BSP-Ibat [Adc];BSP-SOC [%];BSP-Tbat [°C];Solar power (ALL) [kW];DEV XT-DBG1 [];DEV VT-locEr [];DEV SYS MSG;DEV SYS SCOM ERR;"
full_r2=";I3090;I3090;I3113;I3113;I3116;I3116;I3098;I3098;I3097;I3097;I3110;I3110;I3122;I3122;I3010;I3010;I3028;I3028;I3020;I3020;I3086;I3086;I3054;I3054;I3055;I3055;I3092;I3092;I3095;I3095;I3119;I3119;I3101;I3101;I3103;I3103;I11043;I11043;I11016;I11045;I11041;I11040;I11039;I11038;I11082;I11061;I11062;I7030;I7031;I7032;I7033;I17999;I3140;I11076;I17997;I17998;"
full_r3=";L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1-1;L2-2;L1-1;L2-2;L1-1;L2-2;L1-1;L2-2;L1-1;L2-2;1;ALL;1;1;1;1;1;1;1;1;1;1;1;1;1;ALL;1;1;1;1;"


FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

nHeaderSkip = 3
csvSep = ";"

db_file = 'data/akonolinga_database_v3_demo.db'
dbTime_name = "time_data"
dbDayP_name = "dayP_data"
dbDayI_name = "dayI_data"

db_timecol = "time"
db_daycol = "day"

enc = "latin_1"
#nColsTime = 46
nRowsDayP = 10
nColsDayP = 4
nRowsDayI = 13
nColsDayI = 3

# tab-2
maxTimePlotVar = 4
timePlotLineCols=['blue', 'red', 'green', 'orange']  # 'purple']

popupmsg_maxvar = "Vous ne pouvez pas sélectionner plus de " + str(maxTimePlotVar) +" variables."

# Les 2 sources peuvent être disciminée par leurs valeur: Le réseau à une fréquence très stable
# <49,5Hz-50,5Hz>. La generatrice est moin stable est a une fréquence généralement supérieure a 51Hz.
# Une valeur nule indique l''absence de la source réseau/génératrice
xtfin_genThresh = 51
xtfin_nosource = 0
xtfincol = "XT_Fin_Hz_I3122"

xtpuicol = "XT_Pout_a_kW_I3101"
xtpuicol_L1 = xtpuicol + "_L1_1"
xtpuicol_L2 = xtpuicol + "_L2_2"

# température moyenne de la batterie I7033
tempTbatcol = "BSP_Tbat_C_I7033_1"
# tensUbatcol = "BSP_Ubat_Vdc_I7030_1"
# ctIbatcol = "BSP_Ibat_Adc_I7031_1"

# Phase de charge de batterie.Dan ce système seule 3 phase devraient apparaitre:
# Charge de masse,(1 rouge), Absorbtion, (2 orange), et Mintient (4 Jaune)
xtphase_cols ={'1':['Charge de masse', 'red'],
                    '2':['Absorption', 'orange'],
                    '4':['Maintien', 'yellow']
               }

prodsol_dayIcol = 'I11007'
bilanEntree_dayIcol = 'I3081'
bilanSortie_dayIcol = 'I3083'
ahCharge_dayIcol = "I7007"
ahDecharge_dayIcol = "I7008"
dayStat_cols = [prodsol_dayIcol,
                                  bilanEntree_dayIcol,
                                  bilanSortie_dayIcol,
                                  ahCharge_dayIcol,
                                  ahDecharge_dayIcol]

time_txt_cols = [db_timecol]
time_real_cols =  ["XT_Ubat_MIN_Vdc_I3090_L1",
"XT_Ubat_MIN_Vdc_I3090_L2",
"XT_Uin_Vac_I3113_L1",
"XT_Uin_Vac_I3113_L2",
"XT_Iin_Aac_I3116_L1",
"XT_Iin_Aac_I3116_L2",
"XT_Pout_kVA_I3098_L1",
"XT_Pout_kVA_I3098_L2",
"XT_Pout_kVA_I3097_L1",
"XT_Pout_kVA_I3097_L2",
"XT_Fout_Hz_I3110_L1",
"XT_Fout_Hz_I3110_L2",
"XT_Fin_Hz_I3122_L1",
"XT_Fin_Hz_I3122_L2",
"XT_Phase_I3010_L1",
"XT_Phase_I3010_L2",
"XT_Mode_I3028_L1",
"XT_Mode_I3028_L2",
"XT_Transfert_I3020_L1",
"XT_Transfert_I3020_L2",
"XT_E_CMD_I3086_L1",
"XT_E_CMD_I3086_L2",
"XT_Aux_1_I3054_L1",
"XT_Aux_1_I3054_L2",
"XT_Aux_2_I3055_L1",
"XT_Aux_2_I3055_L2",
"XT_Ubat_Vdc_I3092_L1_1",
"XT_Ubat_Vdc_I3092_L2_2",
"XT_Ibat_Adc_I3095_L1_1",
"XT_Ibat_Adc_I3095_L2_2",
"XT_Pin_a_kW_I3119_L1_1",
"XT_Pin_a_kW_I3119_L2_2",
"XT_Pout_a_kW_I3101_L1_1",
"XT_Pout_a_kW_I3101_L2_2",
"XT_Tp1_MAX_C_I3103_L1_1",
"XT_Tp1_MAX_C_I3103_L2_2",
"VT_PsoM_kW_I11043_1",	 ### ajout VT
"VT_PsoM_kW_I11043_ALL",
"VT_Mode_I11016_1",
"VT_Tp1M_C_I11045_1",
"VT_UpvM_Vdc_I11041_1",
"VT_IbaM_Adc_I11040_1",
"VT_UbaM_Vdc_I11039_1", 
"VT_Phase_I11038_1",
"VT_E_CMD_I11082_1",
"VT_Aux_1_I11061_1",
"VT_Aux_2_I11062_1",  
"BSP_Ubat_Vdc_I7030_1",
"BSP_Ibat_Adc_I7031_1",
"BSP_SOC_I7032_1",
"BSP_Tbat_C_I7033_1",
"Solar_power_ALL_kW_I17999_ALL",
"DEV_XT_DBG1_I3140_1",
"DEV_BSP_locE_I7059_1",
"DEV_VT_locEr_I11076_1",              
"DEV_SYS_MSG_I17997_1",
"DEV_SYS_SCOM_ERR_I17998_1"]

time_added_cols = [col.replace('_L1', '_L1_L2') for col in time_real_cols
    if col.endswith('_L1') and col.replace('_L1', '_L2') in time_real_cols
                   and not col.replace('_L1', '_L1_L2')  in time_real_cols]


## somme de colonnes ajoutées par calcul
# time_added_cols = ["XT_Iin_Aac_I3116_tot",
#                    "XT_Pin_a_kW_I3119_tot",
#                    "XT_Pout_a_kW_I3101_tot"]


day_txt_cols = [db_daycol]
# dayP_real_cols =  ['P1107', 'P1567', 'P1138', 'P1108', 'P1140', 'P1155', 'P1156', 'P1163',
#        'P1164', 'P6001']
dayP_cols =  ['P1107', 'P1567', 'P1138', 'P1108', 'P1140', 'P1155', 'P1156', 'P1163',
       'P1164', 'P6001']
dayP_real_cols = ([x + "_1" for x in dayP_cols] +
                  [x + "_2" for x in dayP_cols] +
                  [x + "_3" for x in dayP_cols])
dayI_cols = ['I3081', 'I3083', 'I7007', 'I7008', 'I11006', 'I11007', 'I15016',
       'I15017', 'I7053', 'I7054', 'I7055', 'I7056', 'I7067']
dayI_real_cols = ([x + "_1" for x in dayI_cols] +
                  [x + "_2" for x in dayI_cols])

#assert nColsTime == len(time_txt_cols) + len(time_real_cols)

showcols_settings = {
    "XT_Ubat_MIN_Vdc_I3090_L1": {
        "lab" : "XT Ubat MIN L1 [Vdc]",
        "description": "tension de la batterie (battery voltage (minute min))", ### PAS TROUVE !!!
        "unit" : "Vdc",
        "scale": "",
        "step":""
    },
    "XT_Uin_Vac_I3113_L1": { ### PAS TROUVE !!!
        "lab" : "XT Uin L1 [Vac]",
        "description": "tension d'entrée ou du réseau public ou de la génératrice (input voltage (minute avg))",
        "unit": "Vac",
        "scale": "190-250V",
        "step":""
    },
    "XT_Iin_Aac_I3116_L1": {
        "lab" : "XT Iin L1 [Aac]",
        "description": "courant d'entrée de XTS (input current (minute avg))",
        "unit": "Aac",
        "scale": "auto" ,
        "step":"1A"
    },
    # "XT_Iin_Aac_I3116_tot": { ### PAS TROUVE !!!
    #     "lab" : "XT Iin L1+L2 [Aac]",
    #     "description": "somme Iin I3116 L1+L2 [calculated)",
    #     "unit": "Aac",
    #     "scale": "auto",
    #     "step": "1A"
    # },
    "XT_Pout_kVA_I3098_L1": {
        "lab" : "XT Pout L1 [kVA]",
        "description": "puissance de sortie (output power (minute avg))",
        "unit": "kVA",
        "scale": "auto",
        "step": "100W"
    },
    "XT_Pout_kVA_I3097_L1": {
        "lab" : "XT Pout L1 [kVA]",
        "description": "puissance de sortie+ (output power+ (minute max))",
        "unit": "kVA",
        "scale": "auto",
        "step": "100W"
    },
# Output frequency (minute avg)  (HZ)
    "XT_Fout_Hz_I3110_L1":  {
        "lab" : "XT Fout L1 [Hz]",
        "description": "",
        "unit": "Hz",
        "scale": "",
        "step": ""
    },
    "XT_Fout_Hz_I3110_L2": {
        "lab" : "XT Fout L2 [Hz]",
        "description": "",
        "unit": "Hz",
        "scale": "",
        "step": ""
    },
    "XT_Fin_Hz_I3122_L1": {
        "lab" : "XT Fin L1 [Hz]",
        "description": "fréquence du réseau (stable, < 51 Hz) ou de la génératrice (moins stable, > 51 Hz) (input frequency (minute avg))",
        "unit": "Hz",
        "scale": "45-55",
        "step": ""
    },
# Phase de charge de batterie (----,
    # Ch.masse, Absorpt., Egalise, Maintien, Maint.ré, Abs.pér.,
    # Brassage, Formage) (3010) # Battery cycle phase
#0:Invalid value,1:Bulk,2:Absorpt.,3:Equalise, 4:Floating,5:R.float.,6:Per.abs.,7:Mixing,8:Forming
    "XT_Phase_I3010_L1": {
        "lab" : "XT Phase L1 [enum]",
        "description": "phase de charge de batterie (battery cycle phase) (1/rouge : charge de masse, 2/orange : absorbtion, 4/jaune : maintien)",
        "unit": "CAT",
        "scale": "1-4",
        "step": "1"
    },
# Mode de fonctionnement (----, Onduleur, Chargeur, Boost, Injection) (3028)
    # Operating state
    # give current working mode of the inverter
#0:Invalid value,1:Inverter,2:Charger,3:Boost,4:Injection
    "XT_Mode_I3028_L1" :{
        "lab" : "XT Mode L1 [enum]",
        "description": "current working mode of the inverter (0=invalid, 1=inverter, 2=charger, 3=boost, 4=injection)",
        "unit": "CAT",
        "scale": "1-4",
        "step": "1"
    },
    "XT_Mode_I3028_L2" : {
        "lab" : "XT Mode L2 [enum]",
        "description": "current working mode of the inverter (0=invalid, 1=inverter, 2=charger, 3=boost, 4=injection)",
        "unit": "CAT",
        "scale": "1-4",
        "step": "1"
    },
    "XT_Transfert_I3020_L1": {
#Etat du relais de transfert (Ouvert, Fermé) (3020)
        # State of transfer relay
        "lab": "XT Transfert L1 [bool]",
        "description": "présence du réseau sur les entrées (0=absent, 1=présent) (state of transfer relay (0: opened, 1:closed))",
        "unit": "CAT",
        "scale": "0-1",
        "step": "1"
    },
#Etat de l'entree de commande (E CMD 0, E CMD 1)(3086)
    # Remote entry state 0:RM EN 0 -     # 1:RM EN 1
    "XT_E_CMD_I3086_L1" : {
#Etat du relais de transfert (Ouvert, Fermé) (3020)
        # State of transfer relay
        "lab": "XT E CMD L1 [bool]",
        "description": "présence du réseau sur les entrées (0=absent, 1=présent) (state of transfer relay (0: opened, 1:closed))",
        "unit": "CAT",
        "scale": "0-1",
        "step": "1"
    },
#Etat de l'entree de commande (E CMD 0, E CMD 1)(3086)
    "XT_E_CMD_I3086_L2" :{
#Etat du relais de transfert (Ouvert, Fermé) (3020)
        # State of transfer relay
        "lab": "XT E CMD L2[bool]",
        "description": "présence du réseau sur les entrées (0=absent, 1=présent) (state of transfer relay (0: opened, 1:closed))",
        "unit": "CAT",
        "scale": "0-1",
        "step": "1"
    },
#Mode relais auxiliaire 1 (----, A, I, M, M, G) (3054)
# Relay aux 1 mode 0:Invalid value,1:A, 2:I ,3:M,4:M,5:G
    "XT_Aux_1_I3054_L1" : {
#Etat du relais de transfert (Ouvert, Fermé) (3020)
        # State of transfer relay
        "lab": "XT Aux 1 L1 [enum]",
        "description": "mode relais auxiliaire (0=absent, 1=A, 2=I, 3=M, 4=M, 5=G)",
        "unit": "CAT",
        "scale": "0-1",
        "step": "1"
    },
    # Mode relais auxiliaire 1 (----, A, I, M, M, G) (3054)
    "XT_Aux_1_I3054_L2" : {
#Etat du relais de transfert (Ouvert, Fermé) (3020)
        # State of transfer relay
        "lab": "XT Aux 1 L2 [enum]",
        "description": "mode relais auxiliaire (0=absent, 1=A, 2=I, 3=M, 4=M, 5=G)",
        "unit": "CAT",
        "scale": "0-1",
        "step": "1"
    },
    # Mode relais auxiliaire 2 (----, A, I, M, M, G) (3055)
    # Relay aux 2 mode 0:Invalid value,1:A, 2:I ,3:M,4:M,5:G
    "XT_Aux_2_I3055_L1" : {
#Etat du relais de transfert (Ouvert, Fermé) (3020)
        # State of transfer relay
        "lab": "XT Aux 2 L1 [enum]",
        "description": "mode relais auxiliaire (0=absent, 1=A, 2=I, 3=M, 4=M, 5=G)",
        "unit": "CAT",
        "scale": "0-1",
        "step": "1"
    },
    "XT_Aux_2_I3055_L2" : {
#Etat du relais de transfert (Ouvert, Fermé) (3020)
        # State of transfer relay
        "lab": "XT Aux 2 L2 [enum]",
        "description": "mode relais auxiliaire (0=absent, 1=A, 2=I, 3=M, 4=M, 5=G)",
        "unit": "CAT",
        "scale": "0-1",
        "step": "1"
    },
### Battery voltage (minute avg) (Adc)
    "XT_Ubat_Vdc_I3092_L1_1" : {
        "lab" : "XT Ubat L1 [Vdc]",
        'description' : 'Battery voltage (minute avg)',
        "unit" : "Adc"},
    "XT_Ubat_Vdc_I3092_L2_2" : {
        'lab':"XT Ubat L2 [Vdc]",
            'description' : 'Battery voltage (minute avg)',
                                "unit" : "Adc"},
### Battery charge current (minute avg)  (Adc)
    "XT_Ibat_Adc_I3095_L1_1" : {
        "lab" : "XT Ibat L1 [Adc]",
        'description' : 'Battery charge current (minute avg)',
        "unit" : "Adc"},
    "XT_Ibat_Adc_I3095_L2_2" : {
        "lab" : "XT Ibat L2 [Adc]",
            'description' : 'Battery charge current (minute avg)',
                                "unit" : "Adc"},
    "XT_Pin_a_kW_I3119_L1_1": { ### PAS TROUVé
        "lab" : "XT Pin L1 [kW]",
        "description": "puissance tirée du réseau (>0) ou injectée sur le réseau (<0)  (input active power (minute avg))",
        "unit": "kW",
        "scale": "",
        "step": ""
    },
    # "XT_Pin_a_kW_I3119_tot": {
    #     "lab": "XT Pin L1+L2 [kW]",
    #     "description": "somme Pin I3119 L1+L2 (calculated)",
    #     "unit": "kW",
    #     "scale": "auto",
    #     "step": "0.01"
    # },
    "XT_Pout_a_kW_I3101_L1_1": {
        "lab" : "XT Pout L1 [kW]",
        "description": "puissance de sortie des circuits secourus (output active power (minute avg))",
        "unit": "kW",
        "scale": "",
        "step": ""
    },
    # "XT_Pout_a_kW_I3101_tot": {
    #     "lab": "XT Pout L1+L2 [kW]",
    #     "description": "somme Pout I3101 L1+L2 (calculated)",
    #     "unit": "kW",
    #     "scale": "auto",
    #     "step": "0.01"
    # },
#### "electronic temperature 1+ (minute max) (°C)",
    "XT_Tp1_MAX_C_I3103_L1_1": {
        "lab" : "XT Tp1 MAX L1 1 [°C]",
        "description":  "electronic temperature 1 (minute max)",
        "unit": "°C",
        "scale": "",
        "step": ""
    },

"VT_PsoM_kW_I11043_1": {
    "lab" : "VT PsoM 1 [kW]",
        "description": "PV power (min. avg)",
        "unit": "kW",
        "scale": "",
        "step":""
    },
"VT_PsoM_kW_I11043_ALL": {
    "lab":"VT PsoM ALL [kW]",
        "description": "PV power (min. avg)",
        "unit": "kW",
        "scale": "",
        "step":""
    },
"VT_Mode_I11016_1": {
    "lab" : "VT Mode 1 [enum]",
        "description": "Operating mode (0:Night, 1:StartUp,3:Charger,5:Security,6:OFF,8-12:Charge)",
        "unit": "kW",
        "scale": "",
        "step":""
    },

"VT_Tp1M_C_I11045_1": {
    "lab" : "VT Tp1M 1 [°C]",
        "description": "Electronic temperature 1 (min. avg)",
        "unit": "°C",
        "scale": "",
        "step":""
    },
"VT_UpvM_Vdc_I11041_1": {
    "lab" : "VT UpvM Vdc 1 [Vdc]",
        "description": "PV voltage (minute avg)",
        "unit": "Vdc",
        "scale": "",
        "step":""
    },
"VT_IbaM_Adc_I11040_1": {
        "lab": "VT IbaM 1 [Adc]",
    "description": "Battery current (minute avg)",
        "unit": "Adc",  #float
        "scale": "",
        "step":""
    },
"VT_UbaM_Vdc_I11039_1": {
    "lab" : "VT UbaM 1 [Vdc]",
        "description": "Battery voltage (minute avg)",
        "unit": "Vdc",
        "scale": "",
        "step":""
    },

"VT_Phase_I11038_1": {
    "lab" : "VT Phase 1",
        "description": "Battery cycle phase (0:Bulk, 1:Absorpt., 2:Equalize, 3:Floating, 6:R.float., 7:Per.abs.)",
        "unit": "",
        "scale": "",
        "step":""
    },
"VT_E_CMD_I11082_1": {
        "lab" : "VT E CMD 1",
        "description": "Remote entry state (0:RM EN 0, 1:RM EN 1)",
        "unit": "",
        "scale": "",
        "step":""
    },
"VT_Aux_1_I11061_1": {
            "lab":"VT Aux 1 [bool]",
        "description": "State of auxiliary relay 1 (0:Opened, 1:Closed)",
        "unit": "",
        "scale": "0-1",
        "step":"1"
    },
"VT_Aux_2_I11062_1": {
    "lab" :"VT Aux 2 [bool]",
        "description": "State of auxiliary relay 2 (0:Opened, 1:Closed)",
        "unit": "",
        "scale": "0-1",
        "step":"1"
    },


## VT manquants dans les premiers fichiers 


    "BSP_Ubat_Vdc_I7030_1": {
         "lab" : "BSP Ubat 1 [Vdc]",
        "description": "tension de la batterie (battery voltage - minute avg)",
        "unit": "Vdc",
        "scale": "40-60",
        "step": ""
    },
    "BSP_Ibat_Adc_I7031_1": {
        "lab": "BSP Ibat 1 [Adc]",
        "description": "courant de la batterie (battery current minute avg)",
        "unit": "Adc",
        "scale": "-30-30",
        "step": ""
    },
# "State of Charge (SOC) (minute avg)" (%)
    "BSP_SOC_I7032_1":  {
        "lab": "BSP SOC 1 [%]",
        "description": "state of charge (minute avg)",
        "unit": "%",
        "scale": "0-100",
        "step": ""
    },
    "BSP_Tbat_C_I7033_1": {
        "lab": "BSP Tbat C [°C]",
        "description": "température de la batterie (battery temp. minute avg)",
        "unit": "°C",
        "scale": "-30-30",
        "step": ""
    },
    "Solar_power_ALL_kW_I17999_ALL":  {
        "lab": "Solar power ALL [kW]",
        "description": "solar power ALL (pas trouvé)",
        "unit": "kW",
        "scale": "",
        "step": ""
    },
    "DEV_XT_DBG1_I3140_1":  {
        "lab": "DEV XT DBG1 1",
        "description": "system debug",
        "unit": "NA",
        "scale": "NA",
        "step": "NA"
    },# System debug 1
    "DEV_BSP_locE_I7059_1":  {
        "lab": "DEV BSP locE 1",
        "description": "Local daily communication error counter (CAN)",
        "unit": "",
        "scale": "",
        "step": ""
    },# local daily communication error counter (CAN)
	"DEV_VT_locEr_I11076_1": { 
		"lab":"DEV VT locEr 1 [int]",
            "description": "Local daily communication error counter (CAN)",
		"unit": "",
		"scale": "0-1",
		"step":"1"
	},
    "DEV_SYS_MSG_I17997_1":  {
        "lab": "pas trouvé",
        "description": "pas trouvé",
        "unit": "NA",
        "scale": "NA",
        "step": "NA"
    }, # PAS trouvé
    "DEV_SYS_SCOM_ERR_I17998_1":  {
        "lab": "pas trouvé",
        "description": "pas trouvé",
        "unit": "NA",
        "scale": "NA",
        "step": "NA"
    }# pas trouv é
}


for icol in time_added_cols:
    if not icol in showcols_settings:
        showcols_settings[icol] =  showcols_settings[icol.replace('_L1_L2', '_L1')]
        showcols_settings[icol]['lab'] =showcols_settings[icol]['lab'].replace("L1", "L1+L2")
        showcols_settings[icol]['description'] =showcols_settings[icol]['description'].replace("L1", "L1+L2")

showcols_settings["XT_Tp1_MAX_C_I3103_L2_2"] = showcols_settings["XT_Tp1_MAX_C_I3103_L1_1"]
showcols_settings["XT_Pout_kVA_I3097_L2"] = showcols_settings["XT_Pout_kVA_I3097_L1"]
showcols_settings["XT_Ubat_MIN_Vdc_I3090_L2"] = showcols_settings["XT_Ubat_MIN_Vdc_I3090_L1"]
showcols_settings["XT_Uin_Vac_I3113_L2"] = showcols_settings["XT_Uin_Vac_I3113_L1"]
showcols_settings["XT_Iin_Aac_I3116_L2"] = showcols_settings["XT_Iin_Aac_I3116_L1"]
showcols_settings["XT_Pout_kVA_I3098_L2"] = showcols_settings["XT_Pout_kVA_I3098_L1"]
showcols_settings["XT_Fin_Hz_I3122_L2"] = showcols_settings["XT_Fin_Hz_I3122_L1"]
showcols_settings["XT_Phase_I3010_L2"] = showcols_settings["XT_Phase_I3010_L1"]
showcols_settings["XT_Transfert_I3020_L2"] = showcols_settings["XT_Transfert_I3020_L1"]
showcols_settings["XT_Pin_a_kW_I3119_L2_2"] = showcols_settings["XT_Pin_a_kW_I3119_L1_1"]
showcols_settings["XT_Pout_a_kW_I3101_L2_2"] = showcols_settings["XT_Pout_a_kW_I3101_L1_1"]

assert set(showcols_settings.keys()) == set(time_real_cols+time_added_cols)


IvarsOfInterset = ["I3081",
                   "I3083",
                   "I7007",
                   "I7008",
                   "I11006",
                   "I11007"]

dayIcols_settings={
"I7007": {
    "lab" : "Charge du jour [Ah]",
    "description": "Energie chargée (daily) (Ah charged today)",
    "unit": "Ah",
    "scale": "",
    "step": "",
    "source":"BSP"
},
"I7008": {
    "lab": "Décharge du jour [Ah]",
    "description": "Energie déchargée (daily) (Ah discharged today)",
    "unit": "Ah",
    "scale": "",
    "step": "",
    "source":"BSP"
},
"I11006": {### VarioTrack
    "lab" : "Production du jour [Ah]",
    "description": "Production (daily) (Production in  Ah for the current day)",
    "unit": "Ah",
    "scale": "",
    "step": "",
    "source": "VarioTrack"
},
"I11007": {### VarioTrack
    "lab" :"Production du jour [kWh]",
    "description": "Production solaire (daily) (Production in  kWh for the current day)",
    "unit": "kWh",
    "scale": "",
    "step": "",
    "source": "VarioTrack"
},
    # Energie AC-In de la journée en cours (3081)
# XTender
"I3081": { # Bilan journalier de l'energie (kWh) prise ou injectée (-) sur le réseau (entrée) L1
    "lab" : "Energie AC-In du jour [kWh]",
    "description": "Energie (bilan) sur les entrées (daily) (energy AC-In from the current day)",
    "unit": "kWh",
    "scale": "",
    "step": "",
    "source": "XTender"
},
    # nergie consommée de la journee en cours
    # XTender
"I3083": { # Bilan journalier de l'energie (kWh) conssommée sur les 2 circuit secouru L1
    "lab" : "Energie consommée du jour [kWh]",
    "description": "Energie (bilan) sur les sorties (daily) (consumers energy of the current day (sortie réseau AC-Out))",
    "unit": "kWh",
    "scale": "",
    "step": "",
    "source": "XTender"
},
"I15016": {
    "lab" : "Production PV du jour [Ah]",
    "description": "Production PV in (Ah) for the current day",
    "unit": "Ah",
    "scale": "",
    "step": "",
    "source": "Variostring"
},
"I15017": {
"lab" : "Production PV du jour [kWh]",
    "description": "Production PV in (kWh) for the current day",
    "unit": "kWh",
    "scale": "",
    "step": "",
    "source": "Variostring"
},
"I7053": {
"lab" : "Type de batterie",
    "description": "Battery Type",
    "unit": "",
    "scale": "",
    "step": "",
    "source": "Xcom-CAN BMS"
},
"I7054": {
    "lab" : "Version du BMS",
    "description": "BMS Version",
    "unit": "",
    "scale": "",
    "step": "",
    "source": "Xcom-CAN BMS"
},
"I7055": {
    "lab" : "Capacité de batterie [Ah]",
    "description": "Nominal or remaining battery capacity",
    "unit": "Ah",
    "scale": "",
    "step": "",
    "source": "Xcom-CAN BMS"
},
"I7056": {
    "lab": "Reserve ID fabricant",
    "description": "Reserved Manufacturer ID",
    "unit": "",
    "scale": "",
    "step": "",
    "source": "Xcom-CAN BMS"
},
"I7067": {
    "lab": "Manufacturer name",
    "description": "Manufacturer name",
    "unit": "",
    "scale": "0-3",
    "step": "1",
    "source": "Xcom-CAN BMS"
}
}


dayPcols_settings={
"P1107": {
    "description": "Maximum current of AC source (Input limit)",
    "unit": "Aac",
    "scale": "",
    "step": "",
    "source": "XTender"
},
"P1567": {
    "description": "Second maximum current of the AC source (Input limit)",
    "unit": "Aac",
    "scale": "",
    "step": "",
    "source": "XTender"
},
"P1138": {
    "description": "Battery charge current",
    "unit": "Adc",
    "scale": "0-200",
    "step": "",
    "source": "XTender"
},
"P1108": {
    "description": "Battery undervoltage level without load",
    "unit": "Vdc",
    "scale": "",
    "step": "",
    "source": "XTender"
},
"P1140": {
    "description": "Floating voltage",
    "unit": "Vdc",
    "scale": "",
    "step": "",
    "source": "XTender"
},
    "P1155": {
    "description": "Absorption phase allowed (0=no, 1=yes)",
    "unit": "",
    "scale": "",
    "step": "",
    "source": "XTender"
},
"P1156": {
    "description": "Absorption voltage",
    "unit": "Vdc",
    "scale": "",
    "step": "",
    "source": "XTender"
},
"P1163": {
    "description": "Equalization allowed (0=no, 1=yes)",
    "unit": "",
    "scale": "",
    "step": "",
    "source": "XTender"
},
"P1164": {
    "description": "Equalization voltage",
    "unit": "Vdc",
    "scale": "37.9-72",
    "step": "0.1",
    "source": "XTender"
},
"P6001": {
    "description": "Nominal capacity",
    "unit": "Ah",
    "scale": "20-20000",
    "step": "10",
    "source": "XTender"
}
}

### Xtender
# 1107 Maximum current of AC source (Input limit) (Aac]
# 1567 Second maximum current of the AC source (Input limit) (Aac]
# 1138 Battery charge current [Adc] 0-200 FLOAT def. 60
# 1108 Battery undervoltage level without load Vdc 36-72 FLOAT def. 46.3
# 1140 Floating voltage Vdc def. 54.4 37.9-72 FLOAT
# 1155 Absorption phase allowed def. 1:Yes ; 0:No 1:Yes BOOL
# 1156 Absorption voltage Vdc 57.6 37.9 72  FLOAT
# 1163 Equalization allowed 0:No 0:No 1:Yes BOOL
# 1164 Equalization voltage Vdc 62.4 37.9 72 FLOAT step 0.1
# 6001 6001 Nominal capacity Ah 110 20 20000 FLOAT 10
# missing_desc_cols_dayP = ["","","","","","",""]
# for icol in missing_desc_cols_dayP:
#     dayPcols_settings[icol] = { # Bilan journalier de l'energie [kWh] conssommée sur les 2 circuit secouru L1
#     "description": "-description manquante-"
# }

start_colsI = list(dayIcols_settings.keys())
for icol in start_colsI:
    dayIcols_settings[icol+"_1"] = dayIcols_settings[icol]
    dayIcols_settings[icol + "_2"] = dayIcols_settings[icol]

# start_colsP = list(dayPcols_settings.keys())
# for icol in start_colsP:
#     dayPcols_settings[icol + "_1"] = dayPcols_settings[icol]
#     dayPcols_settings[icol + "_2"] = dayPcols_settings[icol]
#     dayPcols_settings[icol + "_3"] = dayPcols_settings[icol]
# Configuration de la disposition des axes y
yaxis_layout = dict(
    title="yaxis title",
    titlefont=dict(color=timePlotLineCols[0]),
    tickfont=dict(color=timePlotLineCols[0]),
    showline=True,
    linewidth=2,
    linecolor='black'
)
yaxis2_layout = dict(
    title="yaxis2 title",
    titlefont=dict(color=timePlotLineCols[1]),
    tickfont=dict(color=timePlotLineCols[1]),
    overlaying="y",
    side="right",
    showline=True,
    linewidth=2,
    linecolor='black'
)
yaxis3_layout = dict(
    title="yaxis3 title",
    titlefont=dict(color=timePlotLineCols[2]),
    tickfont=dict(color=timePlotLineCols[2]),
    anchor="free",
    overlaying="y",
    autoshift=True,
    showline=True,
    linewidth=2,
    linecolor='black'
)
yaxis4_layout = dict(
    title="yaxis4 title",
    titlefont=dict(color=timePlotLineCols[3]),
    tickfont=dict(color=timePlotLineCols[3]),
    anchor="free",
    overlaying="y",
    side="right",
    autoshift=True,
    showline=True,
    linewidth=2,
    linecolor='black'
)
