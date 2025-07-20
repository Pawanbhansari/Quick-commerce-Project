import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
import os

class GoogleAnalyticsIntegration:
    """
    Google Analytics integration for enriching Quick Commerce data
    """
    
    def __init__(self, property_id=None, api_key=None):
        self.property_id = property_id or os.getenv('GA_PROPERTY_ID')
        self.api_key = api_key or os.getenv('GA_API_KEY')
        self.base_url = "https://analyticsdata.googleapis.com/v1beta"
        
    def fetch_real_time_data(self, dimensions=None, metrics=None):
        """
        Fetch real-time data from Google Analytics
        """
        if not self.property_id:
            print("Warning: No GA Property ID provided. Using simulated data.")
            return self._generate_simulated_ga_data()
        
        url = f"{self.base_url}/properties/{self.property_id}:runRealtimeReport"
        
        # Default dimensions and metrics
        if dimensions is None:
            dimensions = [
                {"name": "dateHourMinute"},
                {"name": "city"},
                {"name": "deviceCategory"},
                {"name": "sourceMedium"}
            ]
        
        if metrics is None:
            metrics = [
                {"name": "activeUsers"},
                {"name": "screenPageViews"},
                {"name": "eventCount"},
                {"name": "averageSessionDuration"}
            ]
        
        payload = {
            "dimensions": dimensions,
            "metrics": metrics
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching GA data: {e}")
            print("Using simulated data instead.")
            return self._generate_simulated_ga_data()
    
    def _generate_simulated_ga_data(self):
        """
        Generate realistic simulated Google Analytics data
        """
        print("Generating simulated Google Analytics data...")
        
        # Generate time series data
        now = datetime.now()
        hours = []
        for i in range(24):
            time_point = now - timedelta(hours=i)
            hours.append(time_point.strftime("%Y-%m-%d %H:%M"))
        
        # Simulate realistic patterns
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia']
        devices = ['desktop', 'mobile', 'tablet']
        sources = ['google / organic', 'facebook / social', 'direct / none', 'email / email']
        
        data = []
        for hour in hours:
            for city in cities:
                for device in devices:
                    for source in sources:
                        # Simulate realistic user behavior patterns
                        base_users = np.random.poisson(50)  # Base user count
                        
                        # Time-based patterns
                        hour_of_day = int(hour.split()[-1])
                        if 9 <= hour_of_day <= 17:  # Business hours
                            base_users *= 1.5
                        elif 18 <= hour_of_day <= 22:  # Evening peak
                            base_users *= 2.0
                        else:  # Night hours
                            base_users *= 0.3
                        
                        # Device-based patterns
                        if device == 'mobile':
                            base_users *= 1.8
                        elif device == 'tablet':
                            base_users *= 0.4
                        
                        # Source-based patterns
                        if 'organic' in source:
                            base_users *= 1.2
                        elif 'social' in source:
                            base_users *= 0.8
                        
                        # City-based patterns (simulate NYC focus)
                        if city == 'New York':
                            base_users *= 2.0
                        
                        # Add some randomness
                        base_users = max(1, int(base_users * np.random.uniform(0.8, 1.2)))
                        
                        # Calculate related metrics
                        page_views = int(base_users * np.random.uniform(2, 5))
                        events = int(page_views * np.random.uniform(3, 8))
                        session_duration = np.random.uniform(60, 300)  # seconds
                        
                        data.append({
                            'dateHourMinute': hour,
                            'city': city,
                            'deviceCategory': device,
                            'sourceMedium': source,
                            'activeUsers': base_users,
                            'screenPageViews': page_views,
                            'eventCount': events,
                            'averageSessionDuration': session_duration
                        })
        
        return {
            'dimensionHeaders': [
                {'name': 'dateHourMinute'},
                {'name': 'city'},
                {'name': 'deviceCategory'},
                {'name': 'sourceMedium'}
            ],
            'metricHeaders': [
                {'name': 'activeUsers'},
                {'name': 'screenPageViews'},
                {'name': 'eventCount'},
                {'name': 'averageSessionDuration'}
            ],
            'rows': data
        }
    
    def process_ga_data(self, ga_response):
        """
        Process Google Analytics response into a pandas DataFrame
        """
        if 'rows' not in ga_response:
            print("No data rows found in GA response")
            return pd.DataFrame()
        
        data = []
        for row in ga_response['rows']:
            row_data = {}
            
            # Process dimensions
            for i, header in enumerate(ga_response.get('dimensionHeaders', [])):
                row_data[header['name']] = row['dimensionValues'][i]['value']
            
            # Process metrics
            for i, header in enumerate(ga_response.get('metricHeaders', [])):
                row_data[header['name']] = float(row['metricValues'][i]['value'])
            
            data.append(row_data)
        
        df = pd.DataFrame(data)
        
        # Convert time column
        if 'dateHourMinute' in df.columns:
            df['dateHourMinute'] = pd.to_datetime(df['dateHourMinute'])
        
        return df
    
    def enrich_order_data(self, orders_df, ga_df):
        """
        Enrich order data with Google Analytics insights
        """
        print("Enriching order data with Google Analytics insights...")
        
        # Merge GA data with orders based on time and location
        enriched_df = orders_df.copy()
        
        # Add GA-derived features
        enriched_df['ga_active_users'] = 0
        enriched_df['ga_page_views'] = 0
        enriched_df['ga_events'] = 0
        enriched_df['ga_avg_session_duration'] = 0
        enriched_df['ga_mobile_ratio'] = 0
        enriched_df['ga_organic_traffic_ratio'] = 0
        
        # For each order, find matching GA data
        for idx, order in enriched_df.iterrows():
            # Extract time and location from order
            order_time = pd.to_datetime(order.get('order_date', datetime.now()))
            order_hour = order_time.hour
            
            # Find matching GA data for the same hour
            matching_ga = ga_df[ga_df['dateHourMinute'].dt.hour == order_hour]
            
            if len(matching_ga) > 0:
                # Aggregate GA metrics for the hour
                enriched_df.loc[idx, 'ga_active_users'] = matching_ga['activeUsers'].sum()
                enriched_df.loc[idx, 'ga_page_views'] = matching_ga['screenPageViews'].sum()
                enriched_df.loc[idx, 'ga_events'] = matching_ga['eventCount'].sum()
                enriched_df.loc[idx, 'ga_avg_session_duration'] = matching_ga['averageSessionDuration'].mean()
                
                # Calculate ratios
                total_users = matching_ga['activeUsers'].sum()
                if total_users > 0:
                    mobile_users = matching_ga[matching_ga['deviceCategory'] == 'mobile']['activeUsers'].sum()
                    organic_users = matching_ga[matching_ga['sourceMedium'].str.contains('organic', na=False)]['activeUsers'].sum()
                    
                    enriched_df.loc[idx, 'ga_mobile_ratio'] = mobile_users / total_users
                    enriched_df.loc[idx, 'ga_organic_traffic_ratio'] = organic_users / total_users
        
        # Add derived features
        enriched_df['ga_engagement_rate'] = enriched_df['ga_events'] / enriched_df['ga_page_views'].replace(0, 1)
        enriched_df['ga_traffic_intensity'] = enriched_df['ga_active_users'] / enriched_df['ga_active_users'].max()
        
        print(f"Enriched {len(enriched_df)} orders with GA data")
        return enriched_df
    
    def create_behavioral_features(self, ga_df):
        """
        Create behavioral features from GA data
        """
        print("Creating behavioral features from GA data...")
        
        # Aggregate by time periods
        hourly_features = ga_df.groupby(ga_df['dateHourMinute'].dt.hour).agg({
            'activeUsers': ['mean', 'std', 'sum'],
            'screenPageViews': ['mean', 'sum'],
            'eventCount': ['mean', 'sum'],
            'averageSessionDuration': 'mean'
        }).fillna(0)
        
        hourly_features.columns = ['_'.join(col).strip() for col in hourly_features.columns]
        
        # Device preferences
        device_features = ga_df.groupby('deviceCategory')['activeUsers'].sum()
        device_ratios = device_features / device_features.sum()
        
        # Traffic source analysis
        source_features = ga_df.groupby('sourceMedium')['activeUsers'].sum()
        source_ratios = source_features / source_features.sum()
        
        # Geographic patterns
        city_features = ga_df.groupby('city')['activeUsers'].sum()
        city_ratios = city_features / city_features.sum()
        
        behavioral_features = {
            'hourly_patterns': hourly_features,
            'device_preferences': device_ratios,
            'traffic_sources': source_ratios,
            'geographic_distribution': city_ratios
        }
        
        return behavioral_features
    
    def save_ga_data(self, ga_df, filename='ga_enriched_data.csv'):
        """
        Save enriched GA data to CSV
        """
        ga_df.to_csv(filename, index=False)
        print(f"Saved GA data to {filename}")
        
        # Also save behavioral features
        behavioral_features = self.create_behavioral_features(ga_df)
        
        # Save hourly patterns
        behavioral_features['hourly_patterns'].to_csv('ga_hourly_patterns.csv')
        
        # Save device preferences
        behavioral_features['device_preferences'].to_csv('ga_device_preferences.csv')
        
        # Save traffic sources
        behavioral_features['traffic_sources'].to_csv('ga_traffic_sources.csv')
        
        # Save geographic distribution
        behavioral_features['geographic_distribution'].to_csv('ga_geographic_distribution.csv')
        
        print("Saved behavioral features to separate CSV files")

def main():
    """
    Main function to demonstrate GA integration
    """
    print("=== Google Analytics Integration for Quick Commerce ===")
    
    # Initialize GA integration
    ga_integration = GoogleAnalyticsIntegration()
    
    # Fetch real-time data
    print("Fetching Google Analytics data...")
    ga_response = ga_integration.fetch_real_time_data()
    
    # Process GA data
    ga_df = ga_integration.process_ga_data(ga_response)
    print(f"Processed {len(ga_df)} GA data points")
    
    # Save GA data
    ga_integration.save_ga_data(ga_df)
    
    # Enrich existing order data if available
    if 'orders.csv' in os.listdir('.'):
        print("Enriching existing order data...")
        orders_df = pd.read_csv('orders.csv')
        enriched_orders = ga_integration.enrich_order_data(orders_df, ga_df)
        enriched_orders.to_csv('orders_enriched_with_ga.csv', index=False)
        print("Saved enriched orders to orders_enriched_with_ga.csv")
    
    # Create summary report
    print("\n=== GA Integration Summary ===")
    print(f"Total GA data points: {len(ga_df)}")
    print(f"Time range: {ga_df['dateHourMinute'].min()} to {ga_df['dateHourMinute'].max()}")
    print(f"Cities covered: {ga_df['city'].nunique()}")
    print(f"Devices tracked: {ga_df['deviceCategory'].nunique()}")
    print(f"Traffic sources: {ga_df['sourceMedium'].nunique()}")
    
    # Show sample of behavioral patterns
    behavioral_features = ga_integration.create_behavioral_features(ga_df)
    print("\nDevice Preferences:")
    print(behavioral_features['device_preferences'])
    
    print("\nTop Traffic Sources:")
    print(behavioral_features['traffic_sources'].head())

if __name__ == "__main__":
    main() 