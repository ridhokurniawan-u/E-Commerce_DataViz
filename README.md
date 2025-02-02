# E-Commerce Customer Data Visualization

## **Overview**
This project focuses on the analysis and visualization of e-commerce customer data. By leveraging Python and data visualization libraries such as Matplotlib, Seaborn, and Plotly, this project aims to provide valuable insights into customer behaviors, product performance, payment methods, and more. The goal is to help businesses make data-driven decisions to optimize their operations and enhance customer experience.

## **Data Source**
The data used in this project is sourced from a public e-commerce dataset containing order and customer information. It includes details such as:

- **Orders**: Order ID, purchase date, shipping date, order status.
- **Order Items**: Product category, price, quantity.
- **Customers**: Customer demographics and location.
- **Payments**: Payment method and transaction details.
- **Geolocation**: Geographic location of the customers.

## **Technologies Used**
- Python 3.x
- Pandas
- Matplotlib
- Seaborn
- Plotly
- Jupyter Notebooks

## **Key Insights**
1. **Most Popular Product Categories**  
   Visualizing which product categories are purchased most frequently, helping businesses understand customer preferences and demand trends.

2. **Order Status Distribution**  
   Visualizing the distribution of orders based on their status (e.g., Delivered, Canceled), offering insights into logistics performance.

3. **Payment Method Preferences**  
   Understanding the distribution of various payment methods (e.g., credit card, boleto) used by customers and highlighting trends.

4. **Customer Locations**  
   Mapping customer geolocations to identify regions with the highest purchasing activity, allowing for targeted marketing strategies.

## **Visualizations**
Here are some of the key visualizations created in this project:

1. **Distribution of Product Categories**  
   Bar chart displaying the most frequently purchased product categories.

2. **Order Status Distribution**  
   Pie chart showing the percentage of orders that are delivered, canceled, or pending.

3. **Top Payment Methods**  
   A bar plot illustrating the most popular payment methods used by customers.

4. **Geographical Distribution of Customers**  
   A map showing customer concentration in different regions of Brazil.

## **EDA Process**
The following steps were followed to clean and explore the dataset:

1. **Data Cleaning:**  
   - Removed duplicates from geolocation data.
   - Filled missing values in order delivery status (marked as "Not Delivered" when data is missing).
   - Converted timestamp columns to `datetime` format for easier analysis.

2. **Exploratory Data Analysis (EDA):**  
   - Performed univariate analysis to understand the distribution of variables like product price and order status.
   - Conducted multivariate analysis to explore relationships between product categories and order status.
   - Analyzed correlations between numeric variables to identify any significant patterns.

3. **Visualization:**  
   - Created various visualizations to present the data in an easy-to-understand format for non-technical stakeholders.

## **Installation**
## Setup Environment

### Anaconda (Recommended)
1. **Create a new environment with Python 3.9:**
   ```bash
   conda create --name ecommerce-dashboard python=3.9
   conda activate ecommerce-dashboard
   pip install -r requirements.txt
   ```

2. Shell/Terminal
   ```bash
   mkdir ecommerce-dashboard
   cd ecommerce-dashboard
   pip install -r requirements.txt

## **Dashboard Execution**
   ```bash
   cd ./dashboard
   streamlit run dashboard.py
