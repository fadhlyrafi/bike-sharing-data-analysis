import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Fungsi untuk membuat DataFrame pelanggan per hari
def create_daily_rentals_df(df):
    daily_rentals_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    }).reset_index()
    daily_rentals_df.rename(columns={
        "cnt": "total_customers"
    }, inplace=True)
    
    return daily_rentals_df

# Fungsi untuk membuat DataFrame pelanggan berdasarkan musim
def create_byseason_df(df):
    byseason_df = df.groupby("season").agg({
        "cnt": "sum"
    }).reset_index()
    byseason_df.rename(columns={
        "cnt": "total_customers"
    }, inplace=True)
    
    return byseason_df

# Fungsi untuk membuat DataFrame pelanggan berdasarkan cuaca
def create_byweather_df(df):
    byweather_df = df.groupby("weathersit").agg({
        "cnt": "sum"
    }).reset_index()
    byweather_df.rename(columns={
        "cnt": "total_customers"
    }, inplace=True)
    
    return byweather_df

# Fungsi untuk membuat DataFrame pelanggan berdasarkan jam
def create_byhour_df(df):
    byhour_df = df.groupby("hr").agg({
        "cnt": "sum"
    }).reset_index()
    byhour_df.rename(columns={
        "cnt": "total_customers"
    }, inplace=True)
    byhour_df['hr'] = byhour_df['hr'].apply(lambda x: f"{x:02}.00")  # Format jam
    
    return byhour_df

# Load data
day_df = pd.read_csv("./data/day.csv")
hour_df = pd.read_csv("./data/hour.csv")

# Konversi kolom dteday menjadi format datetime
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

# Setup rentang waktu minimum dan maksimum untuk filter di dashboard
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# Sidebar untuk rentang waktu
with st.sidebar:
    st.markdown(
        """
        <h1 style='font-size: 50px; text-align: center;'>🚴‍♂️</h1>
        <h1 style='text-align: center; color: #1f77b4;'>Bike Sharing</h1>
        """,
        unsafe_allow_html=True
    )
    start_date, end_date = st.date_input(
        label='Rentang Waktu', 
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter data berdasarkan rentang waktu
filtered_day_df = day_df[(day_df["dteday"] >= str(start_date)) & (day_df["dteday"] <= str(end_date))]
filtered_hour_df = hour_df[(hour_df["dteday"] >= str(start_date)) & (hour_df["dteday"] <= str(end_date))]

# Buat DataFrame untuk analisis
daily_rentals_df = create_daily_rentals_df(filtered_day_df)
byseason_df = create_byseason_df(filtered_day_df)
byweather_df = create_byweather_df(filtered_day_df)
byhour_df = create_byhour_df(filtered_hour_df)

# # Menampilkan data hasil analisis di Streamlit
# st.write("### Total Customers per Day")
# st.dataframe(daily_rentals_df)

# st.write("### Total Customers by Season")
# st.dataframe(byseason_df)

# st.write("### Total Customers by Weather")
# st.dataframe(byweather_df)

# st.write("### Total Customers by Hour")
# st.dataframe(byhour_df)

# Mulai layouting
st.header('Bike Sharing Dashboard 🚴‍♂️')

# Bagian Daily Rentals
st.subheader('Daily Rentals')

col1, col2 = st.columns(2)

with col1:
    total_rentals = daily_rentals_df.total_customers.sum()
    st.metric("Total Rentals", value=total_rentals)

with col2:
    avg_rentals_per_day = round(daily_rentals_df.total_customers.mean(), 2)
    st.metric("Avg Rentals per Day", value=avg_rentals_per_day)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rentals_df["dteday"],
    daily_rentals_df["total_customers"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Membuat kamus untuk season
season_mapping = {
    1: "Spring",
    2: "Summer",
    3: "Fall",
    4: "Winter"
}

# Menerapkan terjemahan pada kolom season
byseason_df['season_name'] = byseason_df['season'].map(season_mapping)

# Menemukan season dengan jumlah total_customers tertinggi
max_season = byseason_df.loc[byseason_df['total_customers'].idxmax(), 'season_name']

# Menentukan warna: oranye untuk season dengan total_customers tertinggi, sisanya lightgrey
colors = ["lightgrey" if season != max_season else "#FFA500" for season in byseason_df['season_name']]

# Membuat visualisasi
st.subheader("Total Rentals by Season")

fig, ax = plt.subplots(figsize=(20, 10))

sns.barplot(
    x="season_name",  # Menggunakan deskripsi musim yang sudah diterjemahkan
    y="total_customers", 
    data=byseason_df, 
    palette=colors,
    ax=ax
)
ax.set_title("Total Customers by Season", loc="center", fontsize=30)
ax.set_ylabel("Total Customers", fontsize=20)
ax.set_xlabel("Season", fontsize=20)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)




# Membuat kamus untuk weather condition
weather_mapping = {
    1: "Clear, Few clouds, Partly cloudy",
    2: "Mist + Cloudy, Mist + Broken clouds,\nMist + Few clouds, Mist",
    3: "Light Snow, Light Rain +\nThunderstorm + Scattered clouds",
    4: "Heavy Rain + Ice Pallets +\nThunderstorm + Mist, Snow + Fog"
}

# Menerapkan terjemahan pada kolom weathersit
byweather_df['weather_condition'] = byweather_df['weathersit'].map(weather_mapping)

# Menemukan kondisi cuaca dengan jumlah total_customers tertinggi
max_weather = byweather_df.loc[byweather_df['total_customers'].idxmax(), 'weathersit']

# Mengatur warna: biru untuk kondisi cuaca dengan total_customers tertinggi, lightgrey untuk sisanya
colors = ["#90CAF9" if x == max_weather else "#D3D3D3" for x in byweather_df['weathersit']]

# Membuat visualisasi
st.subheader("Total Rentals by Weather Condition")

fig, ax = plt.subplots(figsize=(20, 10))

sns.barplot(
    x="weather_condition", 
    y="total_customers", 
    data=byweather_df, 
    palette=colors,
    ax=ax
)

ax.set_title("Total Customers by Weather Condition", loc="center", fontsize=30)
ax.set_ylabel("Total Customers", fontsize=20)
ax.set_xlabel("Weather Condition", fontsize=20)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


# Menemukan jam dengan total_customers tertinggi
max_hour = byhour_df.loc[byhour_df['total_customers'].idxmax(), 'hr']

# Mengatur warna: biru untuk jam dengan total_customers tertinggi, lightgrey untuk jam lainnya
colors = ['#1f77b4' if hour == max_hour else 'lightgrey' for hour in byhour_df['hr']]

# Membuat visualisasi
st.subheader("Total Rentals by Hour")

fig, ax = plt.subplots(figsize=(16, 8))

ax.barh(
    byhour_df['hr'], 
    byhour_df['total_customers'], 
    color=colors
)
ax.set_title("Total Rentals by Hour", fontsize=30)
ax.set_xlabel("Total Customers", fontsize=20)
ax.set_ylabel("Hour", fontsize=20)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Total Customers by Time Bin")

# Binning berdasarkan jam
# Pastikan kolom 'hr' dalam bentuk integer
byhour_df['hr'] = pd.to_numeric(byhour_df['hr'], errors='coerce')

# Menentukan batas bin (jam)
bins = [0, 6, 12, 18, 24]  # Batas untuk pagi, siang, sore, dan malam
labels = ['Malam', 'Pagi', 'Siang', 'Sore']  # Label untuk masing-masing bin

# Menambahkan kolom bin ke byhour_df
byhour_df['time_bin'] = pd.cut(byhour_df['hr'], bins=bins, labels=labels, right=False)

# Menghitung total pelanggan per bin
binned_data = byhour_df.groupby('time_bin')['total_customers'].sum().reset_index()

# Membuat visualisasi
fig, ax = plt.subplots(figsize=(10, 6))

# Menentukan warna: biru untuk bin dengan pelanggan terbanyak, lightgrey untuk sisanya
max_customers = binned_data['total_customers'].max()  # Mencari total pelanggan tertinggi
colors = ['#1f77b4' if count == max_customers else 'lightgrey' for count in binned_data['total_customers']]

sns.barplot(x='time_bin', y='total_customers', data=binned_data, palette=colors, ax=ax)

ax.set_title("Total Customers by Time Bin", fontsize=24)
ax.set_xlabel("Time Bin", fontsize=18)
ax.set_ylabel("Total Customers", fontsize=18)
ax.tick_params(axis='x', labelsize=12)
ax.tick_params(axis='y', labelsize=12)

# Menggunakan st.pyplot untuk menampilkan hasil
st.pyplot(fig)



# Penutup dan Copyright
st.caption('Bike Rental Dashboard | Data from day.csv and hour.csv | Muhamad Fadhly Rafiansyah | © 2024')

