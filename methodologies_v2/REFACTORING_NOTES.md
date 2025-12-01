# Refactoring Notes - methodologies_v2

**Author:** Sermet Pekin  
**Date:** November 2025  
**Purpose:** Documentation of refactoring work to reduce code duplication across methodology notebooks

## Overview

The `methodologies_v2/` folder contains refactored versions of the original methodology notebooks. The goal is to reduce code repetition by extracting common patterns into reusable functions in `common.py`.

## Refactoring Strategy

### Common Patterns Identified

1. **Data Loading and Setup**
   - Loading data and metadata CSVs
   - Setting up test configurations
   - Extracting test dates and actual values

2. **Data Preparation**
   - Generating lagged datasets for vintage testing
   - Flattening data for non-time-series models
   - Mean-filling missing values

3. **Model Evaluation**
   - Calculating RMSE by vintage
   - Plotting predictions vs actuals

4. **Data Transformation**
   - Adding future dates to dataframes
   - Preparing quarterly-only datasets

## Functions in common.py

### Data Loading and Setup
- `load_data()` - Load main data and metadata CSVs
- `setup_test_data()` - Create standard test configuration dictionary
- `get_test_dates_and_actuals()` - Extract test dates and actual values

### Data Transformation (from original)
- `gen_lagged_data()` - Generate lagged datasets for vintage testing
- `flatten_data()` - Flatten dataset with lag columns for non-time-series models
- `mean_fill_dataset()` - Fill missing values with training set mean

### Model Evaluation and Visualization
- `calculate_performance_metrics()` - Calculate RMSE for each lag/vintage
- `plot_predictions()` - Plot predictions vs actuals by vintage

### Data Preparation
- `prepare_flat_data()` - Prepare data for models that don't handle time series natively
- `add_future_dates()` - Add future dates to dataframe if needed

## Example: py_lasso.ipynb Refactoring

### Before (Original)
```python
# Cell 3: Manual data loading and setup
data = pd.read_csv("../data/data_tf.csv", parse_dates=["date"])
metadata = pd.read_csv("../data/meta_data.csv")
target_variable = "gdpc1"
lags = list(range(-2, 3))
train_start_date = "1947-01-01"
test_start_date = "2005-03-01"
test_end_date = "2010-03-01"
test = data.loc[(data.date >= train_start_date) & (data.date <= test_end_date), :].reset_index(drop=True)

# Cell 9: Manual date extraction
dates = pd.date_range(test_start_date, test_end_date, freq="3MS").strftime("%Y-%m-%d").tolist()
actuals = list(test.loc[test.date.isin(dates), target_variable].values)

# Cell 12: Manual RMSE calculation
performance = pd.DataFrame(columns=["Vintage", "RMSE"])
for lag in lags:
    tmp = pd.DataFrame({
        "Vintage":lag,
        "RMSE":np.sqrt(np.mean((np.array(actuals) - np.array(pred_dict[lag])) ** 2))
    }, index=[0])
    performance = pd.concat([performance, tmp]).reset_index(drop=True)
performance.round(4)

# Cell 13: Manual plotting
pd.DataFrame({
    "actuals":actuals, 
    "two_back":pred_dict[-2], 
    "one_back":pred_dict[-1], 
    "zero_back":pred_dict[0],
    "one_ahead":pred_dict[1],
    "two_ahead":pred_dict[2]}
).plot()
```

### After (Refactored)
```python
# Cell 1: Auto-reload for development
%load_ext autoreload
%autoreload 2
from common import *

# Cell 3: Using common utilities
data, metadata = load_data()
test_config = setup_test_data(
    data=data,
    target_variable="gdpc1",
    lags=list(range(-2, 3)),
    train_start_date="1947-01-01",
    test_start_date="2005-03-01",
    test_end_date="2010-03-01"
)
target_variable = test_config["target_variable"]
lags = test_config["lags"]
test = test_config["test"]

# Cell 9: Using common utility
dates, actuals = get_test_dates_and_actuals(
    test, 
    test_config["test_start_date"], 
    test_config["test_end_date"], 
    target_variable
)

# Cell 12: Using common utility
performance = calculate_performance_metrics(actuals, pred_dict, lags)
performance.round(4)

# Cell 13: Using common utility
plot_predictions(actuals, pred_dict)
```

## Benefits

1. **Reduced Code Duplication**: Common patterns extracted into reusable functions
2. **Easier Maintenance**: Changes to common logic only need to be made in one place
3. **Consistency**: All notebooks use the same implementation for common operations
4. **Better Testing**: Common functions can be tested independently
5. **Cleaner Notebooks**: Less boilerplate code, easier to focus on model-specific logic

## Testing

All refactored notebooks have been tested to ensure they produce the same results as the original versions:
- ✅ `py_lasso.ipynb` - Tested and working (RMSE matches original)

## Next Steps

1. Refactor additional notebooks from `methodologies/` folder
2. Apply same pattern to other Python notebooks
3. Consider extracting model-specific utilities if patterns emerge
4. Update documentation with usage examples

## Development Tips

- The first cell includes `%autoreload 2` to automatically reload `common.py` during development
- When adding new functions to `common.py`, follow the existing organization:
  - Data Loading and Setup
  - Data Transformation
  - Model Evaluation and Visualization
  - Data Preparation
- Add clear docstrings to all new functions
- Use descriptive parameter names
- Return values that match existing patterns in notebooks
