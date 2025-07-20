import pandas as pd
from sklearn.preprocessing import LabelEncoder

# --- Instacart Encoding ---
print('Encoding Instacart features...')
orders = pd.read_csv('orders_features.csv')
products = pd.read_csv('products_features.csv')

# Label encoding for eval_set
le_eval_set = LabelEncoder()
orders['eval_set_encoded'] = le_eval_set.fit_transform(orders['eval_set'])

# Label encoding for aisle and department
le_aisle = LabelEncoder()
le_department = LabelEncoder()
products['aisle_encoded'] = le_aisle.fit_transform(products['aisle'])
products['department_encoded'] = le_department.fit_transform(products['department'])

# One-hot encoding for eval_set (for linear models)
orders_onehot = pd.get_dummies(orders, columns=['eval_set'])

# One-hot encoding for aisle and department (for linear models)
products_onehot = pd.get_dummies(products, columns=['aisle', 'department'])

orders.to_csv('orders_encoded.csv', index=False)
products.to_csv('products_encoded.csv', index=False)
orders_onehot.to_csv('orders_onehot.csv', index=False)
products_onehot.to_csv('products_onehot.csv', index=False)

# --- M5 Walmart Encoding ---
print('Encoding M5 Walmart features...')
train = pd.read_csv('train_features.csv')

# Label encoding for Type and Store_Size_Bucket
le_type = LabelEncoder()
le_size = LabelEncoder()
train['Type_encoded'] = le_type.fit_transform(train['Type'])
train['Store_Size_Bucket_encoded'] = le_size.fit_transform(train['Store_Size_Bucket'].astype(str))

# One-hot encoding for Type and Store_Size_Bucket
train_onehot = pd.get_dummies(train, columns=['Type', 'Store_Size_Bucket'])

train.to_csv('train_encoded.csv', index=False)
train_onehot.to_csv('train_onehot.csv', index=False)

print('Encoding complete. Encoded files saved.') 