import numpy as np 
import pandas as pd
import pmdarima as pm
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_absolute_error

cleaned_lmp = pd.read_csv('Data\Cleaned_Merged\cleaned_LMP_data_with_datetime.csv', parse_dates=[
        'UTC Timestamp (Interval Ending)',
        'Local Timestamp Central Time (Interval Beginning)',
        'Local Timestamp Central Time (Interval Ending)',
        'Local Date'
    ])

daily_data = cleaned_lmp.groupby(cleaned_lmp['Local Date'].dt.to_period('D'))['North LMP'].mean().reset_index()
daily_data['Local Date'] = daily_data['Local Date'].dt.to_timestamp()
daily_data.set_index('Local Date', inplace=True)
daily_data.to_csv('daily_LMP.csv')

weekly_data = cleaned_lmp.groupby(cleaned_lmp['Local Date'].dt.to_period('W'))['North LMP'].mean().reset_index()
weekly_data['Local Date'] = weekly_data['Local Date'].dt.to_timestamp()
weekly_data.set_index('Local Date', inplace=True)
weekly_data.to_csv('weekly_LMP.csv')

monthly_data = cleaned_lmp.groupby(cleaned_lmp['Local Date'].dt.to_period('M'))['North LMP'].mean().reset_index()
monthly_data['Local Date'] = monthly_data['Local Date'].dt.to_timestamp()
monthly_data.set_index('Local Date', inplace=True)
monthly_data.to_csv('monthly_LMP.csv')

# Check stationary
def check_stationarity(time_series):
    result = adfuller(time_series, autolag='AIC')
    p_value = result[1]
    print(f'ADF Statistic: {result[0]}')
    print(f'p-value: {p_value}')
    print('Stationary' if p_value < 0.05 else 'Non-Stationary')

time_series_data = [daily_data, weekly_data, monthly_data]

def get_frequency(data):
    # Check if the index is a DatetimeIndex
    if isinstance(data.index, pd.DatetimeIndex):
        # Infer frequency from the index
        freq = pd.infer_freq(data.index)
        if freq:
            if freq.startswith('H'):
                return 'Hourly'
            elif freq.startswith('D'):
                return 'Daily'
            elif freq.startswith('W'):
                return 'Weekly'
            elif freq.startswith('M'):
                return 'Monthly'
        
print(get_frequency(daily_data)) 
print(get_frequency(weekly_data))  
print(get_frequency(monthly_data))  

def time_series_plot(time_series):
    freq = get_frequency(time_series)
    label = f'{freq} North LMP'
    title = f'{freq} North LMP Prices'

    plt.figure(figsize=(10, 6))
    plt.plot(time_series['North LMP'], label=label)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price ($/MWh)')
    plt.legend()
    plt.show()

time_series_plot(daily_data)
time_series_plot(weekly_data)  
time_series_plot(monthly_data)  

def model_analysis(time_series):
    check_stationarity(time_series)
    plot_acf(time_series)
    plot_pacf(time_series)
    plt.show()

model_analysis(daily_data)



model = pm.auto_arima(
    daily_data,
    start_p=1,           # Minimum AR order
    start_q=1,           # Minimum MA order
    max_p=5,            # Maximum AR order
    max_q=5,            # Maximum MA order
    d=0,                # Differencing order (set to 0 for pure ARMA)
    seasonal=False,      # Set to True if you want SARIMA (seasonal ARIMA)
    stepwise=True,       # Use stepwise search to speed up
    trace=True,          # Print progress
    error_action='ignore',  # Ignore invalid models
    suppress_warnings=True,
    information_criterion='aic'  # Use AIC to select the best model
)

# Print the summary of the best model
print(model.summary())

# Get the best parameters
best_order = model.order  # Returns (p, d, q)
print(f"Best ARMA parameters: p={best_order[0]}, q={best_order[2]}")




# Number of steps to forecast (e.g., 30 days)
n_periods = 30

# Generate forecasts and confidence intervals
forecast, conf_int = model.predict(n_periods=n_periods, return_conf_int=True)

# Create future dates for the forecast
last_date = daily_data.index[-1]
future_dates = pd.date_range(start=last_date, periods=n_periods + 1, freq='D')[1:]

# Convert forecast to a pandas Series with the future dates as index
forecast_series = pd.Series(forecast, index=future_dates)
conf_int_df = pd.DataFrame(conf_int, index=future_dates, columns=['Lower CI', 'Upper CI'])

# Plot the original data and forecast
plt.figure(figsize=(12, 6))
plt.plot(daily_data['North LMP'], label='Historical North LMP')
plt.plot(forecast_series, label='Forecast', color='red')
plt.fill_between(conf_int_df.index, conf_int_df['Lower CI'], conf_int_df['Upper CI'], 
                 color='pink', alpha=0.3, label='95% Confidence Interval')
plt.title('Daily North LMP Forecast')
plt.xlabel('Date')
plt.ylabel('Price ($/MWh)')
plt.legend()
plt.show()

# Print forecast values
print("Forecasted Values:")
print(forecast_series)