import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from datetime import datetime
sns.set_theme(style='dark')

# Read dataset
orders_payments_customers_df = pd.read_csv('dashboard/orders_payments_customers.csv')
product_review_df = pd.read_csv('dashboard/product_review.csv')
by_city_df = pd.read_csv('dashboard/by_city.csv')
rfm_df = pd.read_csv('dashboard/rfm.csv')
customer_segment_df = pd.read_csv('dashboard/customer_segment.csv')

# Convert order_purchase_timestamp to datetime
orders_payments_customers_df['order_purchase_timestamp'] = pd.to_datetime(orders_payments_customers_df['order_purchase_timestamp'])

# Functions
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df



# Create date range
min_date = orders_payments_customers_df["order_purchase_timestamp"].min()
max_date = orders_payments_customers_df["order_purchase_timestamp"].max()
 
# Create sidebar for date range
with st.sidebar:
    # Logo
    st.image("https://raw.githubusercontent.com/vitoananta3/vitoananta3/main/src/app/favicon.ico?token=GHSAT0AAAAAACL366IBYOIOMNIWIL2M5NBKZPEITPA", use_column_width=True)

    # Filter by date
    start_date, end_date = st.date_input(
        label='Filter by date',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Convert start_date and end_date to pandas Timestamp objects
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

# Range the df
orders_payments_customers_df = orders_payments_customers_df[
    (orders_payments_customers_df["order_purchase_timestamp"] >= start_date) &
    (orders_payments_customers_df["order_purchase_timestamp"] <= end_date)
]


# Create data
daily_orders_df = create_daily_orders_df(orders_payments_customers_df)

# Main
st.header('Public E-Commerce Dashboard :shopping_trolley:')

# Daily of Orders and Revenue
st.subheader('Daily of Orders and Revenue')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale="pt_BR") 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Daily Orders", loc="center", fontsize=20, pad=15)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.set_xlabel("Date", fontsize=20, labelpad=15)
ax.set_ylabel("Number of Orders", fontsize=20, labelpad=15)

st.pyplot(fig)

# Customer Products Category Performance
st.subheader("Best & Worst Performing Product")

top_5_product_review_df = product_review_df[:5]
bottom_5_product_review_df = product_review_df[-5:]

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(55, 21))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="review_score", y="product_category", data=top_5_product_review_df.head(5), palette=colors, ax=ax[0], hue='product_category')
ax[0].set_ylabel(None)
ax[0].set_xlabel("Review Score", fontsize=89, labelpad=55)
ax[0].set_title("Best Performing Product", loc="center", fontsize=89, pad=55)
ax[0].tick_params(axis='y', labelsize=89)
ax[0].tick_params(axis='x', labelsize=89)
 
sns.barplot(x="review_score", y="product_category", data=bottom_5_product_review_df.sort_values(by="review_score", ascending=True).head(5), palette=colors, ax=ax[1], hue='product_category')
ax[1].set_ylabel(None)
ax[1].set_xlabel("Review Score", fontsize=89, labelpad=55)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=89, pad=55)
ax[1].tick_params(axis='y', labelsize=89)
ax[1].tick_params(axis='x', labelsize=89)
 
st.pyplot(fig)

# Customer Demographics
st.subheader("Customer Demographics")

# Cut the customer_cities
top_5_by_city_df = by_city_df.sort_values(by="customer_count", ascending=False)[:5]
 
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count", 
    y="customer_city",
    data=top_5_by_city_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax,
    hue='customer_city'
)
ax.set_title("Number of Customer by Cities", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# RFM
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="truncated_customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0], hue='customer_unique_id')
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_unique_id", fontsize=30, labelpad=21)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50, pad=21)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="truncated_customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1], hue='customer_unique_id')
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_unique_id", fontsize=30, labelpad=21)
ax[1].set_title("By Frequency", loc="center", fontsize=50, pad=21)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="truncated_customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2], hue='customer_unique_id')
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_unique_id", fontsize=30, labelpad=21)
ax[2].set_title("By Monetary", loc="center", fontsize=50, pad=21)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)

# Customer Segmentation
st.subheader("Customer Segmentation")

fig, ax = plt.subplots(figsize=(55, 21))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="customer_unique_id", y="segment", data=customer_segment_df.sort_values(by='customer_unique_id', ascending=False), palette=colors, hue="segment", ax=ax)
ax.set_ylabel(None)
ax.set_xlabel("Number of Customers", fontsize=89, labelpad=55)
ax.set_title("Customer Segmentation", loc="center", fontsize=89, pad=55)
ax.tick_params(axis='y', labelsize=89)
ax.tick_params(axis='x', labelsize=89)
st.pyplot(fig)