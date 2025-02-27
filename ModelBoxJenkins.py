import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_absolute_error
import warnings


monthly_data = pd.read_csv("Data/Time-Scaled Data/monthly_LMP.csv", parse_dates=['Local Date'])
monthly_data.set_index('Local Date')
time_series = monthly_data['North LMP']
adf_result = adfuller(time_series)

# Plotting the time series data

plt.figure(figsize=(12,5))
plt.plot(monthly_data.index, monthly_data['North LMP'], marker='o', linestyle='-')
plt.xlabel("Time (Months)")
plt.ylabel("Dollars per megawatt-hour ($/MWh).")
plt.title("Dallas-Fort Worth Wholesale Energy Prices")
plt.grid()
plt.show()


# Print results
print("ADF Statistic:", adf_result[0])
print("p-value:", adf_result[1])
print("Critical Values:")

if adf_result[1] < 0.05:
    print("The series is stationary (reject null hypothesis).")
else:
    print("The series is non-stationary")

# Now let's create some ACF and PACF plots to determine if the data 

# Plot ACF
plt.figure(figsize=(12, 5))
plot_acf(time_series.dropna(), lags=60)
plt.title("Autocorrelation Function (ACF)")
plt.ylabel('Correlation (-1,1)')
plt.show()

# Plot PACF
plt.figure(figsize=(12, 5))
plot_pacf(time_series.dropna(), lags=30)
plt.title("Partial Autocorrelation Function (PACF)")
plt.ylabel('Correlation (-1,1)')
plt.show()
