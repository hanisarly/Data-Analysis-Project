import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from datetime import datetime
sns.set(style='dark')

day_fix_df = pd.read_csv("day_fix.csv")
hour_fix_df = pd.read_csv("hour_fix.csv")

def get_total_count_by_hour_df(hour_df):
    """
    Menghitung total jumlah sewa sepeda berdasarkan jam.
    """
    hour_count_df =  hour_df.groupby(by="hours").agg({"count_cr": "sum"})
    return hour_count_df

def count_by_day_df(day_df):
    """
    Menghitung total jumlah sewa sepeda per hari pada rentang waktu tertentu.
    """
    day_df_count_2011 = day_df.query('dteday >= "2011-01-01" and dteday < "2012-12-31"')
    return day_df_count_2011

def total_registered_df(day_df):
    """
    Menghitung total pelanggan registered per hari.
    """
    reg_df =  day_df.groupby(by="dteday").agg({
        "registered": "sum"
    }).reset_index()
    reg_df.rename(columns={"registered": "register_sum"}, inplace=True)
    return reg_df

def total_casual_df(day_df):
    """
    Menghitung total pelanggan casual per hari.
    """
    cas_df =  day_df.groupby(by="dteday").agg({
        "casual": "sum"
    }).reset_index()
    cas_df.rename(columns={"casual": "casual_sum"}, inplace=True)
    return cas_df

def count_by_workingday(day_df):
    """
    Menghitung total jumlah sewa sepeda berdasarkan workingday.
    """
    workingday_df = day_df.groupby(by="workingday")["count_cr"].sum().reset_index()
    return workingday_df


def sum_order(hour_df):
    """
    Menghitung total pesanan berdasarkan jam.
    """
    sum_order_items_df = hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

# def sum_season(day_df): 
#     """
#     Menghitung total jumlah sewa sepeda berdasarkan musim.
#     """
#     season_df = day_df.groupby(by="season").count_cr.sum().reset_index() 
#     return season_df

def most_rentals_by_season(day_df):
    """
    Mengembalikan DataFrame yang berisi jumlah penyewaan terbanyak untuk setiap musim.
    """
    rentals_by_season = day_df.groupby(by="season")['count_cr'].sum().sort_values(ascending=False)
    # Convert Series to DataFrame
    season_df = rentals_by_season.reset_index()
    return season_df

def group_by_hour_and_sum(hour_df):
    """
    Group data by hour and calculate sum of count_cr.
    """
    hour_grouped = hour_df.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return hour_grouped

def create_rfm_casual_df(df):
    rfm_casual_df = day_fix_df.groupby('casual').agg({
        'dteday': 'max', # Recency
        'instant': 'count',  # Frequency
        'count_cr': 'sum'  # Monetary
    }).reset_index()

    # Mengganti nama kolom
    rfm_casual_df.columns = ['casual', 'max_order_timestamp', 'Frequency', 'Monetary']

    # Menghitung kapan terakhir pelanggan melakukan order (hari)
    rfm_casual_df["max_order_timestamp"] = rfm_casual_df["max_order_timestamp"].dt.date
    recent_date = rfm_casual_df["max_order_timestamp"].max()  # Menggunakan nama kolom yang sudah diubah
    rfm_casual_df["Recency"] = rfm_casual_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    return rfm_casual_df

datetime_columns = ["dteday"]

# Mengkonversi kolom datetime menjadi tipe data datetime
for column in datetime_columns:
    day_fix_df[column] = pd.to_datetime(day_fix_df[column])
    hour_fix_df[column] = pd.to_datetime(hour_fix_df[column])

# Mengkonversi tanggal minimum dan maksimum ke tipe data datetime64[ns]
min_date_days = pd.to_datetime(day_fix_df["dteday"].min())
max_date_days = pd.to_datetime(day_fix_df["dteday"].max())

min_date_hour = pd.to_datetime(hour_fix_df["dteday"].min())
max_date_hour = pd.to_datetime(hour_fix_df["dteday"].max())

# Menggunakan streamlit untuk membuat sidebar
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://id.pngtree.com/freepng/bicycle-lets-bike_6262347.html")
    
    # Menampilkan input untuk rentang waktu
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days.date(),  # Konversi ke tipe data date
        max_value=max_date_days.date(),  # Konversi ke tipe data date
        value=[min_date_days.date(), max_date_days.date()]  # Konversi ke tipe data date
    )
  
# Filter data berdasarkan rentang waktu yang dipilih
main_df_days = day_fix_df[(day_fix_df["dteday"] >= pd.to_datetime(start_date)) & (day_fix_df["dteday"] <= pd.to_datetime(end_date))]
main_df_hour = hour_fix_df[(hour_fix_df["dteday"] >= pd.to_datetime(start_date)) & (hour_fix_df["dteday"] <= pd.to_datetime(end_date))]

# Memanggil fungsi-fungsi yang telah Anda definisikan sebelumnya
hour_grouped = group_by_hour_and_sum(main_df_hour)
day_df_count_2011 = count_by_day_df(main_df_days)
reg_df = total_registered_df(main_df_days)
cas_df = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season_df = most_rentals_by_season(main_df_hour)  # Memanggil most_rentals_by_season

# Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Bike Sharing Dashboard :sparkles:')

# Menampilkan header untuk bagian "Daily Sharing"
st.subheader('Daily Sharing')

# Membagi layar menjadi tiga kolom
col1, col2, col3 = st.columns(3)

# Menampilkan metrik untuk total pesanan sepeda
with col1:
    total_orders = day_df_count_2011.count_cr.sum()
    st.metric("Total Sharing Bike", value=total_orders)

# Menampilkan metrik untuk total pelanggan terdaftar
with col2:
    total_registered = reg_df.register_sum.sum()
    st.metric("Total Registered", value=total_registered)

# Menampilkan metrik untuk total pelanggan casual
with col3:
    total_casual = cas_df.casual_sum.sum()
    st.metric("Total Casual", value=total_casual)

# Memanggil fungsi most_rentals_by_season untuk mendapatkan DataFrame musiman
season_df = most_rentals_by_season(main_df_hour)

st.subheader("Pada musim apakah penyewaan sepeda paling banyak terjadi?")
colors = ["#C51E3A", "#FDBCB4", "#FDBCB4", "#FDBCB4"]

fig, ax = plt.subplots(figsize=(20, 10))
# Create a bar chart using seaborn
sns.barplot(
    x=season_df["season"],    # Menggunakan kolom "season" dari DataFrame season_df sebagai sumbu x
    y=season_df["count_cr"],  # Menggunakan kolom "count_cr" dari DataFrame season_df sebagai sumbu y
    palette=colors,
    ax=ax
)
# Set chart title and labels
plt.title("Jumlah Pelanggan di Setiap Musim", loc='center', fontsize=40)
ax.tick_params(axis='x', labelsize=20)  # Menetapkan ukuran label sumbu x
ax.tick_params(axis='y', labelsize=20)  # Menetapkan ukuran label sumbu y

ax.grid(False, axis='both')
st.pyplot(fig)


st.subheader("Pada jam berapa kah penyewaan paling banyak dan paling sedikit dilakukan?")
# membuat bar chart untuk melihat perbedaan penyewaan sepeda berdasarkan jam
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Memanggil fungsi get_total_count_by_hour_df dengan parameter hour_fix_df
hour_grouped = group_by_hour_and_sum(hour_fix_df)
 
# membuat barplot untuk penyewa sepeda terbanyak 
sns.barplot(
    x="hours", # Menggunakan kolom "hours" dari hour_count_df sebagai nilai x
    y="count_cr", 
    data=hour_grouped.head(5), 
    palette=["#FDBCB4", "#FDBCB4", "#C51E3A", "#FDBCB4", "#FDBCB4"], 
    ax=ax[0])

# mengatur label dan judul untuk subplot pertama
ax[0].set_ylabel(None)
ax[0].set_xlabel("Hours (PM)", fontsize=30)
ax[0].set_title("Jam dengan banyak penyewa sepeda", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

# membuat barplot untuk penyewa sepeda terdikit 
sns.barplot(
    x="hours", # Menggunakan kolom "hours" dari hour_count_df sebagai nilai x
    y="count_cr", 
    data=hour_grouped.sort_values(by="hours", ascending=True).head(5), 
    palette=["#FDBCB4", "#FDBCB4", "#FDBCB4", "#FDBCB4","#C51E3A"], 
    ax=ax[1])

# mengatur label dan judul untuk subplot kedua
ax[1].set_ylabel(None)
ax[1].set_xlabel("Hours (AM)",  fontsize=30)
ax[1].set_title("Jam dengan sedikit penyewa sepeda", loc="center", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)

st.subheader("Manakah yang memiliki lebih banyak pelanggan, hari kerja atau hari libur?")
# Call count_by_workingday function with the appropriate DataFrame
workingday_df = count_by_workingday(day_fix_df)

# Replace labels in the DataFrame
workingday_df['workingday'] = workingday_df['workingday'].replace({1: 'Weekday', 0: 'Holiday'})

# Now, you can use the DataFrame to create the pie chart
total = workingday_df['count_cr'].sum()
explode = (0, 0)  # Menambahkan efek 'explode' untuk menonjolkan bagian dari pie chart

# Mengganti warna antar bagian
colors = ['#ff9999', '#C51E3A']

# Membuat pie chart
fig, ax = plt.subplots()
ax.pie(
    x=workingday_df['count_cr'].tolist(),
    labels=workingday_df['workingday'],  # Menggunakan kolom 'workingday' dari DataFrame
    autopct='%1.1f%%',  # Menampilkan persentase
    explode=explode,
    colors=colors,
)

# Mengatur aspek proporsi lingkaran menjadi 'equal' untuk memastikan lingkaran berbentuk bundar
ax.set_aspect('equal')

# Menampilkan pie chart menggunakan st.pyplot()
st.pyplot(fig)


# Call the function to create the DataFrame
rfm_casual_df = create_rfm_casual_df(day_fix_df)

# Calculate average recency, frequency, and monetary
avg_recency = round(rfm_casual_df["Recency"].mean(), 1)
avg_frequency = round(rfm_casual_df["Frequency"].mean(), 2)
avg_monetary = format_currency(rfm_casual_df["Monetary"].mean(), "AUD", locale='es_CO')

# Display the metrics
st.subheader("Best Casual Customers Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    st.metric("Average Monetary", value=avg_monetary)

# Create subplots for the bar plots
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

# Visualizations based on Recency
sns.barplot(y="Recency", x="casual", data=rfm_casual_df.sort_values(by="Recency", ascending=True).head(5), color="#FDBCB4", ax=ax[0])
ax[0].set_ylabel("Recency (days)", fontsize=15)
ax[0].set_xlabel("Customer ID", fontsize=15)
ax[0].set_title("Casual Customers by Recency", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)

# Visualizations based on Frequency
sns.barplot(y="Frequency", x="casual", data=rfm_casual_df.sort_values(by="Frequency", ascending=False).head(5), color="#FDBCB4", ax=ax[1])
ax[1].set_ylabel("Frequency", fontsize=15)
ax[1].set_xlabel("Customer ID", fontsize=15)
ax[1].set_title("Casual Customers by Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

# Visualizations based on Monetary
sns.barplot(y="Monetary", x="casual", data=rfm_casual_df.sort_values(by="Monetary", ascending=False).head(5), color="#FDBCB4", ax=ax[2])
ax[2].set_ylabel("Monetary", fontsize=15)
ax[2].set_xlabel("Customer ID", fontsize=15)
ax[2].set_title("Casual Customers by Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.caption('Copyright (c) SarlyBajsair 2024')
