import pandas as pd

# --- Instacart Data Cleaning ---
print('Cleaning Instacart data...')
orders = pd.read_csv('orders.csv')
order_products_train = pd.read_csv('order_products__train.csv')
order_products_prior = pd.read_csv('order_products__prior.csv')
products = pd.read_csv('products.csv')
aisles = pd.read_csv('aisles.csv')
departments = pd.read_csv('departments.csv')

# Handle missing values in days_since_prior_order (fill with 0 for first order)
orders['days_since_prior_order'] = orders['days_since_prior_order'].fillna(0)

# Merge product info for richer features
df_products_full = products.merge(aisles, on='aisle_id', how='left').merge(departments, on='department_id', how='left')

# --- M5 Walmart Data Cleaning ---
print('Cleaning M5 Walmart data...')
train = pd.read_csv('train.csv')
test = pd.read_csv('test.csv')
features = pd.read_csv('features.csv')
stores = pd.read_csv('stores.csv')

# Convert Date columns to datetime
train['Date'] = pd.to_datetime(train['Date'])
test['Date'] = pd.to_datetime(test['Date'])
features['Date'] = pd.to_datetime(features['Date'])

# Handle missing values in features (fill with 0 for MarkDowns, forward fill for CPI/Unemployment)
for col in ['MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5']:
    features[col] = features[col].fillna(0)
features['CPI'] = features['CPI'].fillna(method='ffill')
features['Unemployment'] = features['Unemployment'].fillna(method='ffill')

# Merge train/test with features and stores
def merge_m5(df):
    df = df.merge(features, on=['Store', 'Date', 'IsHoliday'], how='left')
    df = df.merge(stores, on='Store', how='left')
    return df

train_full = merge_m5(train)
test_full = merge_m5(test)

# Save cleaned data for further analysis
orders.to_csv('orders_cleaned.csv', index=False)
df_products_full.to_csv('products_full.csv', index=False)
train_full.to_csv('train_full.csv', index=False)
test_full.to_csv('test_full.csv', index=False)

print('Data cleaning complete. Cleaned files saved.') 