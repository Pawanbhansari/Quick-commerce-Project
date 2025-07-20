import pandas as pd
from collections import defaultdict

# Aggregation columns (use 'cycle' instead of 'hour')
agg_cols = ['custom_category', 'product_id', 'product_name', 'cycle', 'day_of_week', 'season', 'is_holiday']

# Use a dictionary to accumulate counts
agg_dict = defaultdict(int)

chunk_size = 100_000
for chunk in pd.read_csv('orders_enriched_with_cycle.csv', chunksize=chunk_size):
    grouped = chunk.groupby(agg_cols).size()
    for idx, count in grouped.items():
        agg_dict[idx] += count

# Convert to DataFrame
rows = [list(idx) + [count] for idx, count in agg_dict.items()]
train_data = pd.DataFrame(rows, columns=agg_cols + ['sales_count'])

# Save for ML model training
train_data.to_csv('product_demand_training_data_with_cycle.csv', index=False)

print('Aggregated training data saved as product_demand_training_data_with_cycle.csv (by cycle, chunked)') 