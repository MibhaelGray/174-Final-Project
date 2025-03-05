import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.graphics.gofplots import qqplot  # Added for Q-Q plot
from scipy.stats import shapiro  # Added for Shapiro-Wilk test

HB_NORTH_DATA = pd.read_csv("174-Final-Project/Data/ERCOT SPPS/All_HB_NORTH_Data.csv")
HB_NORTH_DATA['Datetime'] = pd.to_datetime(HB_NORTH_DATA['Delivery Date']) + pd.to_timedelta(HB_NORTH_DATA['Delivery Hour'] - 1, unit='h')
HB_NORTH_DATA.set_index('Datetime', inplace=True)

### Resample to daily frequency (using mean of each day)
daily_data = HB_NORTH_DATA['Settlement Point Price'].resample('D').mean()

### Run ADF test on original series
print("\n=== ADF Test for Original Series ===")
result = adfuller(daily_data.dropna())
print(f'p-value: {result[1]},\n Because the p-value is less than 0.05 we know our data is stationary')

### Plot ACF and PACF
ACF_Plot = plot_acf(daily_data, lags=40)
plt.show()
PACF_Plot = plot_pacf(daily_data, lags=40)
print(PACF_Plot)  # Note: This prints the figure object; remove this line if not needed
plt.show()

'''
Based on the ACF and PACF plots, the time series exhibits characteristics of an autoregressive process
 with significant autocorrelation at short lags but no clear seasonal patterns. The stationary nature of
  the data (confirmed by the ADF test with p-value < 0.05) suggests no differencing is needed, while the
   PACF showing significant spikes at lags 1 and 2 indicates an AR(1) or AR(2) model would be appropriate.
    The gradually decaying ACF pattern with no significant spikes in higher lags suggests minimal or no moving 
    average components are needed, pointing toward a SARIMA model with parameters around (1-2,0,0-1)(0,0,0)7. 
    Multiple candidate models should be tested and compared using information criteria and forecast
     accuracy metrics to determine the optimal specification for the electricity price data. The evidence 
     most strongly supports a simple AR process rather than a complex seasonal model, though weak weekly 
     seasonality could be explored if domain knowledge suggests it might exist.
'''

# Candidate models
candidate_models = [
    ((1, 0, 0), (0, 0, 0, 7)),  # AR(1)
    ((2, 0, 0), (0, 0, 0, 7)),  # AR(2)
    ((1, 0, 1), (0, 0, 0, 7)),  # ARMA(1,1)
    ((1, 0, 0), (1, 0, 0, 7)),  # AR(1) + Seasonal AR(1)
    ((1, 0, 1), (0, 0, 1, 7)),  # ARMA(1,1) + Seasonal MA(1)
    ((1, 0, 2), (0, 0, 1, 7)),  # ARIMA (1,0,2) + Seasonal MA(1)
    ((1, 0, 3), (0, 0, 1, 7))   # ARIMA (1,0,3) + Seasonal MA(1)
]

best_model_aic = float('inf')
best_model_bic = float('inf')
best_aic_model = None
best_bic_model = None

for order, seasonal_order in candidate_models:
    model = SARIMAX(daily_data, order=order, seasonal_order=seasonal_order)
    results = model.fit()
    
    print(f"Model: {order}, Seasonal: {seasonal_order}")
    print(f"AIC: {results.aic}, BIC: {results.bic}")
    
    # Track best AIC model
    if results.aic < best_model_aic:
        best_model_aic = results.aic
        best_aic_model = (order, seasonal_order)
    
    # Track best BIC model
    if results.bic < best_model_bic:
        best_model_bic = results.bic
        best_bic_model = (order, seasonal_order)

print(f"Best Model based on AIC: {best_aic_model}, AIC: {best_model_aic}")
print(f"Best Model based on BIC: {best_bic_model}, BIC: {best_model_bic}")

# Fit the best model based on AIC
best_order, best_seasonal_order = best_aic_model
best_model = SARIMAX(daily_data, order=best_order, seasonal_order=best_seasonal_order)
best_results = best_model.fit()

# Residual diagnostics for the best model
residuals = best_results.resid

plt.figure(figsize=(10,6))
plt.plot(residuals)
plt.title('Residuals of the Best SARIMAX Model')
plt.show()

'''Residuals of the SARIMA Model: The plot of residuals over time shows a stationary pattern with no 
clear trends or seasonality, which is kind of what I expected
However, noticeable spikes, particularly around 2021, suggest the model might not fully 
capture extreme market events, possibly due to external shocks like weather or policy changes impacting electricity
 prices. These spikes highlight a limitation in the model's ability to handle outliers, suggesting a need for 
 further investigation or model enhancement to improve robustness.'''


plt.figure(figsize=(10,6))
plt.hist(residuals, bins=30)
plt.title('Histogram of Residuals')
plt.show()


'''Histogram of Residuals: I made this Histogram of Residuals to check how well my SARIMAX model is 
doing with the ERCOT HB_NORTH electricity price data, and it looks like most of the residuals are super 
close to zero, which I think is a good sign that my model is catching the main patterns. There are a few 
outliers though, which makes me wonder if there were some crazy price jumps my model couldn’t handle—like 
maybe some unexpected market stuff happened. I might need to tweak my model or add something to deal with 
those rare big swings better.'''

plot_acf(residuals, lags=40)
plt.title('ACF Plot of Residuals')
plt.show()

'''
The ACF Plot of Residuals shows no significant autocorrelation beyond lag 0, 
with nearly all values falling within the confidence bounds, indicating that the residuals resemble white noise.
'''

# Q-Q plot for residuals
qqplot(residuals, line='s')
plt.title('Q-Q Plot of Residuals')
plt.show()

'''The Q-Q Plot of Residuals shows that the residuals generally align with the theoretical normal distribution
 along the diagonal, particularly in the central range, suggesting that the models residuals are approximately
normally distributed for typical values. However, deviations at the tails, especially at the extremes, indicate
non-normality in the residuals, consistent with potential heavy-tailed behavior in the data. This suggests
that while the model fits well for the bulk of the data, it may not fully account for extreme 
price movements, potentially necessitating a model that better handles such distributions.'''

# Shapiro-Wilk test for normality
stat, p = shapiro(residuals)
print(f'Shapiro-Wilk Test: Statistic={stat}, p-value={p}')





n_forecast = 12
forecast_values = best_results.forecast(steps=n_forecast)
print(forecast_values)
plt.figure(figsize=(12, 6))
historical_period = 30
historical_data = daily_data[-historical_period:]

plt.plot(historical_data.index, historical_data, label='Historical Data', color='blue')

forecast_dates = pd.date_range(start=historical_data.index[-1], 
                             periods=n_forecast + 1, 
                             freq='D')[1:] 

# Plot forecast
plt.plot(forecast_dates, forecast_values, label='Forecast', color='red', linestyle='--')
plt.title('Historical Data and Price Forecast')
plt.xlabel('Date')
plt.ylabel('Settlement Point Price')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()



