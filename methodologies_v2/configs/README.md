# Using YAML Configurations

You can now load configurations from YAML files instead of defining them inline.

## Quick Start

**Load from YAML:**
```python
from nowcasting_framework import NowcastConfig

config = NowcastConfig.from_yaml("configs/ols_baseline.yaml")
```

**Save to YAML:**
```python
config = NowcastConfig(n_lags=3, target_variable="gdpc1")
config.to_yaml("configs/my_experiment.yaml")
```

## When to Use YAML

Use inline configs (current approach):
- Exploring in notebooks
- Quick experiments
- One-off tests

Use YAML configs:
- Running batch experiments
- Reproducing exact results
- Sharing configurations with others
- Version controlling experiment parameters

## Example Workflow

```python
# 1. Start with inline config
config = NowcastConfig(
    n_lags=3,
    variable_lags={'payems': 6, 'indpro': 6}
)

# 2. Run experiment
data_manager = DataManager(config)
model = ModelManager(Ridge, {'alpha': 0.1}, config)
# ... train and evaluate ...

# 3. Save if results are good
config.to_yaml("configs/ridge_tuned_v1.yaml")

# 4. Later: reproduce exact results
config = NowcastConfig.from_yaml("configs/ridge_tuned_v1.yaml")
```

## Available Configs

Check `configs/` directory for examples:
- `ols_baseline.yaml` - Simple OLS with uniform lags
- `ols_variable_lags.yaml` - OLS with different lags per variable
- `ridge_baseline.yaml` - Ridge regression baseline
- `ols_randomized.yaml` - Control experiment with random data

## Installation

YAML support requires PyYAML:
```bash
pip install pyyaml
```

or with uv:
```bash
uv pip install pyyaml
```
