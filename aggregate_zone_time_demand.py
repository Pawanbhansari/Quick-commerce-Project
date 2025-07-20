import pandas as pd
import matplotlib.pyplot as plt

# Read the data
orders = pd.read_csv('orders_with_zones.csv')

# Aggregate by zone and order_hour_of_day
zone_hour = orders.groupby(['zone', 'order_hour_of_day']).size().reset_index(name='num_orders')
zone_hour_pivot = zone_hour.pivot(index='zone', columns='order_hour_of_day', values='num_orders').fillna(0)

# Plot: Orders by zone and hour of day
plt.figure(figsize=(12, 6))
for zone in zone_hour['zone'].unique():
    plt.plot(zone_hour_pivot.columns, zone_hour_pivot.loc[zone], label=f'Zone {zone}')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Orders')
plt.title('Orders by Zone and Hour of Day')
plt.legend(title='Zone', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('orders_by_zone_hour.png')
plt.close()

# Aggregate by zone and order_dow
zone_dow = orders.groupby(['zone', 'order_dow']).size().reset_index(name='num_orders')
zone_dow_pivot = zone_dow.pivot(index='zone', columns='order_dow', values='num_orders').fillna(0)

# Plot: Orders by zone and day of week
plt.figure(figsize=(12, 6))
for zone in zone_dow['zone'].unique():
    plt.plot(zone_dow_pivot.columns, zone_dow_pivot.loc[zone], label=f'Zone {zone}')
plt.xlabel('Day of Week (0=Sunday)')
plt.ylabel('Number of Orders')
plt.title('Orders by Zone and Day of Week')
plt.legend(title='Zone', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('orders_by_zone_dow.png')
plt.close()

# Save summary tables
zone_hour_pivot.to_csv('zone_hour_order_counts.csv')
zone_dow_pivot.to_csv('zone_dow_order_counts.csv')

print('Aggregation and plots complete. Outputs:')
print(' - zone_hour_order_counts.csv')
print(' - zone_dow_order_counts.csv')
print(' - orders_by_zone_hour.png')
print(' - orders_by_zone_dow.png') 