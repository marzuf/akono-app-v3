from settings import *

tabname2tablab = dict()
tabname2tablab[dbTime_name] = "mesures minutées"
tabname2tablab[dbDayP_name] = "bilans journaliers P"
tabname2tablab[dbDayI_name] = "bilans journaliers I"

freq_colors = {'Réseau': 'blue', 'Génératrice': 'green',
              'Absence de source': 'red', 'Incertain': 'grey'}

navbtn_style = {
    'style': {'backgroundColor': '#2507cf', 'color': 'white'},
    'className': 'my-2'
}
# my-2 : Cette classe ajoute de l'espacement vertical (my = marge verticale) autour des boutons pour les séparer visuellement

I_colors = {'I3081': 'green', 'I3083': 'red'}


all_range_pickers = [
                        'range-picker-stat',
                        'range-picker-evotime',
                        'range-picker-analyseGraph',
                        'range-picker-subxtender',
                        'range-picker-subvariotrack',
                        'range-picker-subbsp',
                        'range-picker-subbat',
                        'range-picker-subminutes',
                        'range-picker-subdayI',
                    'range-picker-exportdata'
                            ]

all_confirm_dialogs = [
                    'confirm-dialog-stat',
                    'confirm-dialog-statgraph',
                   # 'confirm-dialog-evotime',
                    'confirm-dialog-evoDayIDBgraph',
                    'confirm-dialog-evoTimeDBgraph',
                    'confirm-dialog-evoDayPDBgraph',
                    'confirm-dialog-analyseGraph',
                    'confirm-dialog-subxtender',
                    'confirm-dialog-subvariotrack',
                    'confirm-dialog-subbsp',
                    'confirm-dialog-subbat',
                    'confirm-dialog-subminutes',
                    'confirm-dialog-subdayI',
                'confirm-dialog-exportdata'
                                 ]

xaxis_settings = dict(
            title='Temps',
            rangeslider=dict(visible=True),  # Add a range slider to the x-axis
            type="date"  # Set the x-axis type to date
        )