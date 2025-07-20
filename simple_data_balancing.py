import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

def analyze_and_fix_skewness():
    """
    Simple data skewness analysis and fixing without external dependencies
    """
    print("=== Simple Data Skewness Analysis and Fixing ===")
    
    # 1. Analyze Instacart data skewness
    if 'order_products__train.csv' in os.listdir('.'):
        print("\n--- Analyzing Instacart Data ---")
        instacart_df = pd.read_csv('order_products__train.csv')
        
        # Analyze product popularity
        product_counts = instacart_df['product_id'].value_counts()
        print(f"Total products: {len(product_counts)}")
        print(f"Products with < 10 orders: {(product_counts < 10).sum()}")
        print(f"Products with < 50 orders: {(product_counts < 50).sum()}")
        print(f"Top 10% products account for {product_counts.head(int(len(product_counts)*0.1)).sum() / len(instacart_df)*100:.1f}% of orders")
        
        # Create balanced product sample
        balanced_products = balance_product_distribution(instacart_df, 'product_id')
        balanced_products.to_csv('order_products__train_balanced.csv', index=False)
        print("Saved balanced Instacart data")
    
    # 2. Analyze M5 Walmart data skewness
    if 'train.csv' in os.listdir('.'):
        print("\n--- Analyzing M5 Walmart Data ---")
        m5_df = pd.read_csv('train.csv')
        
        # Analyze sales distribution
        store_sales = m5_df.groupby('Store')['Weekly_Sales'].sum()
        print(f"Store sales range: {store_sales.min():.0f} to {store_sales.max():.0f}")
        print(f"Top 20% stores account for {store_sales.nlargest(int(len(store_sales)*0.2)).sum() / store_sales.sum()*100:.1f}% of sales")
        
        # Create balanced store sample
        balanced_m5 = balance_store_distribution(m5_df, 'Store', 'Weekly_Sales')
        balanced_m5.to_csv('train_balanced.csv', index=False)
        print("Saved balanced M5 Walmart data")
    
    # 3. Analyze zone data if available
    if 'zone_hour_order_counts.csv' in os.listdir('.'):
        print("\n--- Analyzing Zone Data ---")
        zone_df = pd.read_csv('zone_hour_order_counts.csv')
        
        # Analyze zone distribution
        zone_totals = zone_df.drop('zone', axis=1).sum(axis=1)
        print(f"Zone order range: {zone_totals.min():.0f} to {zone_totals.max():.0f}")
        print(f"Top 30% zones account for {zone_totals.nlargest(int(len(zone_totals)*0.3)).sum() / zone_totals.sum()*100:.1f}% of orders")
        
        # Create balanced zone data
        balanced_zones = balance_zone_distribution(zone_df)
        balanced_zones.to_csv('zone_hour_order_counts_balanced.csv', index=False)
        print("Saved balanced zone data")

def balance_product_distribution(df, product_col, target_samples_per_product=50):
    """
    Balance product distribution by sampling
    """
    print("Balancing product distribution...")
    
    product_counts = df[product_col].value_counts()
    
    balanced_data = []
    
    for product_id, count in product_counts.items():
        product_data = df[df[product_col] == product_id]
        
        if count < target_samples_per_product:
            # Under-sampled: duplicate some samples
            needed = target_samples_per_product - count
            additional_samples = product_data.sample(n=needed, replace=True)
            product_data = pd.concat([product_data, additional_samples])
        elif count > target_samples_per_product * 2:
            # Over-sampled: take a sample
            product_data = product_data.sample(n=target_samples_per_product, random_state=42)
        
        balanced_data.append(product_data)
    
    balanced_df = pd.concat(balanced_data, ignore_index=True)
    
    print(f"Balanced from {len(df)} to {len(balanced_df)} records")
    print(f"Products: {len(df[product_col].unique())} -> {len(balanced_df[product_col].unique())}")
    
    return balanced_df

def balance_store_distribution(df, store_col, sales_col, target_samples_per_store=100):
    """
    Balance store distribution by sampling
    """
    print("Balancing store distribution...")
    
    store_counts = df[store_col].value_counts()
    
    balanced_data = []
    
    for store_id, count in store_counts.items():
        store_data = df[df[store_col] == store_id]
        
        if count < target_samples_per_store:
            # Under-sampled: duplicate some samples
            needed = target_samples_per_store - count
            additional_samples = store_data.sample(n=needed, replace=True)
            store_data = pd.concat([store_data, additional_samples])
        elif count > target_samples_per_store * 2:
            # Over-sampled: take a sample
            store_data = store_data.sample(n=target_samples_per_store, random_state=42)
        
        balanced_data.append(store_data)
    
    balanced_df = pd.concat(balanced_data, ignore_index=True)
    
    print(f"Balanced from {len(df)} to {len(balanced_df)} records")
    print(f"Stores: {len(df[store_col].unique())} -> {len(balanced_df[store_col].unique())}")
    
    return balanced_df

def balance_zone_distribution(df, target_samples_per_zone=1000):
    """
    Balance zone distribution by sampling
    """
    print("Balancing zone distribution...")
    
    zone_col = 'zone'
    zone_counts = df[zone_col].value_counts()
    
    balanced_data = []
    
    for zone_id, count in zone_counts.items():
        zone_data = df[df[zone_col] == zone_id]
        
        if count < target_samples_per_zone:
            # Under-sampled: duplicate some samples
            needed = target_samples_per_zone - count
            additional_samples = zone_data.sample(n=needed, replace=True)
            zone_data = pd.concat([zone_data, additional_samples])
        elif count > target_samples_per_zone * 2:
            # Over-sampled: take a sample
            zone_data = zone_data.sample(n=target_samples_per_zone, random_state=42)
        
        balanced_data.append(zone_data)
    
    balanced_df = pd.concat(balanced_data, ignore_index=True)
    
    print(f"Balanced from {len(df)} to {len(balanced_df)} records")
    print(f"Zones: {len(df[zone_col].unique())} -> {len(balanced_df[zone_col].unique())}")
    
    return balanced_df

def create_synthetic_context_data():
    """
    Create synthetic external context data to enrich the dataset
    """
    print("\n=== Creating Synthetic External Context Data ===")
    
    # Generate weather data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
    weather_data = []
    
    for date in dates:
        # Simulate realistic weather patterns
        hour = date.hour
        month = date.month
        
        # Base temperature by month
        base_temp = 20 + 10 * np.sin(2 * np.pi * (month - 6) / 12)
        
        # Hourly variation
        if 6 <= hour <= 18:  # Daytime
            temp = base_temp + np.random.normal(5, 3)
        else:  # Nighttime
            temp = base_temp + np.random.normal(-5, 2)
        
        # Precipitation (more likely in certain months)
        precip_prob = 0.1 + 0.2 * np.sin(2 * np.pi * (month - 3) / 12)
        precipitation = np.random.exponential(2) if np.random.random() < precip_prob else 0
        
        weather_data.append({
            'datetime': date,
            'temperature': temp,
            'precipitation': precipitation,
            'humidity': np.random.uniform(30, 90),
            'is_weekend': date.weekday() >= 5,
            'is_holiday': np.random.choice([0, 1], p=[0.95, 0.05]),
            'season': ['winter', 'spring', 'summer', 'fall'][(month % 12) // 3]
        })
    
    weather_df = pd.DataFrame(weather_data)
    weather_df.to_csv('synthetic_weather_data.csv', index=False)
    print("Created synthetic weather data")
    
    # Generate event data
    events_data = []
    for date in pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'):
        # Simulate events (sports, concerts, etc.)
        if np.random.random() < 0.1:  # 10% chance of event
            event_types = ['sports', 'concert', 'festival', 'conference', 'holiday']
            event_type = np.random.choice(event_types)
            
            events_data.append({
                'date': date,
                'event_type': event_type,
                'event_impact': np.random.uniform(0.5, 2.0)  # Multiplier for demand
            })
    
    events_df = pd.DataFrame(events_data)
    events_df.to_csv('synthetic_events_data.csv', index=False)
    print("Created synthetic events data")
    
    return weather_df, events_df

def generate_summary_report():
    """
    Generate a summary report of the data balancing process
    """
    print("\n=== Data Balancing Summary Report ===")
    
    report = []
    report.append("# Data Skewness Fix Summary Report\n")
    
    # Check original vs balanced files
    files_to_check = [
        ('order_products__train.csv', 'order_products__train_balanced.csv'),
        ('train.csv', 'train_balanced.csv'),
        ('zone_hour_order_counts.csv', 'zone_hour_order_counts_balanced.csv')
    ]
    
    for original, balanced in files_to_check:
        if original in os.listdir('.') and balanced in os.listdir('.'):
            orig_df = pd.read_csv(original)
            bal_df = pd.read_csv(balanced)
            
            report.append(f"## {original} -> {balanced}")
            report.append(f"- Original records: {len(orig_df):,}")
            report.append(f"- Balanced records: {len(bal_df):,}")
            report.append(f"- Change: {((len(bal_df) - len(orig_df)) / len(orig_df) * 100):+.1f}%")
            report.append("")
    
    # Check synthetic data
    if 'synthetic_weather_data.csv' in os.listdir('.'):
        weather_df = pd.read_csv('synthetic_weather_data.csv')
        report.append("## Synthetic Data Created")
        report.append(f"- Weather data: {len(weather_df):,} records")
        report.append(f"- Time range: {weather_df['datetime'].min()} to {weather_df['datetime'].max()}")
        report.append("")
    
    if 'synthetic_events_data.csv' in os.listdir('.'):
        events_df = pd.read_csv('synthetic_events_data.csv')
        report.append(f"- Events data: {len(events_df):,} records")
        report.append(f"- Event types: {events_df['event_type'].nunique()}")
        report.append("")
    
    report.append("## Next Steps")
    report.append("1. Retrain models with balanced data")
    report.append("2. Compare performance metrics")
    report.append("3. Integrate synthetic context data")
    report.append("4. Set up Google Analytics integration")
    
    # Save report
    with open('data_balancing_report.md', 'w') as f:
        f.write('\n'.join(report))
    
    print("Generated data balancing summary report")

if __name__ == "__main__":
    import os
    
    # Run the complete data balancing process
    analyze_and_fix_skewness()
    create_synthetic_context_data()
    generate_summary_report()
    
    print("\n=== Data Skewness Fixing Complete ===")
    print("Check the generated files and report for details.") 