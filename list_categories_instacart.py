import pandas as pd

# Load product and department data
products = pd.read_csv('products.csv')
departments = pd.read_csv('departments.csv')

# Merge to get department names for each product
products = products.merge(departments, on='department_id', how='left')

# List unique categories (departments)
categories = products['department'].unique()

print('Unique product categories (departments):')
for cat in categories:
    print('-', cat) 