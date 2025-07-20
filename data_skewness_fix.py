import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class DataSkewnessFixer:
    """
    Comprehensive solution to fix data skewness issues in the Quick Commerce project
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.product_clusters = None
        self.zone_weights = None
        
    def analyze_skewness(self, df, target_col, group_col=None):
        """
        Analyze data skewness and provide detailed statistics
        """
        print(f"=== Skewness Analysis for {target_col} ===")
        
        # Basic statistics
        print(f"Mean: {df[target_col].mean():.2f}")
        print(f"Median: {df[target_col].median():.2f}")
        print(f"Std: {df[target_col].std():.2f}")
        print(f"Skewness: {df[target_col].skew():.2f}")
        
        # Distribution analysis
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        print("\nPercentiles:")
        for p in percentiles:
            print(f"{p}th percentile: {df[target_col].quantile(p/100):.2f}")
        
        # Outlier analysis using IQR
        Q1 = df[target_col].quantile(0.25)
        Q3 = df[target_col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[target_col] < Q1 - 1.5*IQR) | (df[target_col] > Q3 + 1.5*IQR)]
        print(f"\nOutliers (IQR method): {len(outliers)} ({len(outliers)/len(df)*100:.2f}%)")
        
        # Group analysis if specified
        if group_col:
            print(f"\n=== Skewness by {group_col} ===")
            group_stats = df.groupby(group_col)[target_col].agg(['count', 'mean', 'std', 'skew'])
            print(group_stats)
            
            # Visualize distribution by group
            plt.figure(figsize=(12, 6))
            df.boxplot(column=target_col, by=group_col, ax=plt.gca())
            plt.title(f'{target_col} Distribution by {group_col}')
            plt.suptitle('')
            plt.savefig(f'skewness_analysis_{target_col}_by_{group_col}.png')
            plt.close()
        
        return {
            'outliers': outliers,
            'group_stats': group_stats if group_col else None,
            'iqr_bounds': (Q1 - 1.5*IQR, Q3 + 1.5*IQR)
        }
    
    def balance_product_popularity(self, df, product_col, target_col, method='smote'):
        """
        Balance product popularity using various techniques
        """
        print(f"\n=== Balancing Product Popularity ===")
        
        # Analyze current distribution
        product_counts = df[product_col].value_counts()
        print(f"Products with < 10 orders: {(product_counts < 10).sum()}")
        print(f"Products with < 50 orders: {(product_counts < 50).sum()}")
        print(f"Products with < 100 orders: {(product_counts < 100).sum()}")
        
        if method == 'smote':
            return self._apply_smote_balancing(df, product_col, target_col)
        elif method == 'clustering':
            return self._apply_clustering_balancing(df, product_col, target_col)
        elif method == 'synthetic':
            return self._apply_synthetic_generation(df, product_col, target_col)
        else:
            return self._apply_weighted_sampling(df, product_col, target_col)
    
    def _apply_smote_balancing(self, df, product_col, target_col):
        """
        Apply SMOTE to balance rare products
        """
        # Prepare features for SMOTE
        feature_cols = [col for col in df.columns if col not in [product_col, target_col]]
        
        # Create product popularity categories
        product_counts = df[product_col].value_counts()
        df['product_popularity'] = df[product_col].map(product_counts)
        
        # Categorize products
        df['product_category'] = pd.cut(df['product_popularity'], 
                                       bins=[0, 50, 200, 1000, float('inf')],
                                       labels=['rare', 'uncommon', 'common', 'popular'])
        
        # Apply SMOTE for rare products
        rare_products = df[df['product_category'] == 'rare']
        if len(rare_products) > 0:
            smote = SMOTE(random_state=42)
            X = rare_products[feature_cols].fillna(0)
            y = rare_products[target_col]
            
            try:
                X_resampled, y_resampled = smote.fit_resample(X, y)
                
                # Create synthetic samples
                synthetic_df = pd.DataFrame(X_resampled, columns=feature_cols)
                synthetic_df[target_col] = y_resampled
                synthetic_df[product_col] = rare_products[product_col].iloc[0]  # Assign to rare product
                synthetic_df['product_popularity'] = rare_products['product_popularity'].iloc[0]
                synthetic_df['product_category'] = 'rare'
                
                # Combine original and synthetic data
                balanced_df = pd.concat([df, synthetic_df], ignore_index=True)
                print(f"Added {len(synthetic_df)} synthetic samples for rare products")
                
            except Exception as e:
                print(f"SMOTE failed: {e}")
                balanced_df = df
        else:
            balanced_df = df
            
        return balanced_df
    
    def _apply_clustering_balancing(self, df, product_col, target_col):
        """
        Use clustering to group similar products and balance data
        """
        # Create product features
        product_features = df.groupby(product_col).agg({
            target_col: ['mean', 'std', 'count'],
            'order_dow': 'mean',
            'order_hour_of_day': 'mean'
        }).fillna(0)
        
        product_features.columns = ['_'.join(col).strip() for col in product_features.columns]
        
        # Cluster products
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(product_features)
        
        n_clusters = min(10, len(product_features))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        product_features['cluster'] = kmeans.fit_predict(features_scaled)
        
        # Balance clusters
        cluster_counts = product_features['cluster'].value_counts()
        target_count = cluster_counts.median()
        
        balanced_products = []
        for cluster in range(n_clusters):
            cluster_products = product_features[product_features['cluster'] == cluster].index.tolist()
            if len(cluster_products) < target_count:
                # Duplicate some products to balance
                needed = int(target_count - len(cluster_products))
                additional = np.random.choice(cluster_products, size=needed, replace=True)
                cluster_products.extend(additional)
            balanced_products.extend(cluster_products)
        
        # Filter dataframe to balanced products
        balanced_df = df[df[product_col].isin(balanced_products)].copy()
        
        print(f"Balanced products from {len(df[product_col].unique())} to {len(balanced_products)}")
        
        return balanced_df
    
    def _apply_synthetic_generation(self, df, product_col, target_col):
        """
        Generate synthetic data for rare products
        """
        # Identify rare products
        product_counts = df[product_col].value_counts()
        rare_products = product_counts[product_counts < 50].index.tolist()
        
        synthetic_data = []
        
        for product in rare_products:
            product_data = df[df[product_col] == product]
            
            if len(product_data) > 0:
                # Generate synthetic samples based on existing patterns
                for _ in range(min(50 - len(product_data), 20)):  # Add up to 20 synthetic samples
                    # Randomly sample from existing data with noise
                    sample = product_data.sample(1).iloc[0].copy()
                    
                    # Add noise to numeric features
                    numeric_cols = product_data.select_dtypes(include=[np.number]).columns
                    for col in numeric_cols:
                        if col != product_col and col != target_col:
                            noise = np.random.normal(0, product_data[col].std() * 0.1)
                            sample[col] += noise
                    
                    # Modify target with realistic variation
                    target_noise = np.random.normal(0, product_data[target_col].std() * 0.2)
                    sample[target_col] = max(0, sample[target_col] + target_noise)
                    
                    synthetic_data.append(sample)
        
        if synthetic_data:
            synthetic_df = pd.DataFrame(synthetic_data)
            balanced_df = pd.concat([df, synthetic_df], ignore_index=True)
            print(f"Generated {len(synthetic_data)} synthetic samples")
        else:
            balanced_df = df
            
        return balanced_df
    
    def _apply_weighted_sampling(self, df, product_col, target_col):
        """
        Apply weighted sampling to balance product distribution
        """
        # Calculate weights inversely proportional to product frequency
        product_counts = df[product_col].value_counts()
        weights = 1 / product_counts[df[product_col]].values
        
        # Normalize weights
        weights = weights / weights.sum()
        
        # Sample with replacement
        sample_indices = np.random.choice(len(df), size=len(df), p=weights, replace=True)
        balanced_df = df.iloc[sample_indices].copy()
        
        print(f"Applied weighted sampling to balance product distribution")
        
        return balanced_df
    
    def balance_geographic_data(self, df, zone_col, target_col):
        """
        Balance data across different geographic zones
        """
        print(f"\n=== Balancing Geographic Data ===")
        
        # Analyze zone distribution
        zone_stats = df.groupby(zone_col)[target_col].agg(['count', 'mean', 'std'])
        print("Zone distribution before balancing:")
        print(zone_stats)
        
        # Calculate target count per zone (median)
        target_count = zone_stats['count'].median()
        
        balanced_zones = []
        
        for zone in df[zone_col].unique():
            zone_data = df[df[zone_col] == zone]
            
            if len(zone_data) < target_count:
                # Under-sample if too many samples
                zone_data = zone_data.sample(n=int(target_count), random_state=42)
            elif len(zone_data) > target_count * 1.5:
                # Over-sample if too few samples
                additional_needed = int(target_count - len(zone_data))
                additional_samples = zone_data.sample(n=additional_needed, replace=True, random_state=42)
                zone_data = pd.concat([zone_data, additional_samples])
            
            balanced_zones.append(zone_data)
        
        balanced_df = pd.concat(balanced_zones, ignore_index=True)
        
        print("\nZone distribution after balancing:")
        print(balanced_df.groupby(zone_col)[target_col].agg(['count', 'mean', 'std']))
        
        return balanced_df
    
    def add_external_context(self, df, date_col, location_col):
        """
        Add external context data (weather, events, etc.)
        """
        print(f"\n=== Adding External Context ===")
        
        # Convert date column to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Add weather-like features (simulated for now)
        df['temperature'] = np.random.normal(20, 10, len(df))  # Simulated temperature
        df['precipitation'] = np.random.exponential(2, len(df))  # Simulated precipitation
        df['humidity'] = np.random.uniform(30, 90, len(df))  # Simulated humidity
        
        # Add event features
        df['is_weekend'] = df[date_col].dt.weekday.isin([5, 6]).astype(int)
        df['is_holiday'] = np.random.choice([0, 1], len(df), p=[0.95, 0.05])  # Simulated holidays
        df['is_event_day'] = np.random.choice([0, 1], len(df), p=[0.9, 0.1])  # Simulated events
        
        # Add seasonal features
        df['season'] = df[date_col].dt.month.map({
            12: 'winter', 1: 'winter', 2: 'winter',
            3: 'spring', 4: 'spring', 5: 'spring',
            6: 'summer', 7: 'summer', 8: 'summer',
            9: 'fall', 10: 'fall', 11: 'fall'
        })
        
        print("Added external context features: temperature, precipitation, humidity, events, seasons")
        
        return df
    
    def create_balanced_dataset(self, input_file, output_file):
        """
        Main function to create a balanced dataset
        """
        print("=== Creating Balanced Dataset ===")
        
        # Load data
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} records from {input_file}")
        
        # Analyze original skewness
        if 'add_to_cart_order' in df.columns:
            self.analyze_skewness(df, 'add_to_cart_order', 'department')
        
        if 'Weekly_Sales' in df.columns:
            self.analyze_skewness(df, 'Weekly_Sales', 'Store')
        
        # Apply balancing techniques
        if 'product_id' in df.columns and 'add_to_cart_order' in df.columns:
            df = self.balance_product_popularity(df, 'product_id', 'add_to_cart_order', method='synthetic')
        
        if 'zone' in df.columns:
            df = self.balance_geographic_data(df, 'zone', 'demand')
        
        # Add external context
        if 'order_date' in df.columns:
            df = self.add_external_context(df, 'order_date', 'zone')
        
        # Save balanced dataset
        df.to_csv(output_file, index=False)
        print(f"Saved balanced dataset to {output_file}")
        
        # Final analysis
        print("\n=== Final Dataset Statistics ===")
        print(f"Total records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        
        return df

# Example usage
if __name__ == "__main__":
    import os
    fixer = DataSkewnessFixer()
    
    # Fix Instacart data
    if 'order_products__train.csv' in os.listdir('.'):
        print("Fixing Instacart data skewness...")
        balanced_instacart = fixer.create_balanced_dataset(
            'order_products__train.csv',
            'order_products__train_balanced.csv'
        )
    
    # Fix M5 Walmart data
    if 'train.csv' in os.listdir('.'):
        print("\nFixing M5 Walmart data skewness...")
        balanced_m5 = fixer.create_balanced_dataset(
            'train.csv',
            'train_balanced.csv'
        )
    
    print("\nData skewness fixing complete!") 