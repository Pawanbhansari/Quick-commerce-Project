import pandas as pd
import numpy as np

# --- Load Data ---
zone_hour = pd.read_csv('zone_hour_order_counts.csv', index_col=0)
zone_dow = pd.read_csv('zone_dow_order_counts.csv', index_col=0)

# --- Feature Engineering for zone-hour data ---
zone_hour_long = zone_hour.reset_index().melt(id_vars='zone', var_name='hour', value_name='demand')
zone_hour_long['hour'] = zone_hour_long['hour'].astype(int)

# Rolling average and lag features (window=3, 6, 12 hours)
for window in [3, 6, 12]:
    zone_hour_long[f'rolling_avg_{window}h'] = zone_hour_long.groupby('zone')['demand'].transform(lambda x: x.rolling(window, min_periods=1).mean())
for lag in [1, 2, 3]:
    zone_hour_long[f'lag_{lag}h'] = zone_hour_long.groupby('zone')['demand'].shift(lag)

# One-hot encode hour, but keep the original 'hour' column
hour_onehot = pd.get_dummies(zone_hour_long['hour'], prefix='hour')
zone_hour_long = pd.concat([zone_hour_long, hour_onehot], axis=1)

# Zone demand rank by total demand (for interpretability)
zone_totals = zone_hour_long.groupby('zone')['demand'].sum()
zone_totals_rank = zone_totals.rank(ascending=False).astype(int)
zone_hour_long['zone_demand_rank'] = zone_hour_long['zone'].map(zone_totals_rank.to_dict())

zone_hour_long.to_csv('zone_hour_features.csv', index=False)

# --- Feature Engineering for zone-dow data ---
zone_dow_long = zone_dow.reset_index().melt(id_vars='zone', var_name='dow', value_name='demand')
zone_dow_long['dow'] = zone_dow_long['dow'].astype(int)

# Rolling average and lag features (window=2, 3 days)
for window in [2, 3]:
    zone_dow_long[f'rolling_avg_{window}d'] = zone_dow_long.groupby('zone')['demand'].transform(lambda x: x.rolling(window, min_periods=1).mean())
for lag in [1, 2]:
    zone_dow_long[f'lag_{lag}d'] = zone_dow_long.groupby('zone')['demand'].shift(lag)

# One-hot encode day of week, but keep the original 'dow' column
onehot_dow = pd.get_dummies(zone_dow_long['dow'], prefix='dow')
zone_dow_long = pd.concat([zone_dow_long, onehot_dow], axis=1)

# Zone demand rank by total demand
zone_totals_dow = zone_dow_long.groupby('zone')['demand'].sum()
zone_totals_dow_rank = zone_totals_dow.rank(ascending=False).astype(int)
zone_dow_long['zone_demand_rank'] = zone_dow_long['zone'].map(zone_totals_dow_rank.to_dict())

zone_dow_long.to_csv('zone_dow_features.csv', index=False)

print('Feature engineering complete. Outputs:')
print(' - zone_hour_features.csv')
print(' - zone_dow_features.csv') 