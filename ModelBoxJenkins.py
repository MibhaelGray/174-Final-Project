import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_absolute_error
import warnings


HB_NORTH_DATA = pd.read_csv("Final Project/Data/ERCOT SPPS/All_HB_NORTH_Data.csv")





# Convert Delivery Date and Hour into a proper datetime format
HB_NORTH_DATA['Datetime'] = pd.to_datetime(HB_NORTH_DATA['Delivery Date']) + pd.to_timedelta(HB_NORTH_DATA['Delivery Hour'] - 1, unit='h')

# Set Datetime as the index
HB_NORTH_DATA.set_index('Datetime', inplace=True)

# Plot the Settlement Point Price over time
plt.figure(figsize=(12, 6))
plt.plot(HB_NORTH_DATA.index, HB_NORTH_DATA['Settlement Point Price'], label='Settlement Point Price', color='b', alpha=0.7)
plt.xlabel('Time')
plt.ylabel('Price ($)')
plt.title('ERCOT HB NORTH Settlement Point Price Over Time')
plt.legend()
plt.grid(True)
plt.show()