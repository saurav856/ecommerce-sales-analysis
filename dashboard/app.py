import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-Commerce Sales Analysis", layout="wide")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

raw = os.path.join(BASE_DIR, 'data', 'raw')

orders = pd.read_csv(os.path.join(raw, 'olist_orders_dataset.csv'))
items = pd.read_csv(os.path.join(raw, 'olist_order_items_dataset.csv'))
payments = pd.read_csv(os.path.join(raw, 'olist_order_payments_dataset.csv'))
products = pd.read_csv(os.path.join(raw, 'olist_products_dataset.csv'))
customers = pd.read_csv(os.path.join(raw, 'olist_customers_dataset.csv'))

orders = orders[orders['order_status'] == 'delivered']
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

master = orders.merge(items, on='order_id', how='left')
master = master.merge(payments, on='order_id', how='left')
master = master.merge(products, on='product_id', how='left')
master = master.merge(customers, on='customer_id', how='left')

st.title("E-Commerce Sales Dashboard")

col1, col2, col3 = st.columns(3)


col1.metric("Total Revenue", f"R$ {master['payment_value'].sum():,.0f}")
col2.metric("Total Orders", f"{master['order_id'].nunique():,}")
col3.metric("Average Order Value", f"R$ {master.groupby('order_id')['payment_value'].sum().mean():,.2f}")

st.subheader("Monthly Revenue")

master['month'] = master['order_purchase_timestamp'].dt.to_period('M').astype(str)
monthly_revenue = master.groupby('month')['payment_value'].sum().reset_index()

fig1 = px.line(monthly_revenue, x='month', y='payment_value', title='Revenue Over Time')
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Top 10 Product Categories by Revenue")

top_categories = master.groupby('product_category_name')['payment_value'].sum().sort_values(ascending=False).head(10).reset_index()

fig2 = px.bar(top_categories, x='payment_value', y='product_category_name', orientation='h', title='Top 10 Categories')
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Orders by Customer State")

state_orders = master.groupby('customer_state')['order_id'].nunique().sort_values(ascending=True).tail(10).reset_index()

fig3 = px.bar(state_orders, x='order_id', y='customer_state', orientation='h', title='Top 10 States by Orders')
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Orders by Day of Week")

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
master['day_of_week'] = master['order_purchase_timestamp'].dt.day_name()
day_orders = master.groupby('day_of_week')['order_id'].nunique().reindex(day_order).reset_index()

fig4 = px.bar(day_orders, x='day_of_week', y='order_id', title='Orders by Day of Week')
st.plotly_chart(fig4, use_container_width=True)
