import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

# --- Helper functions ---
def moving_average_forecast(train, test, zone_col, time_col, demand_col, window=3):
    preds = []
    for zone in test[zone_col].unique():
        train_zone = train[train[zone_col] == zone].sort_values(time_col)
        test_zone = test[test[zone_col] == zone].sort_values(time_col)
        history = list(train_zone[demand_col].values)
        for t in range(len(test_zone)):
            if len(history) >= window:
                pred = np.mean(history[-window:])
            else:
                pred = np.mean(history)
            preds.append(pred)
            history.append(test_zone.iloc[t][demand_col])
    return np.array(preds)

def naive_forecast(train, test, zone_col, time_col, demand_col):
    preds = []
    for zone in test[zone_col].unique():
        train_zone = train[train[zone_col] == zone].sort_values(time_col)
        test_zone = test[test[zone_col] == zone].sort_values(time_col)
        last_value = train_zone[demand_col].values[-1]
        preds.extend([last_value] * len(test_zone))
    return np.array(preds)

def evaluate_forecast(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    return mae, rmse

# --- Hourly data ---
hour_train = pd.read_csv('zone_hour_train.csv')
hour_test = pd.read_csv('zone_hour_test.csv')

results_hour = []
for zone in hour_test['zone'].unique():
    test_zone = hour_test[hour_test['zone'] == zone].sort_values('hour')
    train_zone = hour_train[hour_train['zone'] == zone].sort_values('hour')
    y_true = test_zone['demand'].values
    # Moving average
    y_pred_ma = moving_average_forecast(train_zone, test_zone, 'zone', 'hour', 'demand', window=3)
    mae_ma, rmse_ma = evaluate_forecast(y_true, y_pred_ma)
    # Naive
    y_pred_naive = naive_forecast(train_zone, test_zone, 'zone', 'hour', 'demand')
    mae_naive, rmse_naive = evaluate_forecast(y_true, y_pred_naive)
    results_hour.append({'zone': zone, 'model': 'moving_average', 'MAE': mae_ma, 'RMSE': rmse_ma})
    results_hour.append({'zone': zone, 'model': 'naive', 'MAE': mae_naive, 'RMSE': rmse_naive})

pd.DataFrame(results_hour).to_csv('baseline_hourly_results.csv', index=False)

# --- Daily data ---
dow_train = pd.read_csv('zone_dow_train.csv')
dow_test = pd.read_csv('zone_dow_test.csv')

results_dow = []
for zone in dow_test['zone'].unique():
    test_zone = dow_test[dow_test['zone'] == zone].sort_values('dow')
    train_zone = dow_train[dow_train['zone'] == zone].sort_values('dow')
    y_true = test_zone['demand'].values
    # Moving average
    y_pred_ma = moving_average_forecast(train_zone, test_zone, 'zone', 'dow', 'demand', window=2)
    mae_ma, rmse_ma = evaluate_forecast(y_true, y_pred_ma)
    # Naive
    y_pred_naive = naive_forecast(train_zone, test_zone, 'zone', 'dow', 'demand')
    mae_naive, rmse_naive = evaluate_forecast(y_true, y_pred_naive)
    results_dow.append({'zone': zone, 'model': 'moving_average', 'MAE': mae_ma, 'RMSE': rmse_ma})
    results_dow.append({'zone': zone, 'model': 'naive', 'MAE': mae_naive, 'RMSE': rmse_naive})

pd.DataFrame(results_dow).to_csv('baseline_dow_results.csv', index=False)

print('Baseline model evaluation complete. Outputs:')
print(' - baseline_hourly_results.csv')
print(' - baseline_dow_results.csv') 