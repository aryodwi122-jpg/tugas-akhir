import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import os

st.set_page_config(layout="wide")
sns.set(style="whitegrid")

# =====================
# LOAD DATA
# =====================
zip_path = r"C:\Users\aryod\Downloads\Air-quality-dataset.zip"
extract_dir = r"C:\Users\aryod\Downloads\air_quality_data"

with zipfile.ZipFile(zip_path, 'r') as z:
    z.extractall(extract_dir)

csv_files = []
for root, dirs, files in os.walk(extract_dir):
    for file in files:
        if file.endswith(".csv"):
            csv_files.append(os.path.join(root, file))

df_list = [pd.read_csv(f) for f in csv_files]
df = pd.concat(df_list, ignore_index=True)

# Cleaning
df['datetime'] = pd.to_datetime(df[['year','month','day','hour']])
df = df.sort_values("datetime")
df.set_index("datetime", inplace=True)
df = df.fillna(df.median(numeric_only=True))

# =====================
# SIDEBAR FILTER
# =====================
st.sidebar.header("Filter")
pollutant = st.sidebar.selectbox("Pilih variabel polusi:", ['PM2.5','PM10','NO2','SO2','CO','O3'])

# Filter Stasiun
stations = df['station'].unique().tolist()
station_selected = st.sidebar.selectbox("Pilih Stasiun:", stations)

# Filter dataframe sesuai stasiun
df_station = df[df['station'] == station_selected]




# =====================
# HEADER
# =====================
st.title(" Air Quality Dashboard Beijing")
st.write(f"### Stasiun terpilih: **{station_selected}**")

# =====================
# 1. TIMESERIES PLOT
# =====================
st.subheader(f"Tren Waktu: {pollutant} - {station_selected}")

fig, ax = plt.subplots(figsize=(14,5))
df_station[pollutant].plot(ax=ax) 
ax.set_title(f"Tren Waktu {pollutant} di Stasiun {station_selected}")
st.pyplot(fig)

# =====================
# 2. DISTRIBUTION
# =====================
st.subheader(f"Distribusi {pollutant} - {station_selected}")

fig, ax = plt.subplots(figsize=(7,5))
sns.histplot(df_station[pollutant], bins=40, kde=True, ax=ax)
st.pyplot(fig)

# =====================
# 3. Korelasi Polutan
# =====================
st.subheader(f"Heatmap Korelasi Polutan - {station_selected}")

fig, ax = plt.subplots(figsize=(10,6))
sns.heatmap(df[['PM2.5','PM10','NO2','SO2','CO','O3']].corr(),
            cmap='coolwarm', annot=True, ax=ax)
st.pyplot(fig)

# =====================
# 4. Average per Month
# =====================
st.subheader(f"Rata-rata PM2.5 per Bulan - {station_selected}")
monthly_avg = df_station.groupby(df_station.index.month)['PM2.5'].mean()
fig, ax = plt.subplots(figsize=(10,5))
monthly_avg.plot(marker='o', ax=ax)
ax.set_xlabel("Bulan")
ax.set_ylabel("PM2.5")
st.pyplot(fig)

# =====================
# 5. Perbandingan Antar Stasiun (Enhanced)
# =====================
st.subheader(f"Perbandingan {pollutant} Antar Stasiun (Lebih Mudah Dibaca)")

fig, ax = plt.subplots(figsize=(14,6))

# Color palette otomatis sebanyak jumlah stasiun
colors = sns.color_palette("tab10", n_colors=len(stations))

for idx, st_name in enumerate(stations):
    df_temp = df[df['station'] == st_name][pollutant] \
                .resample('D').mean() \
                .rolling(7).mean()               
    ax.plot(df_temp.index, df_temp.values,
            label=st_name,
            linewidth=2,                         
            alpha=0.85,                          
            color=colors[idx])

ax.set_title(f"Perbandingan Harian {pollutant} Antar Stasiun (Smoothing 7 hari)")
ax.set_xlabel("Tanggal")
ax.set_ylabel(pollutant)
ax.legend(title="Stasiun", bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# =====================
# 6. Ranking Stasiun berdasarkan Polutan
# =====================
st.subheader(f"Ranking Stasiun berdasarkan rata-rata {pollutant}")

rank_df = df.groupby("station")[pollutant] \
            .mean() \
            .sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(10,5))
rank_df.plot(kind="bar", ax=ax)

ax.set_ylabel("Rata-rata Konsentrasi")
ax.set_xlabel("Stasiun")
ax.set_title(f"Ranking Stasiun - {pollutant}")
plt.xticks(rotation=45)

st.pyplot(fig)



  