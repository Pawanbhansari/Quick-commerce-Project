import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Ensure plots directory exists
os.makedirs('plots', exist_ok=True)

# --- Instacart Advanced EDA ---
orders = pd.read_csv('orders_encoded.csv')
products = pd.read_csv('products_encoded.csv')
order_products_prior = pd.read_csv('order_products__prior.csv')

eda_report = []
eda_report.append('# Advanced EDA Report\n')

eda_report.append('## Instacart Dataset\n')

# 1. Order Patterns
eda_report.append('### Order Patterns')
orders_per_user = orders.groupby('user_id')['order_id'].count()
plt.figure(figsize=(8,4))
sns.histplot(orders_per_user, bins=50, kde=True)
plt.title('Orders per User')
plt.xlabel('Number of Orders')
plt.ylabel('User Count')
plt.savefig('plots/instacart_orders_per_user.png')
plt.close()
eda_report.append('- Distribution of orders per user plotted.\n')

plt.figure(figsize=(8,4))
sns.countplot(x='order_dow', data=orders)
plt.title('Orders by Day of Week')
plt.xlabel('Day of Week (0=Sunday)')
plt.ylabel('Order Count')
plt.savefig('plots/instacart_orders_by_dow.png')
plt.close()
eda_report.append('- Orders by day of week plotted.\n')

plt.figure(figsize=(8,4))
sns.countplot(x='order_hour_of_day', data=orders)
plt.title('Orders by Hour of Day')
plt.xlabel('Hour of Day')
plt.ylabel('Order Count')
plt.savefig('plots/instacart_orders_by_hour.png')
plt.close()
eda_report.append('- Orders by hour of day plotted.\n')

plt.figure(figsize=(8,4))
sns.histplot(orders['days_since_prior_order'], bins=30, kde=True)
plt.title('Days Since Prior Order')
plt.xlabel('Days')
plt.ylabel('Order Count')
plt.savefig('plots/instacart_days_since_prior_order.png')
plt.close()
eda_report.append('- Days since prior order distribution plotted.\n')

# 2. Product & Basket Analysis
eda_report.append('### Product & Basket Analysis')
product_counts = order_products_prior['product_id'].value_counts().head(20)
plt.figure(figsize=(10,5))
sns.barplot(x=product_counts.index, y=product_counts.values)
plt.title('Top 20 Most Popular Products')
plt.xlabel('Product ID')
plt.ylabel('Count')
plt.xticks(rotation=90)
plt.savefig('plots/instacart_top_products.png')
plt.close()
eda_report.append('- Top 20 most popular products plotted.\n')

basket_sizes = order_products_prior.groupby('order_id').size()
plt.figure(figsize=(8,4))
sns.histplot(basket_sizes, bins=50, kde=True)
plt.title('Basket Size Distribution')
plt.xlabel('Number of Products per Order')
plt.ylabel('Order Count')
plt.savefig('plots/instacart_basket_size.png')
plt.close()
eda_report.append('- Basket size distribution plotted.\n')

reorder_rates = order_products_prior.groupby('product_id')['reordered'].mean().sort_values(ascending=False).head(20)
plt.figure(figsize=(10,5))
sns.barplot(x=reorder_rates.index, y=reorder_rates.values)
plt.title('Top 20 Products by Reorder Rate')
plt.xlabel('Product ID')
plt.ylabel('Reorder Rate')
plt.xticks(rotation=90)
plt.savefig('plots/instacart_top_reorder_products.png')
plt.close()
eda_report.append('- Top 20 products by reorder rate plotted.\n')

# 3. Customer Segmentation
eda_report.append('### Customer Segmentation')
user_reorder_ratio = order_products_prior.groupby('order_id')['reordered'].mean()
plt.figure(figsize=(8,4))
sns.histplot(user_reorder_ratio, bins=30, kde=True)
plt.title('User Reorder Ratio Distribution')
plt.xlabel('Reorder Ratio')
plt.ylabel('Order Count')
plt.savefig('plots/instacart_user_reorder_ratio.png')
plt.close()
eda_report.append('- User reorder ratio distribution plotted.\n')

# 4. Time Series Trends
eda_report.append('### Time Series Trends')
orders['order_date'] = pd.to_datetime(orders['order_id'], errors='coerce')  # Placeholder, as no date column
orders_by_number = orders.groupby('order_number').size()
plt.figure(figsize=(8,4))
orders_by_number.plot()
plt.title('Order Volume by Order Number (Proxy for Time)')
plt.xlabel('Order Number')
plt.ylabel('Order Count')
plt.savefig('plots/instacart_order_volume_over_time.png')
plt.close()
eda_report.append('- Order volume by order number (proxy for time) plotted.\n')

# 5. Feature Distributions
eda_report.append('### Feature Distributions')
for col in ['total_orders_per_user', 'avg_days_between_orders']:
    plt.figure(figsize=(8,4))
    sns.histplot(orders[col], bins=30, kde=True)
    plt.title(f'Distribution of {col}')
    plt.xlabel(col)
    plt.ylabel('Count')
    plt.savefig(f'plots/instacart_{col}_dist.png')
    plt.close()
    eda_report.append(f'- Distribution of {col} plotted.\\n')

# --- M5 Walmart Advanced EDA ---
eda_report.append('\n## M5 Walmart Dataset\n')
train = pd.read_csv('train_encoded.csv')

# 1. Sales Trends
eda_report.append('### Sales Trends')
plt.figure(figsize=(12,5))
train.groupby('Date')['Weekly_Sales'].sum().plot()
plt.title('Total Weekly Sales Over Time')
plt.xlabel('Date')
plt.ylabel('Total Weekly Sales')
plt.savefig('plots/m5_total_weekly_sales_over_time.png')
plt.close()
eda_report.append('- Total weekly sales over time plotted.\n')

plt.figure(figsize=(10,5))
train.groupby('Store')['Weekly_Sales'].sum().plot(kind='bar')
plt.title('Total Sales by Store')
plt.xlabel('Store')
plt.ylabel('Total Sales')
plt.savefig('plots/m5_total_sales_by_store.png')
plt.close()
eda_report.append('- Total sales by store plotted.\n')

plt.figure(figsize=(10,5))
train.groupby('Dept')['Weekly_Sales'].sum().plot(kind='bar')
plt.title('Total Sales by Department')
plt.xlabel('Department')
plt.ylabel('Total Sales')
plt.savefig('plots/m5_total_sales_by_dept.png')
plt.close()
eda_report.append('- Total sales by department plotted.\n')

# 2. Seasonality & Holidays
eda_report.append('### Seasonality & Holidays')
plt.figure(figsize=(10,5))
sns.boxplot(x='IsHoliday', y='Weekly_Sales', data=train)
plt.title('Weekly Sales by Holiday')
plt.xlabel('Is Holiday')
plt.ylabel('Weekly Sales')
plt.savefig('plots/m5_sales_by_holiday.png')
plt.close()
eda_report.append('- Weekly sales by holiday plotted.\n')

# 3. Markdown & Promotion Effects
eda_report.append('### Markdown & Promotion Effects')
markdown_cols = [col for col in train.columns if 'MarkDown' in col]
for col in markdown_cols:
    plt.figure(figsize=(8,4))
    sns.scatterplot(x=col, y='Weekly_Sales', data=train)
    plt.title(f'Weekly Sales vs {col}')
    plt.xlabel(col)
    plt.ylabel('Weekly Sales')
    plt.savefig(f'plots/m5_sales_vs_{col}.png')
    plt.close()
    eda_report.append(f'- Weekly sales vs {col} plotted.\\n')

# 4. Store & Department Analysis
eda_report.append('### Store & Department Analysis')
plt.figure(figsize=(8,4))
sns.boxplot(x='Type', y='Weekly_Sales', data=train)
plt.title('Weekly Sales by Store Type')
plt.xlabel('Store Type')
plt.ylabel('Weekly Sales')
plt.savefig('plots/m5_sales_by_store_type.png')
plt.close()
eda_report.append('- Weekly sales by store type plotted.\n')

plt.figure(figsize=(8,4))
sns.boxplot(x='Store_Size_Bucket', y='Weekly_Sales', data=train)
plt.title('Weekly Sales by Store Size Bucket')
plt.xlabel('Store Size Bucket')
plt.ylabel('Weekly Sales')
plt.savefig('plots/m5_sales_by_store_size_bucket.png')
plt.close()
eda_report.append('- Weekly sales by store size bucket plotted.\n')

# 5. Feature Distributions
eda_report.append('### Feature Distributions')
for col in ['Weekly_Sales_MA4', 'Days_to_next_holiday']:
    plt.figure(figsize=(8,4))
    sns.histplot(train[col], bins=30, kde=True)
    plt.title(f'Distribution of {col}')
    plt.xlabel(col)
    plt.ylabel('Count')
    plt.savefig(f'plots/m5_{col}_dist.png')
    plt.close()
    eda_report.append(f'- Distribution of {col} plotted.\\n')

# --- Correlation & Relationships ---
eda_report.append('\n## Correlation & Relationships\n')
plt.figure(figsize=(10,8))
corr = train.select_dtypes(include=[np.number]).corr()
sns.heatmap(corr, annot=False, cmap='coolwarm')
plt.title('M5 Walmart: Correlation Heatmap')
plt.savefig('plots/m5_correlation_heatmap.png')
plt.close()
eda_report.append('- Correlation heatmap for M5 Walmart numeric features plotted.\n')

# --- Missing Values & Anomalies ---
eda_report.append('\n## Missing Values & Anomalies\n')
missing_instacart = orders.isnull().sum().sum() + products.isnull().sum().sum()
missing_m5 = train.isnull().sum().sum()
eda_report.append(f'- Instacart missing values: {missing_instacart}\n')
eda_report.append(f'- M5 Walmart missing values: {missing_m5}\n')

# --- Save EDA Report ---
with open('advanced_eda_report.md', 'w') as f:
    f.writelines(eda_report)

print('Advanced EDA complete. Plots saved in plots/. Report saved as advanced_eda_report.md.') 