import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta


def fix_arrow_compatibility(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str)
    return df

@st.cache_data
def load_data():
    customers = pd.read_csv('data/customers_dataset.csv')
    geolocation = pd.read_csv('data/geolocation_dataset.csv')
    order_items = pd.read_csv('data/order_items_dataset.csv')
    product_category_name_translation = pd.read_csv('data/product_category_name_translation.csv')
    order_payments = pd.read_csv('data/order_payments_dataset.csv')
    order_reviews = pd.read_csv('data/order_reviews_dataset.csv')
    orders = pd.read_csv('data/orders_dataset.csv')
    products = pd.read_csv('data/products_dataset.csv')
    sellers = pd.read_csv('data/sellers_dataset.csv')

    customers = fix_arrow_compatibility(customers)
    geolocation = fix_arrow_compatibility(geolocation)
    order_items = fix_arrow_compatibility(order_items)
    product_category_name_translation = fix_arrow_compatibility(product_category_name_translation)
    order_payments = fix_arrow_compatibility(order_payments)
    order_reviews = fix_arrow_compatibility(order_reviews)
    orders = fix_arrow_compatibility(orders)
    products = fix_arrow_compatibility(products)
    sellers = fix_arrow_compatibility(sellers)

    return customers, geolocation, order_items, product_category_name_translation, order_payments, order_reviews, orders, products, sellers

customers, geolocation, order_items, product_category_name_translation, order_payments, order_reviews, orders, products, sellers = load_data()

def clean_data():
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'], errors='coerce')
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'], errors='coerce')
    order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'], errors='coerce')
    
    orders['order_delivered_customer_date'] = orders['order_delivered_customer_date'].fillna("Not delivered")
    geolocation.drop_duplicates(inplace=True)

clean_data()

def data_assessment():
    st.header("Data Assessment")
    st.write("""
    In this section, we provide an overview of the datasets being used in the analysis. 
    You can view basic statistics, check for missing values or duplicates, and explore the data types.
    It helps to understand the data structure before diving into deeper analysis.
             
    As you may notice, theres still some missing data at several datasets, which would be dropped in the cleaning data phase.
    """)
    datasets = {
        'Customers': customers,
        'Geolocation': geolocation,
        'Order Items': order_items,
        'Order Payments': order_payments,
        'Order Reviews': order_reviews,
        'Orders': orders,
        'Products': products,
        'Sellers': sellers
    }
    for name, df in datasets.items():
        st.subheader(f"{name} Dataset")
        st.write(f"Shape: {df.shape}")
        st.write("Missing values:")
        st.write(df.isnull().sum())
        st.write("Data types:")
        st.write(df.dtypes)

def eda_checking():
    st.header("Exploratory Data Analysis")
    st.markdown("""
    **Exploratory Data Analysis (EDA)** is an essential step in understanding the structure of your dataset. 
    It helps us uncover hidden patterns, detect outliers, and ensure data quality by identifying issues like missing values.

    ### Key Components of EDA:
    - **Summary Statistics**: Provides an overview of the dataset's numerical features (e.g., mean, median, standard deviation).
    - **Missing Data**: Identifies columns with missing or null values, which can significantly affect our analysis.
    - **Data Distribution**: Visualizing the distribution of data helps identify trends and outliers in the numerical features.
    - **Correlations**: Exploring relationships between different features to uncover potential patterns and insights.

    EDA serves as the foundation for any further, more complex analysis. It allows us to better understand the data before we start modeling.
    """)
    st.subheader("Order Items Price Statistics")
    st.write(order_items['price'].describe())

    st.subheader("Order Status Distribution")
    st.write(orders['order_status'].value_counts())

    st.subheader("Payment Types Distribution")
    st.write(order_payments['payment_type'].value_counts())


def top_selling_products():
    st.header("Top Selling Products")
    st.markdown("""
    In this section, we display the top-selling products based on order volume. 
    The bar chart shows the products with the highest sales volume, categorized by product category.
    You can see how much each product has sold and their total sales value.
    ---
    Using this Visualisation, we can answer on Question Number 1
        - What is the most high-selling product?
    """)
    date_range = st.date_input(
        "Select Date Range",
        value=(orders['order_purchase_timestamp'].min().date(), 
               orders['order_purchase_timestamp'].max().date()),
        key="date_range_products"
    )
    
    # Add category filter
    unique_categories = product_category_name_translation['product_category_name_english'].unique()
    selected_categories = st.multiselect(
        "Select Product Categories",
        unique_categories,
        default=unique_categories[:5]
    )

    filtered_orders = orders[
        (orders['order_purchase_timestamp'].dt.date >= date_range[0]) &
        (orders['order_purchase_timestamp'].dt.date <= date_range[1])
    ]
    
    product_sales = order_items.merge(
        filtered_orders[['order_id']], 
        on='order_id', 
        how='inner'
    ).groupby('product_id').agg({
        'order_item_id': 'count',
        'price': 'sum'
    }).reset_index()
    
    product_sales = pd.merge(product_sales, products[['product_id', 'product_category_name']], on='product_id', how='left')
    product_sales = pd.merge(product_sales, product_category_name_translation, on='product_category_name', how='left')
    
    product_sales = product_sales[
        product_sales['product_category_name_english'].isin(selected_categories)
    ]
    
    sort_by = st.selectbox(
        "Sort by",
        ["Sales Volume", "Total Revenue"]
    )
    
    if sort_by == "Sales Volume":
        top_10 = product_sales.nlargest(10, 'order_item_id')
        x_col = 'order_item_id'
        title = 'Top 10 Products by Sales Volume'
    else:
        top_10 = product_sales.nlargest(10, 'price')
        x_col = 'price'
        title = 'Top 10 Products by Revenue'

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=top_10, x=x_col, y='product_category_name_english', palette='viridis', ax=ax)
    ax.set_title(title)
    st.pyplot(fig)

def order_status_distribution():
    st.header("Order Status Distribution")
    st.markdown("""
    This section visualizes the distribution of order statuses across all orders. 
    The pie chart shows the proportion of each order status, such as 'Shipped', 'Delivered', 'Canceled', etc.
    Understanding the order status distribution helps us see the overall order completion rate and potential issues.
    ---
    Using this Visualisation, we can answer on Question Number 2
        - Rate of order cancelled and order delivered
    """)
    time_period = st.selectbox(
        "Select Time Period",
        ["Last 30 days", "Last 90 days", "Last 180 days", "All time"]
    )
    
    end_date = orders['order_purchase_timestamp'].max()
    if time_period != "All time":
        days = int(time_period.split()[1])
        start_date = end_date - timedelta(days=days)
        filtered_orders = orders[orders['order_purchase_timestamp'] >= start_date]
    else:
        filtered_orders = orders

    view_type = st.radio(
        "Select View Type",
        ["Pie Chart", "Bar Chart"]
    )
    
    status_counts = filtered_orders['order_status'].value_counts()
    
    if view_type == "Pie Chart":
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(
            status_counts,
            autopct='%1.1f%%',
            startangle=140,
            pctdistance=0.85
        )
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)
    else:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=status_counts.index, y=status_counts.values, palette='viridis')
        plt.xticks(rotation=45)
    
    st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Total Orders",
            len(filtered_orders),
            delta=f"{((len(filtered_orders)/len(orders))*100):.1f}% of all orders"
        )
    with col2:
        delivery_rate = (filtered_orders['order_status'] == 'delivered').mean() * 100
        st.metric(
            "Delivery Rate",
            f"{delivery_rate:.1f}%"
        )

def top_cities_by_order():
    st.header("Top Cities by Order Count")
    st.markdown("""
    Here, we visualize the cities with the highest number of orders. 
    The bar chart highlights the cities that are driving the most orders, which can give insight into regional demand.
    The top 10 cities are listed based on the order count, helping us understand where the majority of the sales are coming from.
                
    Also we included a Geographical Map to locate the highest number of orders (Limited to 1000, to avoid performance issues)
    Please Wait until it fully loaded! :D
    ---
    Using this Visualisation, we can answer on Question Number 3
        - Geolocation of the highest consumer
    """)
    states = customers['customer_state'].unique()
    selected_states = st.multiselect(
        "Select States",
        states,
        default=states[:5]
    )

    min_orders = st.slider(
        "Minimum Number of Orders",
        min_value=1,
        max_value=1000,
        value=50
    )
    
    customer_orders = pd.merge(orders, customers, on='customer_id', how='left')
    customer_orders = customer_orders[customer_orders['customer_state'].isin(selected_states)]
    
    top_locations = customer_orders.groupby(['customer_city', 'customer_state']).size()
    top_locations = top_locations[top_locations >= min_orders].reset_index(name='order_count')
    top_locations = top_locations.nlargest(10, 'order_count')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=top_locations, x='order_count', y='customer_city', palette='viridis', ax=ax)
    ax.set_title('Top Cities by Order Count')
    st.pyplot(fig)
    
    st.subheader("Interactive Map")
    map_points = st.slider(
        "Number of locations to show on map",
        min_value=100,
        max_value=5000,
        value=1000,
        step=100
    )
    
    customer_locations = pd.merge(
        customers[customers['customer_state'].isin(selected_states)],
        geolocation[['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']],
        left_on='customer_zip_code_prefix',
        right_on='geolocation_zip_code_prefix',
        how='left'
    )
    
    m = folium.Map(location=[-14.235, -51.925], zoom_start=4)
    
    heat_data = [[row['geolocation_lat'], row['geolocation_lng']] 
                 for idx, row in customer_locations.head(map_points).iterrows()
                 if not pd.isna(row['geolocation_lat'])]
    
    from folium.plugins import HeatMap
    HeatMap(heat_data).add_to(m)
    folium_static(m)

def payment_methods_distribution():
    st.header("Payment Methods Distribution")
    st.markdown("""
    In this section, we examine the distribution of payment methods used by customers when placing their orders. 
    The bar chart presents the most popular payment methods, giving insights into how customers prefer to pay for their orders.
    This can help in understanding payment trends and potential areas for optimizing payment options.    
    ---
    Using this Visualisation, we can answer on Question Number 4
        - Most used Payment mode    
    """)
    
    payment_counts = order_payments['payment_type'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=payment_counts.index, y=payment_counts.values, ax=ax)
    ax.set_title('Payment Methods Distribution')
    ax.set_xticklabels(payment_counts.index, rotation=45)
    st.pyplot(fig)
    st.write(payment_counts)

def rfm_analytics():
    st.header("RFM Analytics")
    st.markdown("""
                RFM Analytics: This function analyzes customers based on three key metrics: Recency, Frequency, and Monetary (RFM). The goal is to segment customers based on their behavior in terms of recent activity, how often they purchase, and how much they spend.

     - Recency: Measures the time since the customer's last purchase.
     - Frequency: Measures how often the customer makes a purchase.
     - Monetary: Measures the total amount the customer has spent.
                
The function calculates each customer's recency, frequency, and monetary values, then segments them into three categories (High, Mid, Low) for each metric. It also creates a combined RFM_Score (e.g., Recent - High Frequency - High Spend). The function then visualizes the distribution of each score and displays the top RFM scores.

Visualization: The distributions of recency, frequency, and monetary scores are plotted in a 3-part countplot.""")
    latest_date = orders['order_purchase_timestamp'].max()
    order_values = order_payments.groupby('order_id')['payment_value'].sum().reset_index()
    orders_with_values = pd.merge(orders, order_values, on='order_id', how='left')
    
    rfm = orders_with_values.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (latest_date - x.max()).days,
        'order_id': 'count',
        'payment_value': 'sum'
    }).reset_index()
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    rfm['R_Score'] = pd.cut(rfm['recency'], bins=3, labels=['1-High', '2-Mid', '3-Low'])
    rfm['F_Score'] = pd.cut(rfm['frequency'], bins=3, labels=['3-Low', '2-Mid', '1-High'])
    rfm['M_Score'] = pd.cut(rfm['monetary'], bins=3, labels=['3-Low', '2-Mid', '1-High'])
    
    def rfm_statement(row):
        recency_map = {'1-High': 'Recent', '2-Mid': 'Mid-Recent', '3-Low': 'Not Recent'}
        frequency_map = {'3-Low': 'Low Frequency', '2-Mid': 'Mid Frequency', '1-High': 'High Frequency'}
        monetary_map = {'3-Low': 'Low Spend', '2-Mid': 'Mid Spend', '1-High': 'High Spend'}
        return f"{recency_map[row['R_Score']]} - {frequency_map[row['F_Score']]} - {monetary_map[row['M_Score']]}"
    
    rfm['RFM_Score'] = rfm.apply(rfm_statement, axis=1)
    
    fig, ax = plt.subplots(1, 3, figsize=(14, 6))
    sns.countplot(data=rfm, x='R_Score', palette='viridis', ax=ax[0])
    ax[0].set_title('Recency Score Distribution')
    sns.countplot(data=rfm, x='F_Score', palette='viridis', ax=ax[1])
    ax[1].set_title('Frequency Score Distribution')
    sns.countplot(data=rfm, x='M_Score', palette='viridis', ax=ax[2])
    ax[2].set_title('Monetary Score Distribution')
    plt.tight_layout()
    st.pyplot(plt)
    st.write(rfm['RFM_Score'].value_counts().head())

def customer_clustering():
    st.header("Customer Clustering")
    st.markdown(""" Customer Clustering: This function segments customers based on two factors: Frequency (how often they purchase) and Spending (how much they spend).

    - Frequency Segment: Divides customers into three segments based on the number of orders.
    - Spending Segment: Divides customers into three segments based on the total amount they spent.
    - Customer Segment: Combines the Frequency and Spending segments to create a unique customer segment identifier (e.g., Low_Budget).
                
    Visualization: 
    - Two countplots display the distribution of the frequency and spending segments. """)
    order_summary = pd.merge(orders, order_payments, on='order_id', how='left')
    customer_summary = order_summary.groupby('customer_id').agg({
        'order_id': 'count',
        'payment_value': 'sum'
    }).reset_index()
    
    customer_summary['frequency_segment'] = pd.cut(customer_summary['order_id'], bins=3, labels=['Low', 'Medium', 'High'])
    customer_summary['spending_segment'] = pd.cut(customer_summary['payment_value'], bins=3, labels=['Budget', 'Regular', 'Premium'])
    customer_summary['customer_segment'] = customer_summary['frequency_segment'].astype(str) + '_' + customer_summary['spending_segment'].astype(str)
    
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    sns.countplot(data=customer_summary, x='frequency_segment', palette='viridis', ax=ax[0])
    ax[0].set_title('Frequency Segment Distribution')
    sns.countplot(data=customer_summary, x='spending_segment', palette='viridis', ax=ax[1])
    ax[1].set_title('Spending Segment Distribution')
    plt.tight_layout()
    st.pyplot(plt)
    st.write(customer_summary['customer_segment'].value_counts().head())

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select a page", 
                                ["Home", "Data Assessment", "Data Cleaning", "EDA Checking", "Question 1", 
                                 "Question 2", "Question 3", "Question 4", "RFM Analytics", "Customer Clustering"])
    
    if page == "Home":
        st.title("Welcome to the E-Commerce Data Analysis App")
        st.markdown("""
        This application provides an overview of the Brazilian e-commerce dataset by Olist.
        You can explore various aspects such as order statistics, customer insights, and more.
        Navigate through the sidebar to explore different sections of the analysis.
                 
        In this scenario, we will try to answer these 4 business question
        - Question 1. What is the most high-selling product?
        - Question 2. Rate of order cancelled and order delivered
        - Question 3. Geolocation of the highest consumer
        - Question 4. Most used Payment mode
                    
        Made by RidhoK.U
        """)
    
    elif page == "Data Assessment":
        data_assessment()
    elif page == "Data Cleaning":
        st.header("Data Cleaning")
        st.write("Data cleaning was performed at load time. Thus, Data is Currently Clean :D")
    elif page == "EDA Checking":
        eda_checking()
    elif page == "Question 1":
        top_selling_products()
    elif page == "Question 2":
        order_status_distribution()
    elif page == "Question 3":
        top_cities_by_order()
    elif page == "Question 4":
        payment_methods_distribution()
    elif page == "RFM Analytics":
        rfm_analytics()
    elif page == "Customer Clustering":
        customer_clustering()

if __name__ == '__main__':
    main()
