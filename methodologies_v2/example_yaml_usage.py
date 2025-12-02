"""
Example: Using YAML Configurations

This shows how to use YAML config files instead of inline configuration.
"""

# Method 1: Inline (current approach)
from methodologies_v2.nowkit.nowcasting_framework import NowcastConfig, DataManager, ModelManager
from sklearn.linear_model import Ridge

config = NowcastConfig(
    target_variable="gdpc1",
    test_start_date="2005-03-01",
    test_end_date="2010-03-01",
    n_lags=3
)

# Method 2: Load from YAML
config = NowcastConfig.from_yaml("configs/ols_baseline.yaml")

# Rest of the code stays the same
data_manager = DataManager(config)
data_manager.load_data().prepare_test_data()

model = ModelManager(Ridge, {'alpha': 0.1}, config)
model.run_backtest(data_manager)

# Save your tuned config for later
# config.to_yaml("configs/my_best_config.yaml")

print("RMSE:", model.get_predictions())
