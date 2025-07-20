import pandas as pd

# --- Instacart Outlier Analysis ---
order_products_prior = pd.read_csv('order_products__prior.csv')

# Outlier detection for add_to_cart_order using IQR rule
q1 = order_products_prior['add_to_cart_order'].quantile(0.25)
q3 = order_products_prior['add_to_cart_order'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
outlier_mask = (order_products_prior['add_to_cart_order'] < lower_bound) | (order_products_prior['add_to_cart_order'] > upper_bound)
num_outliers = outlier_mask.sum()
total = len(order_products_prior)
percent_outliers = 100 * num_outliers / total

print('Instacart Outlier Detection:')
print(f'- Method: IQR rule (values < {lower_bound:.2f} or > {upper_bound:.2f})')
print(f'- Outliers in add_to_cart_order: {num_outliers} / {total} ({percent_outliers:.2f}%)')

# --- M5 Walmart Outlier Analysis ---
train_full = pd.read_csv('train_full.csv')

# Outlier detection for Weekly_Sales using IQR rule
q1 = train_full['Weekly_Sales'].quantile(0.25)
q3 = train_full['Weekly_Sales'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
outlier_mask = (train_full['Weekly_Sales'] < lower_bound) | (train_full['Weekly_Sales'] > upper_bound)
num_outliers = outlier_mask.sum()
total = len(train_full)
percent_outliers = 100 * num_outliers / total

print('\nM5 Walmart Outlier Detection:')
print(f'- Method: IQR rule (values < {lower_bound:.2f} or > {upper_bound:.2f})')
print(f'- Outliers in Weekly_Sales: {num_outliers} / {total} ({percent_outliers:.2f}%)') 