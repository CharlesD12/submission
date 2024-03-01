import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#create customers_demographics_df
def create_customer_bycity_df(df):
  bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
  bycity_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

  return bycity_df

#create customers_demographics_df 2
def create_customer_bystate_df(df):
  bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
  bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

  return bystate_df

#create_frm_df()
def create_frm_df(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])

    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "payment_value": "sum" # menghitung jumlah revenue yang dihasilkan
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    recent_date = df["order_purchase_timestamp"].max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

all_df = pd.read_csv("main_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

#Membuat komponen filter
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan dengan penyesuaian agar berada di tengah
    st.markdown(
        f'<div style="display: flex; justify-content: center;"><img src="https://raw.githubusercontent.com/CharlesD12/E-commerce_public_dataset/main/logo.jpg" width="150"></div>',
        unsafe_allow_html=True,
    )

 # Menambahkan jarak antara gambar dan rentang waktu
    st.markdown("<br>", unsafe_allow_html=True)

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                (all_df["order_purchase_timestamp"] <= str(end_date))]

customer_bycity_df = create_customer_bycity_df(main_df)
customer_bystate_df = create_customer_bystate_df(main_df)
rfm_df = create_frm_df(main_df)

st.header(':sparkles: Charles Dometian Dashboard :sparkles:')

#Membuat grafik customers
st.subheader("Customer Demographics")

#Demografi customer berdasarkan city
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#FF0000"] + ["#FF7F7F"] * 19
sns.barplot(
    x="customer_count",
    y="customer_city",
    data=customer_bycity_df.sort_values(by="customer_count", ascending=False).head(20),
    palette=colors,
    ax=ax
)
ax.set_title("Jumlah Pelanggan berdasarkan Kota", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
plt.show()

#Demografi customer berdasarkan state
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#0000FF"] + ["#ADD8E6"] * 26
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=customer_bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Jumlah Pelanggan berdasarkan Negara", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
plt.show()

#Membuat RFM grafik
st.subheader("Pelanggan terbaik berdasarkan RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 10)) # Ukuran gambar diperbesar

# Buat daftar warna dengan biru untuk bar pertama dan biru cerah untuk sisa bar
colors = ["#72BCD4"] * 5

# Plot untuk Recency
top5_recency = rfm_df.sort_values(by="recency", ascending=True).head(5)
sns.barplot(y="recency", x="customer_id", data=top5_recency, palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=90)

# Plot untuk Frequency
top5_frequency = rfm_df.sort_values(by="frequency", ascending=False).head(5)
sns.barplot(y="frequency", x="customer_id", data=top5_frequency, palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=90)

# Plot untuk Monetary
top5_monetary = rfm_df.sort_values(by="monetary", ascending=False).head(5)
sns.barplot(y="monetary", x="customer_id", data=top5_monetary, palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=90)

plt.suptitle("Pelanggan terbaik berdasarkan RFM Parameters", fontsize=20)
plt.tight_layout()
plt.subplots_adjust(bottom=0.15) # Menambahkan ruang ekstra di bagian bawah untuk label sumbu x

st.pyplot(fig)
