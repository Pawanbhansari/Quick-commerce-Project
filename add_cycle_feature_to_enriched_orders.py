import pandas as pd

# Function to map hour to cycle
def hour_to_cycle(hour):
    if 0 <= hour < 6:
        return 1
    elif 6 <= hour < 12:
        return 2
    elif 12 <= hour < 18:
        return 3
    else:
        return 4

input_file = 'orders_enriched_for_ml.csv'
output_file = 'orders_enriched_with_cycle.csv'

# Clear output file if exists
with open(output_file, 'w') as f:
    pass

chunk_size = 100_000
first_chunk = True
chunk_num = 0
for chunk in pd.read_csv(input_file, chunksize=chunk_size):
    chunk['cycle'] = chunk['hour'].apply(hour_to_cycle)
    chunk.to_csv(output_file, mode='a', index=False, header=first_chunk)
    chunk_num += 1
    print(f"Processed chunk {chunk_num} ({chunk_size} rows per chunk)")
    first_chunk = False

print('Added cycle feature to orders_enriched_for_ml.csv and saved as orders_enriched_with_cycle.csv') 