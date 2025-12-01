# library imports
import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso

# just for jupyter notebooks plot size
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [15, 10]


# ============================================================================
# DATA LOADING AND SETUP
# ============================================================================

def load_data(data_path="../data/data_tf.csv", metadata_path="../data/meta_data.csv"):
    """Load main data and metadata CSVs."""
    data = pd.read_csv(data_path, parse_dates=["date"])
    metadata = pd.read_csv(metadata_path)
    return data, metadata


def setup_test_data(data, target_variable="gdpc1", 
                    lags=None,
                    train_start_date="1947-01-01",
                    test_start_date="2005-03-01", 
                    test_end_date="2010-03-01"):
    """
    Setup standard test dataset configuration.
    
    Returns:
        dict: Configuration dictionary with all parameters and test dataset
    """
    if lags is None:
        lags = list(range(-2, 3))
    
    config = {
        'target_variable': target_variable,
        'lags': lags,
        'train_start_date': train_start_date,
        'test_start_date': test_start_date,
        'test_end_date': test_end_date
    }
    
    test = data.loc[(data.date >= train_start_date) & (data.date <= test_end_date), :].reset_index(drop=True)
    config['test'] = test
    
    return config


def get_test_dates_and_actuals(test, test_start_date, test_end_date, target_variable):
    """
    Extract test dates and actual values for the target variable.
    
    Returns:
        tuple: (dates, actuals) - list of test dates and corresponding actual values
    """
    dates = (
        pd.date_range(test_start_date, test_end_date, freq="3MS")
        .strftime("%Y-%m-%d")
        .tolist()
    )
    actuals = list(test.loc[test.date.isin(dates), target_variable].values)
    return dates, actuals


# helper function, generate lagged datasets for testing on vintages
def gen_lagged_data(metadata, data, last_date, lag):
    # only go up to the last date
    lagged_data = data.loc[data.date <= last_date, :].reset_index(drop=True)
    for col in lagged_data.columns[1:]:
        pub_lag = metadata.loc[metadata.series == col, "months_lag"].values[0] # publication lag of this particular variable
        # go back as far as needed for the pub_lag of the variable, then + the lag (so -2 for 2 months back), also -1 because 0 lag means in month, last month data available, not current month in
        lagged_data.loc[(len(lagged_data) - pub_lag + lag - 1) :, col] = np.nan

    return lagged_data

# helper function, flatten a dataset for methods that don't do timeseries, extra columns for each lag
def flatten_data(data, target_variable, n_lags):
    flattened_data = data.loc[~pd.isna(data[target_variable]), :]
    orig_index = flattened_data.index
    for i in range(1, n_lags + 1):
        lagged_indices = orig_index - i
        lagged_indices = lagged_indices[lagged_indices >= 0]
        tmp = data.loc[lagged_indices, :]
        tmp.date = tmp.date + pd.DateOffset(months=i)
        tmp = tmp.drop([target_variable], axis=1)
        tmp.columns = [j + "_" + str(i) if j != "date" else j for j in tmp.columns]
        flattened_data = flattened_data.merge(tmp, how="left", on="date")

    return flattened_data

# helper function fill missings in a dataset with the mean from the training set
def mean_fill_dataset(training, test):
    mean_dict = {}
    for col in training.columns[1:]:
        mean_dict[col] = np.nanmean(training[col])
    filled = test.copy()
    for col in training.columns[1:]:
        filled.loc[pd.isna(filled[col]), col] = mean_dict[col]
    return filled


# ============================================================================
# MODEL EVALUATION AND VISUALIZATION
# ============================================================================

def calculate_performance_metrics(actuals, pred_dict, lags):
    """
    Calculate RMSE for each lag/vintage.
    
    Args:
        actuals: List of actual values
        pred_dict: Dictionary mapping lags to predictions
        lags: List of lags to evaluate
        
    Returns:
        pd.DataFrame: Performance metrics by vintage
    """
    performance = pd.DataFrame(columns=["Vintage", "RMSE"])
    for lag in lags:
        tmp = pd.DataFrame({
            "Vintage": lag,
            "RMSE": np.sqrt(np.mean((np.array(actuals) - np.array(pred_dict[lag])) ** 2))
        }, index=[0])
        performance = pd.concat([performance, tmp]).reset_index(drop=True)
    return performance


def plot_predictions(actuals, pred_dict, lags=None):
    """
    Plot predictions vs actuals for different vintages.
    
    Args:
        actuals: List of actual values
        pred_dict: Dictionary mapping lags to predictions
        lags: List of lags to plot (default: [-2, -1, 0, 1, 2])
    """
    if lags is None:
        lags = [-2, -1, 0, 1, 2]
    
    plot_data = {"actuals": actuals}
    lag_names = {
        -2: "two_back",
        -1: "one_back",
        0: "zero_back",
        1: "one_ahead",
        2: "two_ahead"
    }
    
    for lag in lags:
        if lag in pred_dict:
            name = lag_names.get(lag, f"lag_{lag}")
            plot_data[name] = pred_dict[lag]
    
    pd.DataFrame(plot_data).plot()
    plt.ylabel('GDP Growth Rate')
    plt.xlabel('Time Period')
    plt.title('Predictions vs Actuals by Vintage')
    plt.legend()
    return plt.gcf()


# ============================================================================
# DATA PREPARATION FOR FLAT MODELS
# ============================================================================

def prepare_flat_data(data, target_variable, n_lags=4, quarterly_only=True):
    """
    Prepare data for models that don't handle time series natively.
    
    Args:
        data: Input dataframe
        target_variable: Name of target variable
        n_lags: Number of lags to include
        quarterly_only: If True, keep only quarterly observations
        
    Returns:
        pd.DataFrame: Transformed data with lagged features
    """
    transformed = mean_fill_dataset(data, data)
    transformed = flatten_data(transformed, target_variable, n_lags)
    
    if quarterly_only:
        transformed = transformed.loc[
            transformed.date.dt.month.isin([3, 6, 9, 12]), :
        ].dropna(axis=0, how="any").reset_index(drop=True)
    
    return transformed


def add_future_dates(data, desired_date):
    """
    Add future dates to dataframe if they don't exist yet.
    
    Args:
        data: Input dataframe with 'date' column
        desired_date: Target date to ensure exists in data
        
    Returns:
        pd.DataFrame: Data with future dates added
    """
    new_data = data.copy()
    desired_date = pd.to_datetime(desired_date)
    
    while desired_date > np.max(new_data.date):
        new_data.loc[len(new_data), "date"] = np.max(new_data.date) + pd.DateOffset(months=1)
    
    return new_data