import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Read the data
# Assuming columns are Date, Time, Temperature_F
data = pd.read_csv('Data\Weather\dallas_temps_20250216_to_20250222_complete.csv')

# Convert to datetime
data['datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], 
                                 format='%Y-%m-%d %I:%M %p')
data = data.sort_values('datetime')  # Ensure data is sorted

# Generate hourly timestamps for the entire period
start_time = data['datetime'].min().replace(minute=0, second=0)
end_time = data['datetime'].max().replace(minute=0, second=0) + timedelta(hours=1)
hourly_timestamps = pd.date_range(start=start_time, end=end_time, freq='H')

# Create a new dataframe for results
result = pd.DataFrame(hourly_timestamps, columns=['datetime'])

# Perform linear interpolation
# Set index to datetime for easy interpolation
data = data.set_index('datetime')
# Create a Series with original temperatures
temps = data['Temperature_F']

# Interpolate to hourly timestamps
interpolated_temps = np.interp(
    x=hourly_timestamps.astype(np.int64) / 10**9,  # Convert to seconds
    xp=temps.index.astype(np.int64) / 10**9,       # Convert to seconds
    fp=temps.values
)

# Add interpolated temperatures to result dataframe
result['Temperature_F'] = np.round(interpolated_temps).astype(int)

# Format the output
result['Date'] = result['datetime'].dt.strftime('%Y-%m-%d')
result['Time'] = result['datetime'].dt.strftime('%I:00 %p')
result = result[['Date', 'Time', 'Temperature_F']]  # Select and order columns

# Save the result
result.to_csv('interpolated_temps.csv', index=False)

# Print sample
print(result.head(10))