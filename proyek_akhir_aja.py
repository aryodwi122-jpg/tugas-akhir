import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile
import os


sns.set(style="whitegrid")

# ============================================================
# Gathering Data
# ============================================================
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

# ============================================================
# Assesing Data
print(df.info())
print(df.describe())
print("Missing values per column")
print(df.isnull().sum())
print("Duplikasi baris:",df.duplicated().sum())

# ============================================================
#Cleaning Data
#Convert ke datetime
df["datetime"] = pd.to_datetime(df[['year', 'month', 'day', 'hour']], errors='coerce')

# Buang row jika date time gagal dibuat
df.dropna(subset=["datetime"], inplace=True)

#Set datetime sebagai index
df = df.sort_values("datetime").set_index("datetime")

# Imputasi numeric
df.fillna(df.median(numeric_only=True), inplace=True)


# Imputasi Kategori
cat_cols = df.select_dtypes(include='object').columns
for col in cat_cols:
    df[col]=df[col].fillna(df[col].mode()[0])

# Hapus duplikasi timestamp
df = df[~df.index.duplicated(keep='last')]

print("\nData setelah cleaning:")
print(df.head())
print(df['station'].unique()[:20])

#EDA
## 1. Distribusi Polutan (PM2.5, PM10, NO2, SO2, CO, O3)
#
pollutants = ["PM2.5", "PM10", "NO2","SO2", "CO", "O3"]

plt.figure(figsize=(10,6))
sns.boxplot(data=df[pollutants])
plt.title("Distribusi Polutan Utama")
plt.xticks(rotation=45)
plt.yscale("log")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.show()


## 2. Korelasi Antar Variabel
numeric_df = df.select_dtypes(include=['int64', 'float64'])
if "No" in numeric_df.columns:
    numeric_df = numeric_df.drop(columns=["No"])
plt.figure(figsize=(14,10))
sns.heatmap(numeric_df.corr(),
            cmap='coolwarm',
            annot=True,
            fmt=".2f",
            linewidth=.5
)
plt.title("Heatmap Korelasi Numerik")
plt.show()

## 3. Tren Harian PM2.5
plt.figure(figsize=(12,6))
df["PM2.5"].plot(color="steelblue", linewidth=1)
plt.title("Tren Harian PM2.5", fontsize=14)
plt.xlabel("Tahun")
plt.ylabel(" Mikrogram per meter kubik µg/m³")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

## 4. Tren Bulanan
monthly_avg = df['PM2.5'].resample("ME").mean()

plt.figure(figsize=(15,5))
monthly_avg.plot(marker='o')
plt.xlabel("Bulan")
plt.ylabel(" Mikrogram per meter kubik (µg/m³)")
plt.title("Rata-rata PM2.5 per Bulan")
plt.show()


## 5. Tren Tahunan
yearly_avg = df.groupby(df.index.year)['PM2.5'].mean()

plt.figure(figsize=(15,5))
yearly_avg.plot(marker='o')
plt.xlabel("Tahun")
plt.ylabel("Mikrogram per meter kubik (µg/m³)")
plt.title("Rata-rata PM2.5 per Tahun")
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.show()

## 6. Tren Musiman
df['month'] = df.index.month
df['season'] = df['month'].map({
    12:'Winter', 1:'Winter', 2:'Winter',
    3:'Spring', 4:'Spring', 5:'Spring',
    6:'Summer', 7:'Summer', 8:'Summer',
    9:'Autumn', 10:'Autumn', 11:'Autumn'
})

plt.figure(figsize=(8,5))
df.groupby("season")["PM2.5"].mean().plot(kind="bar")
plt.title("Rata-rata PM2.5 per Musim")
plt.xlabel("Musim")
plt.ylabel("Mikrogram per meter kubik (µg/m³)")
plt.show()

## 7. Calendar Heatmap
df['day_of_year'] = df.index.dayofyear
calendar = df.pivot_table(values= "PM2.5", index=df.index.year, columns='day_of_year')
calendar = calendar.sort_index()

plt.figure(figsize=(18,6))
sns.heatmap(calendar, cmap='viridis', linewidth=0)
plt.title("Calendar Heatmap PM2.5")
plt.xlabel("Hari ke-")
plt.ylabel("Tahun")
plt.show()

## 8. Perbandingan Antar Stasiun
station_avg = df.groupby("station")["PM2.5"].mean().sort_values()

plt.figure(figsize=(12,6))
station_avg.plot(kind="bar")
plt.title("Rata-rata PM2.5 per Stasiun")
plt.xlabel("Stasiun")
plt.ylabel("PM2.5")
plt.xticks(rotation=45)
plt.show()
