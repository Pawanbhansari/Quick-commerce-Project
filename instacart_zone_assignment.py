import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

# Load orders data
orders = pd.read_csv('orders.csv')

# Aggregate user order patterns (e.g., order frequency, avg order hour, avg days between orders)
user_features = orders.groupby('user_id').agg({
    'order_id': 'count',
    'order_hour_of_day': 'mean',
    'days_since_prior_order': 'mean',
    'order_dow': 'mean'
}).rename(columns={
    'order_id': 'order_count',
    'order_hour_of_day': 'avg_order_hour',
    'days_since_prior_order': 'avg_days_between',
    'order_dow': 'avg_order_dow'
}).fillna(0)

# K-means clustering to assign zones
n_zones = 10
kmeans = KMeans(n_clusters=n_zones, random_state=42)
user_features['zone'] = kmeans.fit_predict(user_features)

# Map user_id to zone
user_zone_map = user_features['zone'].to_dict()
orders['zone'] = orders['user_id'].map(user_zone_map)

# Save orders with zone assignment
orders.to_csv('orders_with_zones.csv', index=False)
print('Zone assignment complete. Saved as orders_with_zones.csv.') 