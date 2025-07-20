# Data Skewness Solution Plan
## Addressing Data Imbalance in Quick Commerce Project

### Current Problems Identified

1. **Product Popularity Skewness**
   - 4.18% outliers in add_to_cart_order (Instacart)
   - 8.43% outliers in Weekly_Sales (M5 Walmart)
   - Small subset of products dominate orders
   - Long tail of rare products with minimal data

2. **User Activity Imbalance**
   - Highly active users vs. occasional shoppers
   - Inconsistent ordering patterns
   - Missing behavioral context

3. **Geographic & Temporal Skewness**
   - Some zones have 3-4x higher order volumes
   - Extreme peaks during certain hours/days
   - Weekend vs. weekday imbalance

### Solution Strategy: Multi-Source Data Enrichment

#### 1. Google Analytics Integration

**Data Sources to Add:**
- **Real-time User Behavior**: Page views, session duration, cart abandonment
- **Traffic Sources**: Organic, paid, social, direct traffic patterns
- **Device & Location Data**: Mobile vs. desktop, geographic distribution
- **Event Tracking**: Product views, add-to-cart actions, checkout steps
- **Conversion Funnels**: User journey analysis

**Implementation Steps:**
```python
# Google Analytics API Integration
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

def fetch_ga_data():
    """Fetch real-time data from Google Analytics"""
    client = BetaAnalyticsDataClient()
    
    # Real-time user behavior
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[{"name": "dateHourMinute"}, {"name": "city"}],
        metrics=[{"name": "activeUsers"}, {"name": "screenPageViews"}],
        date_ranges=[{"start_date": "today", "end_date": "today"}]
    )
    
    return client.run_report(request)
```

#### 2. External Data Sources

**Weather Data Integration:**
```python
import requests

def get_weather_context(location, date):
    """Get weather data for demand prediction"""
    api_key = "YOUR_WEATHER_API_KEY"
    url = f"http://api.weatherapi.com/v1/historical.json"
    
    params = {
        'key': api_key,
        'q': location,
        'dt': date,
        'aqi': 'no'
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

**Social Media Trends:**
```python
def get_social_trends(product_category):
    """Get trending topics related to product categories"""
    # Twitter API, Google Trends, etc.
    pass
```

**Local Events & Holidays:**
```python
def get_local_events(location, date):
    """Get local events that might affect demand"""
    # Event APIs, calendar data
    pass
```

#### 3. Data Balancing Techniques

**For Product Popularity:**
```python
def balance_product_data(df):
    """Apply techniques to balance product popularity"""
    
    # 1. SMOTE for rare products
    from imblearn.over_sampling import SMOTE
    
    # 2. Product clustering for similar items
    from sklearn.cluster import KMeans
    
    # 3. Synthetic data generation for rare products
    # 4. Weighted sampling for training
    
    return balanced_df
```

**For Geographic Skewness:**
```python
def balance_geographic_data(df):
    """Balance data across different zones"""
    
    # 1. Zone-based sampling weights
    zone_weights = calculate_zone_weights(df)
    
    # 2. Synthetic zone data generation
    # 3. Cross-zone feature engineering
    
    return balanced_df
```

#### 4. Real-time Data Pipeline

**Streaming Data Integration:**
```python
import kafka
from kafka import KafkaConsumer, KafkaProducer

def setup_real_time_pipeline():
    """Set up real-time data ingestion"""
    
    # Kafka consumer for real-time orders
    consumer = KafkaConsumer(
        'orders_topic',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='latest'
    )
    
    # Google Analytics real-time API
    ga_client = BetaAnalyticsDataClient()
    
    # Weather API streaming
    weather_stream = setup_weather_stream()
    
    return consumer, ga_client, weather_stream
```

#### 5. Enhanced Feature Engineering

**Behavioral Features:**
```python
def engineer_behavioral_features(user_data, ga_data):
    """Create features from user behavior"""
    
    features = {
        'session_duration_avg': ga_data['avg_session_duration'],
        'pages_per_session': ga_data['pages_per_session'],
        'bounce_rate': ga_data['bounce_rate'],
        'cart_abandonment_rate': calculate_cart_abandonment(user_data),
        'device_preference': ga_data['device_category'],
        'traffic_source': ga_data['source_medium'],
        'time_on_site': ga_data['avg_time_on_page']
    }
    
    return features
```

**Contextual Features:**
```python
def engineer_contextual_features(location, date, weather_data, events_data):
    """Create contextual features"""
    
    features = {
        'temperature': weather_data['temp_c'],
        'precipitation': weather_data['precip_mm'],
        'humidity': weather_data['humidity'],
        'is_event_day': len(events_data) > 0,
        'event_type': events_data.get('type', 'none'),
        'day_of_week': date.weekday(),
        'is_holiday': check_holiday(date),
        'season': get_season(date)
    }
    
    return features
```

### Implementation Roadmap

#### Phase 1: Data Enrichment (Week 1-2)
1. Set up Google Analytics API integration
2. Implement weather data fetching
3. Create real-time data pipeline
4. Test data quality and consistency

#### Phase 2: Data Balancing (Week 3-4)
1. Implement SMOTE and other balancing techniques
2. Create synthetic data for rare products
3. Balance geographic and temporal distributions
4. Validate balanced datasets

#### Phase 3: Enhanced Modeling (Week 5-6)
1. Retrain models with enriched data
2. Implement real-time prediction pipeline
3. A/B test new vs. old models
4. Monitor performance improvements

#### Phase 4: Production Deployment (Week 7-8)
1. Deploy real-time prediction system
2. Set up monitoring and alerting
3. Create dashboards for data quality
4. Document new data pipeline

### Expected Benefits

1. **Reduced Data Skewness**: More balanced product and user distributions
2. **Better Predictions**: Real-time context improves accuracy
3. **Improved Personalization**: Behavioral data enables better recommendations
4. **Higher Accuracy**: External factors (weather, events) improve forecasting
5. **Real-time Adaptability**: Live data enables dynamic adjustments

### Success Metrics

- **Data Balance**: Gini coefficient < 0.3 for product popularity
- **Prediction Accuracy**: 15-20% improvement in MAPE
- **Coverage**: 95% of products with sufficient training data
- **Real-time Performance**: < 100ms prediction latency

### Technical Requirements

- Google Analytics 4 API access
- Weather API subscription
- Kafka/streaming infrastructure
- Additional storage for enriched data
- Real-time processing capabilities 