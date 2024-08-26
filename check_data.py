from settings import *

from utils_fcts import *
db_file = 'data/akonolinga_database_v3.db'
conn = sqlite3.connect(db_file)

selected_period = "as_all"

start_date ="2024-01-19"
end_date ="2024-01-19"

start_date ="2023-12-01"
end_date ="2023-12-03"

dbname = dbTime_name

query = get_query_extractInterval(dbTime_name, "2024-04-20","2024-04-20")

dbname = dbDayI_name
selected_period="custom"
if selected_period == 'as_all':
    query = f"SELECT * FROM {dbname}"
    # interval_txt = " (tout)"
    # interval_txt = " Toutes les données"
else:
    query = get_query_extractInterval(dbname, start_date, end_date)
    print(query)
    # interval_txt = ("Période : " + start_date.strftime('%d/%m/%Y') + " - " +
    #                 end_date.strftime('%d/%m/%Y'))
all_df = pd.read_sql_query(query, conn)
conn.close()
puicol_tot = xtpuicol_L1 + "+" + xtpuicol_L2
all_df[puicol_tot] = all_df[xtpuicol_L1] + all_df[xtpuicol_L2]
import numpy as np

df = all_df[[db_timecol, puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()
df.loc[:, 'catTime'] = np.where(
    (pd.to_datetime(df[db_timecol]).dt.time >=
     datetime.strptime("08:00", "%H:%M").time()) &
    (pd.to_datetime(df[db_timecol]).dt.time <
     datetime.strptime("18:00", "%H:%M").time()),
    "Jour",
    "Nuit"
)
time_df = df[['catTime', puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()
tot_df = df[[puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()

catTime_counts = time_df['catTime'].value_counts().reset_index()
# VRAI si 1 jour sélectionné
if selected_period == 'as_day':
    assert (catTime_counts.loc[catTime_counts['catTime'] == 'Nuit', 'count'] == 840).all()
    assert (catTime_counts.loc[catTime_counts['catTime'] == 'Jour', 'count'] == 600).all()

all_df['time'] = pd.to_datetime(all_df['time'])
all_df['BSP_Tbat_C_I7033_1_dayMean'] = all_df.groupby(all_df['time'].dt.date)['BSP_Tbat_C_I7033_1'].transform('mean')

# Calcul des zones colorées
df = dayI_df
df['day'] = pd.to_datetime(df['day'])


# Fonction pour trouver les points d'intersection exacts
def find_intersections(df):
    intersections = []
    for i in range(len(df) - 1):
        if (df['I7007_1'][i] - df['I7008_1'][i]) * (df['I7007_1'][i + 1] - df['I7008_1'][i + 1]) < 0:
            x1, x2 = df['day'][i], df['day'][i + 1]
            y1_1, y2_1 = df['I7007_1'][i], df['I7007_1'][i + 1]
            y1_2, y2_2 = df['I7008_1'][i], df['I7008_1'][i + 1]

            # Calcul de l'intersection linéaire
            slope_1 = (y2_1 - y1_1) / (x2 - x1).days
            slope_2 = (y2_2 - y1_2) / (x2 - x1).days
            intersect_day = x1 + pd.Timedelta(days=(y1_2 - y1_1) / (slope_1 - slope_2))
            intersect_value = y1_1 + slope_1 * (intersect_day - x1).days
            intersections.append((intersect_day, intersect_value))
    return intersections


# Trouver les points d'intersection
intersections = find_intersections(df)

# Ajouter les points d'intersection aux données en utilisant pd.concat
intersect_df = pd.DataFrame(intersections, columns=['day', 'I7007_1'])
intersect_df['I7008_1'] = intersect_df['I7007_1']

df = pd.concat([df, intersect_df], ignore_index=True)

# Trier les données par jour
df=all_df
# df = df.sort_values('day').reset_index(drop=True)
df.set_index('day', inplace=True)
import matplotlib
matplotlib.use('TkAgg')  ### poru voir plots dans paycharm
import matplotlib.pyplot as plt
x = df.index
y1 = df['I7007_1']
y2 = df['I7008_1']

# Création de la figure
fig, ax = plt.subplots(figsize=(10, 6))

# Tracer les lignes
ax.plot(x, y1, label='I7007_1', color='blue')
ax.plot(x, y2, label='I7008_1', color='red')

# Remplir les zones entre les courbes
ax.fill_between(x, y1, y2, where=(y2 >= y1), facecolor='green', alpha=0.3, interpolate=True)
ax.fill_between(x, y1, y2, where=(y2 <= y1), facecolor='red', alpha=0.3, interpolate=True)

# Ajouter le titre et les légendes
ax.set_title('Fill Between with Interpolation')
ax.legend(loc='upper left')

# Afficher le graphique
plt.show()