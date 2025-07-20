import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Instacart Outlier Visualization ---
order_products_prior = pd.read_csv('order_products__prior.csv')

plt.figure(figsize=(10, 4))
sns.boxplot(x=order_products_prior['add_to_cart_order'])
plt.title('Instacart: Boxplot of add_to_cart_order')
plt.savefig('instacart_add_to_cart_order_boxplot.png')
plt.close()

plt.figure(figsize=(10, 4))
sns.histplot(order_products_prior['add_to_cart_order'], bins=50, kde=True)
plt.title('Instacart: Histogram of add_to_cart_order')
plt.savefig('instacart_add_to_cart_order_hist.png')
plt.close()

# --- M5 Walmart Outlier Visualization ---
train_full = pd.read_csv('train_full.csv')

plt.figure(figsize=(10, 4))
sns.boxplot(x=train_full['Weekly_Sales'])
plt.title('M5 Walmart: Boxplot of Weekly_Sales')
plt.savefig('m5_weekly_sales_boxplot.png')
plt.close()

plt.figure(figsize=(10, 4))
sns.histplot(train_full['Weekly_Sales'], bins=50, kde=True)
plt.title('M5 Walmart: Histogram of Weekly_Sales')
plt.savefig('m5_weekly_sales_hist.png')
plt.close()

# --- Outlier Summary ---
instacart_total = len(order_products_prior)
instacart_outliers = ((order_products_prior['add_to_cart_order'] < order_products_prior['add_to_cart_order'].quantile(0.25) - 1.5 * (order_products_prior['add_to_cart_order'].quantile(0.75) - order_products_prior['add_to_cart_order'].quantile(0.25))) | (order_products_prior['add_to_cart_order'] > order_products_prior['add_to_cart_order'].quantile(0.75) + 1.5 * (order_products_prior['add_to_cart_order'].quantile(0.75) - order_products_prior['add_to_cart_order'].quantile(0.25)))).sum()
instacart_percent = 100 * instacart_outliers / instacart_total

m5_total = len(train_full)
m5_outliers = ((train_full['Weekly_Sales'] < train_full['Weekly_Sales'].quantile(0.25) - 1.5 * (train_full['Weekly_Sales'].quantile(0.75) - train_full['Weekly_Sales'].quantile(0.25))) | (train_full['Weekly_Sales'] > train_full['Weekly_Sales'].quantile(0.75) + 1.5 * (train_full['Weekly_Sales'].quantile(0.75) - train_full['Weekly_Sales'].quantile(0.25)))).sum()
m5_percent = 100 * m5_outliers / m5_total

with open('outlier_detection.md', 'w') as f:
    f.write('# Outlier Detection Summary\n\n')
    f.write('## Instacart\n')
    f.write(f'- Outliers in add_to_cart_order: {instacart_outliers} / {instacart_total} ({instacart_percent:.2f}%)\n')
    f.write('- Outliers detected using IQR rule.\n')
    f.write('  - See instacart_add_to_cart_order_boxplot.png and instacart_add_to_cart_order_hist.png for visualizations.\n\n')
    f.write('## M5 Walmart\n')
    f.write(f'- Outliers in Weekly_Sales: {m5_outliers} / {m5_total} ({m5_percent:.2f}%)\n')
    f.write('- Outliers detected using IQR rule.\n')
    f.write('  - See m5_weekly_sales_boxplot.png and m5_weekly_sales_hist.png for visualizations.\n')

print('Outlier visualizations and summary saved.') 