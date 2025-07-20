import pandas as pd

# Load Instacart datasets
df_orders = pd.read_csv('orders.csv')
df_order_products_train = pd.read_csv('order_products__train.csv')
df_order_products_prior = pd.read_csv('order_products__prior.csv')
df_products = pd.read_csv('products.csv')
df_aisles = pd.read_csv('aisles.csv')
df_departments = pd.read_csv('departments.csv')

# Display basic info
def print_basic_info(df, name):
    print(f'--- {name} ---')
    print(df.info())
    print(df.head())
    print(df.describe(include="all"))
    print('\n')

print_basic_info(df_orders, 'orders')
print_basic_info(df_order_products_train, 'order_products__train')
print_basic_info(df_order_products_prior, 'order_products__prior')
print_basic_info(df_products, 'products')
print_basic_info(df_aisles, 'aisles')
print_basic_info(df_departments, 'departments') 