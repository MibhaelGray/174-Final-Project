# Forecasting ERCOT North Hub Electricity Prices: A SARIMAX Approach to Short-Term Price Prediction

## Overview
This project develops forecasting models for hourly electricity prices at ERCOT's North Hub using historical Real-Time Market (RTM) Settlement Point Prices. Employing the Box-Jenkins methodology, we construct SARIMA models to capture the complex seasonal patterns inherent in electricity pricing data. We extend our analysis by exploring the inclusion of weather as an exogenous variable to improve prediction accuracy. Our models aim to generate reliable price forecasts up to ten days ahead, providing valuable information for market participants in the volatile Texas electricity market.

## Datasets

### ERCOT North Hub Energy Prices
- **Time Range**: December 25, 2024 to February 22, 2025
- **Frequency**: 15-minute interval settlement prices resampled to hourly averages
- **Size**: Approximately 1,584 hourly data points (24 observations per day)
- **Units**: Dollars per megawatt-hour ($/MWh)
- **Source**: Electric Reliability Council of Texas (ERCOT) Market Information System

### Dallas, TX Weather Data
- **Time Range**: December 12, 2024 to February 15, 2025
- **Frequency**: Hourly measurements
- **Size**: Approximately 1,584 hourly observations
- **Units**: Temperature in degrees Fahrenheit (°F)
- **Source**: Weather Underground (wunderground.com) from Dallas/Fort Worth International Airport weather station

## Methodology

### Data Selection Rationale
- **Limited Timeframe (3 Months)**: Captures recent market dynamics and winter volatility while keeping computation manageable
- **Short-Term Forecast Horizon (10 Days)**: Aligns with reliability of weather predictions and operational decision timeframes in electricity markets

### Model Implementation
1. **SARIMA (p, d, q) × (P, D, Q) Model**
   - Captures both non-seasonal and seasonal components
   - Parameters identified through ACF/PACF analysis
   - Optimal model: SARIMA(1,1,1)(0,0,2)[24]

2. **SARIMAX with Exogenous Variables**
   - Extended model incorporating temperature data from Dallas as an exogenous variable
   - Captures the influence of weather conditions on electricity demand and prices

## Key Findings

1. **Model Performance**: The SARIMAX model achieved an R² of approximately 0.11 for 10-day forecasts with an MSE of 3357.88
2. **Seasonal Patterns**: The 24-hour seasonality was effectively captured by the model
3. **Temperature Effects**: Initial significant negative correlation (-0.23, p<0.001) between temperature and prices, though this relationship weakened in the final model
4. **Volatility Challenges**: The model struggled with price spikes and extreme values (residuals showed skewness of 24.22 and kurtosis of 760.04)
5. **Forecast Reliability**: Reasonable during normal market conditions but less accurate during price volatility events

## Limitations
- Dataset covers only winter months, missing broader seasonal patterns
- Standard time series models struggle with extreme price volatility
- Simple linear temperature relationship may oversimplify weather impacts
- Other crucial market factors not included (fuel costs, outages, grid constraints, renewable production)

## Future Research Directions
1. **Enhanced Volatility Modeling**: Specialized approaches for electricity market price swings
2. **Additional Variables**: Include natural gas prices, wind/solar generation, demand forecasts, reserve margins, transmission congestion
3. **Non-linear Temperature Effects**: More complex temperature relationships
4. **Regime-Switching Models**: Adaptive models for normal vs. crisis pricing modes
5. **Varying Forecast Horizons**: Test shorter forecasts (1-3 days) for reliability
6. **Extended Historical Data**: Multiple years to capture diverse market conditions
7. **Machine Learning Approaches**: For handling complexity and non-linearity
8. **Comparative Hub Analysis**: Extend to other ERCOT trading hubs

## Project Structure
```
/
├── Data/
│   ├── ERCOT SPPS/        # Settlement Point Price data
│   └── Weather/           # Temperature data for Dallas
├── Model/                 # Jupyter notebooks with analysis
├── README.md              # This file
```

## Contact
Michael Gray - Michaelgray@ucsb.edu