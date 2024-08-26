
from dash.dependencies import Input, Output
from app_settings import *

all_pickers = ['date-picker-dbdata'] + all_range_pickers

# def register_callbacks(app):

    ##################################################################################
    ######################################### DATE PICKER HANDLING
    ##################################################################################
    # @app.callback(
    #     [Output(picker_id, 'style') for picker_id in all_pickers],
    #     [
    #         Input('tabs-example', 'value'),
    #         Input('subtabs-appareils', 'value'),
    #         Input('subtabs-fonctions', 'value'),
    #         Input('subtabs-dashboard', 'value'),
    #         Input('subtabs-data', 'value')        ]
    # )
    # def show_hide_datepickers(tab, subtab_appareils, subtab_fonctions,
    #                           subtab_dashboard, subtab_data):
    #     # styles = {
    #     #     'date-picker-dbdata': {'display': 'none'},
    #     #     'range-picker-evotime': {'display': 'none'},
    #     #     'range-picker-stat': {'display': 'none'},
    #     #     'range-picker-analyseGraph': {'display': 'none'},
    #     #     'range-picker-subxtender': {'display': 'none'},
    #     #     'range-picker-subvariotrack': {'display': 'none'},
    #     #     'range-picker-subbsp': {'display': 'none'},
    #     #     'range-picker-subbat': {'display': 'none'},
    #     #     'range-picker-subminutes': {'display': 'none'},
    #     #     'range-picker-subdayI': {'display': 'none'},
    #     #     'range-picker-exportdata': {'display': 'none'}
    #     # }
    #
    #     styles = {picker: {'display': 'none'} for picker in all_pickers}
    #
    #     if tab == "tab-data" :
    #         if subtab_data == 'subtab-showDB':
    #             styles['date-picker-dbdata'] = {'display': 'block', 'margin': '20px 0'}
    #         elif subtab_data == 'subtab-exportDB':
    #             styles['range-picker-exportdata'] = {'display': 'block', 'margin': '20px 0'}
    #     elif tab == 'tab-evotime':
    #         styles['range-picker-evotime'] = {'display': 'block', 'margin': '20px 0'}
    #     elif tab == 'tab-stat':
    #         styles['range-picker-stat'] = {'display': 'block', 'margin': '20px 0'}
    #     elif tab == 'tab-analyseGraph':
    #         styles['range-picker-analyseGraph'] = {'display': 'block', 'margin': '20px 0'}
    #     elif tab == 'tab-appareils':
    #         if subtab_appareils == "subtab-xtender":
    #             styles['range-picker-subxtender'] = {'display': 'block', 'margin': '20px 0'}
    #         elif subtab_appareils == "subtab-variotrack":
    #             styles['range-picker-subvariotrack'] = {'display': 'block', 'margin': '20px 0'}
    #         elif subtab_appareils == "subtab-bsp":
    #             styles['range-picker-subbsp'] = {'display': 'block', 'margin': '20px 0'}
    #     elif tab == 'tab-fonctions':
    #         if subtab_fonctions == "subtab-batterie":
    #             styles['range-picker-subbat'] = {'display': 'block', 'margin': '20px 0'}
    #     elif tab == 'tab-dashboard':
    #         if subtab_dashboard == "subtab-minutesdata":
    #             styles['range-picker-subminutes'] = {'display': 'block', 'margin': '20px 0'}
    #         elif subtab_dashboard == "subtab-dayIdata":
    #             styles['range-picker-subdayI'] = {'display': 'block', 'margin': '20px 0'}
    #
    #     return [styles[key] for key in styles]
    #


def register_callbacks(app):

    @app.callback(
        [Output(picker_id, 'style') for picker_id in all_pickers] +
        [Output(picker_id, 'min_date_allowed') for picker_id in all_pickers] +
        [Output(picker_id, 'max_date_allowed') for picker_id in all_pickers] +
        [Output(picker_id, 'disabled_days') for picker_id in all_pickers],
        [
            Input('tabs-example', 'value'),
            Input('subtabs-appareils', 'value'),
            Input('subtabs-fonctions', 'value'),
            Input('subtabs-dashboard', 'value'),
            Input('subtabs-data', 'value'),
            Input('stored_timeDB', 'data'),
            Input('stored_dayDB', 'data'),
            Input('stored_stat_dropdownval', 'data'),
            Input('stored_dataShowDB_dropdownval', 'data'),
            Input('stored_dataExportDB_dropdownval', 'data'),
            Input('stored_evotime_dropdownval', 'data'),
            Input('stored_analyseGraph_dropdownval', 'data'),
            Input('stored_appXT_dropdownval', 'data'),
            Input('stored_appBSP_dropdownval', 'data'),
            Input('stored_appVT_dropdownval', 'data'),
            Input('stored_fctBat_dropdownval', 'data'),
            Input('stored_dashMin_dropdownval', 'data'),
            Input('stored_dashDay_dropdownval', 'data'),
            # Input('evotimeTimeDB-db', 'value'),### marche pas car pas défini dès le départ
            # Input('tabstatgraph-db', 'value')# Selection de la base de données
        ]
    )
    def update_all_in_onedatepickers(tab, subtab_appareils, subtab_fonctions,
                           subtab_dashboard, subtab_data,
                           stored_timeDB_data, stored_dayDB_data,
                                     stat_dropdownval,
                                     dataShowDB_dropdownval,
                                     dataExportDB_dropdownval,
                                     evotime_dropdownval,
                                     analyseGraph_dropdownval,
                                     appXT_dropdownval,
                                     appBSP_dropdownval,
                                     appVT_dropdownval,
                                     fctBat_dropdownval,
                                     dashMin_dropdownval,
                                     dashDay_dropdownval
                                     ):
        # 1. Gestion des styles des DatePickerRange
        styles = {picker: {'display': 'none'} for picker in all_pickers}

        if tab == "tab-data":
            ## mettre dayI mélnage des 2
            selected_db = "both"
            if subtab_data == 'subtab-showDB':
                if dataShowDB_dropdownval == "stat_perso" :
                    styles['date-picker-dbdata'] = {'display': 'block', 'margin': '20px 0'}
            elif subtab_data == 'subtab-exportDB':
                if dataExportDB_dropdownval == "stat_perso" :
                    styles['range-picker-exportdata'] = {'display': 'block', 'margin': '20px 0'}
        elif tab == 'tab-evotime':
            # selected_db = evotime_selected_db
            if evotime_dropdownval == "stat_perso":
                styles['range-picker-evotime'] = {'display': 'block', 'margin': '20px 0'}
        elif tab == 'tab-stat':
            # selected_db = stat_selected_db
            if stat_dropdownval == "stat_perso" :
                styles['range-picker-stat'] = {'display': 'block', 'margin': '20px 0'}
        elif tab == 'tab-analyseGraph':
            if analyseGraph_dropdownval == "stat_perso" :
                styles['range-picker-analyseGraph'] = {'display': 'block', 'margin': '20px 0'}
            # que time
            selected_db = dbTime_name
        elif tab == 'tab-appareils':
            ## mélange des 2 -> on met dayI
            selected_db = "both"
            if subtab_appareils == "subtab-xtender":
                if appXT_dropdownval == "stat_perso" :
                    styles['range-picker-subxtender'] = {'display': 'block', 'margin': '20px 0'}
            elif subtab_appareils == "subtab-variotrack":
                if appVT_dropdownval == "stat_perso" :
                    styles['range-picker-subvariotrack'] = {'display': 'block', 'margin': '20px 0'}
            elif subtab_appareils == "subtab-bsp":
                if appBSP_dropdownval == "stat_perso" :
                    styles['range-picker-subbsp'] = {'display': 'block', 'margin': '20px 0'}
        elif tab == 'tab-fonctions':
            ## mélange des 2 -> on met dayI
            selected_db = "both"
            if subtab_fonctions == "subtab-batterie":
                if fctBat_dropdownval == "stat_preso":
                    styles['range-picker-subbat'] = {'display': 'block', 'margin': '20px 0'}
        elif tab == 'tab-dashboard':
            if subtab_dashboard == "subtab-minutesdata":
                selected_db = dbTime_name
                if dashMin_dropdownval == "stat_perso" :
                    styles['range-picker-subminutes'] = {'display': 'block', 'margin': '20px 0'}
            elif subtab_dashboard == "subtab-dayIdata":
                selected_db = dbDayI_name
                if dashDay_dropdownval == "stat_perso":
                    styles['range-picker-subdayI'] = {'display': 'block', 'margin': '20px 0'}

        selected_db = "both"
        # 2. Mise à jour des plages de dates disponibles
        if selected_db == dbTime_name or selected_db == "both":
            if stored_timeDB_data:
                time_df = pd.DataFrame(stored_timeDB_data)
                print(time_df)
                time_min_date = time_df[db_timecol].min()
                time_max_date = time_df[db_timecol].max()
                time_disabled_days = pd.date_range(time_min_date, time_max_date).difference(
                    time_df[db_timecol]).to_list()
                if selected_db == dbTime_name:
                    min_date, max_date, disabled_days = (time_min_date, time_max_date,
                                                         time_disabled_days)
            else:
                min_date, max_date, disabled_days = None, None, []

        if selected_db == dbDayI_name or selected_db == "both":
            if stored_dayDB_data:
                day_df = pd.DataFrame(stored_dayDB_data)
                day_min_date = day_df[db_daycol].min()
                day_max_date = day_df[db_daycol].max()
                day_disabled_days = pd.date_range(day_min_date, day_max_date).difference(
                    day_df[db_daycol]).to_list()
                if selected_db == dbDayI_name:
                    min_date, max_date, disabled_days = (day_min_date,
                                                         day_max_date,
                                                         day_disabled_days)

            else:
                min_date, max_date, disabled_days = None, None, []

        if selected_db == "both":
            if not stored_dayDB_data and not stored_timeDB_data :
                min_date, max_date, disabled_days = None, None, []
            elif not stored_dayDB_data:
                min_date, max_date, disabled_days = (time_min_date, time_max_date,
                                                     time_disabled_days)
            elif not stored_timeDB_data:
                min_date, max_date, disabled_days = (day_min_date,
                                                     day_max_date,
                                                     day_disabled_days)
            else :
                min_date = min([day_min_date]+ [time_min_date])
                max_date = max([day_min_date]+[time_min_date])
                disabled_days = [x for x in day_disabled_days if x in time_disabled_days]

        # else:
        #     # Si la base de données sélectionnée n'est ni time ni day, on sort
        #     min_date, max_date, disabled_days = None, None, []
        print("time_min date = ", time_min_date)
        print("time_max date = ", time_max_date)
        print("disabled_days = ", time_disabled_days)
        print("day_min date = ", day_min_date)
        print("day_max date = ", day_max_date)
        print("daydisabled_days = ", day_disabled_days)

        print("min date = ", min_date)
        print("max date = ", max_date)
        print("disabled_days = ", disabled_days)

        # 3. Retour des styles et des dates mises à jour pour les DatePickerRange
        return (
            [styles[picker] for picker in all_pickers]+  # Styles pour tous les pickers
            [min_date] * len(all_pickers)+  # Min date pour tous les pickers
            [max_date] * len(all_pickers)+  # Max date pour tous les pickers
            [disabled_days] * len(all_pickers)  # Disabled days pour tous les pickers
        )


    @app.callback(
        Output('stored_stat_dropdownval', 'data'),
        Input('statperiod-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period

    # @app.callback(
    #     Output('stored_dataShowDB_dropdownval', 'data'),
    #     Input('statperiod-dropdown', 'value')
    # )
    # def update_statperiod_store(selected_period):
    #     return selected_period


    @app.callback(
        Output('stored_dataExportDB_dropdownval', 'data'),
        Input('exportdata-period-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period

    @app.callback(
        Output('stored_evotime_dropdownval', 'data'),
        Input('evotimeperiod-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period
    @app.callback(
        Output('stored_analyseGraph_dropdownval', 'data'),
        Input('asGraphPeriod-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period

    @app.callback(
        Output('stored_appXT_dropdownval', 'data'),
        Input('subxtender-period-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period


    @app.callback(
        Output('stored_appBSP_dropdownval', 'data'),
        Input('subbsp-period-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period



    @app.callback(
        Output('stored_appVT_dropdownval', 'data'),
        Input('subvariotrack-period-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period



    @app.callback(
        Output('stored_fctBat_dropdownval', 'data'),
        Input('subbat-period-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period



    @app.callback(
        Output('stored_dashMin_dropdownval', 'data'),
        Input('subminutesdashb-period-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period



    @app.callback(
        Output('stored_dashDay_dropdownval', 'data'),
        Input('subdayIdashb-period-dropdown', 'value')
    )
    def update_statperiod_store(selected_period):
        return selected_period


