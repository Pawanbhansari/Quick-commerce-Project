import pandas as pd
import numpy as np

def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

# --- Hourly ---
hour_test = pd.read_csv('zone_hour_test.csv')
hour_results = pd.read_csv('baseline_hourly_results.csv')

print('Hourly MAPE by zone:')
for zone in hour_test['zone'].unique():
    test_zone = hour_test[hour_test['zone'] == zone].sort_values('hour')
    y_true = test_zone['demand'].values
    # Moving average
    mae_row = hour_results[(hour_results['zone'] == zone) & (hour_results['model'] == 'moving_average')]
    naive_row = hour_results[(hour_results['zone'] == zone) & (hour_results['model'] == 'naive')]
    # Recompute predictions for MAPE
    # (Recompute to ensure alignment, as baseline script does not save predictions)
    # Moving average
    train_zone = pd.read_csv('zone_hour_train.csv')
    train_zone = train_zone[train_zone['zone'] == zone].sort_values('hour')
    history = list(train_zone['demand'].values)
    preds_ma = []
    for t in range(len(test_zone)):
        if len(history) >= 3:
            pred = np.mean(history[-3:])
        else:
            pred = np.mean(history)
        preds_ma.append(pred)
        history.append(y_true[t])
    # Naive
    last_value = train_zone['demand'].values[-1]
    preds_naive = [last_value] * len(test_zone)
    mape_ma = mape(y_true, preds_ma)
    mape_naive = mape(y_true, preds_naive)
    print(f'Zone {zone}: Moving Average MAPE = {mape_ma:.2f}%, Naive MAPE = {mape_naive:.2f}%')

# --- Daily ---
dow_test = pd.read_csv('zone_dow_test.csv')
dow_results = pd.read_csv('baseline_dow_results.csv')

print('\nDay-of-Week MAPE by zone:')
for zone in dow_test['zone'].unique():
    test_zone = dow_test[dow_test['zone'] == zone].sort_values('dow')
    y_true = test_zone['demand'].values
    # Moving average
    train_zone = pd.read_csv('zone_dow_train.csv')
    train_zone = train_zone[train_zone['zone'] == zone].sort_values('dow')
    history = list(train_zone['demand'].values)
    preds_ma = []
    for t in range(len(test_zone)):
        if len(history) >= 2:
            pred = np.mean(history[-2:])
        else:
            pred = np.mean(history)
        preds_ma.append(pred)
        history.append(y_true[t])
    # Naive
    last_value = train_zone['demand'].values[-1]
    preds_naive = [last_value] * len(test_zone)
    mape_ma = mape(y_true, preds_ma)
    mape_naive = mape(y_true, preds_naive)
    print(f'Zone {zone}: Moving Average MAPE = {mape_ma:.2f}%, Naive MAPE = {mape_naive:.2f}%') 