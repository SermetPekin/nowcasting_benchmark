# Variable-Specific Lags

Not all economic indicators are created equal. Some need more historical context than others.

## The Problem

Right now, every variable gets the same number of lags. If you set `n_lags=3`, then employment data gets 3 lags, GDP deflator gets 3 lags, interest rates get 3 lags—everything gets 3.

But this doesn't really make sense:
- Monthly employment data might need 6 lags to capture momentum
- Quarterly GDP components probably don't need as many
- Leading indicators behave differently than lagging ones

## The Solution

You can now specify different lag counts for different variables:

```python
config = NowcastConfig(
    target_variable="gdpc1",
    n_lags=3,  # default fallback
    variable_lags={
        'payems': 6,    # employment needs more history
        'indpro': 6,    # so does industrial production
        'gdpdef': 2,    # but quarterly deflator doesn't
    }
)
```

If a variable isn't in the `variable_lags` dict, it just uses the default `n_lags` value.

## Example

Say you have monthly employment (`payems`) and quarterly deflator (`gdpdef`).

**Old way** (uniform lags):
```
payems: payems, payems_1, payems_2, payems_3
gdpdef: gdpdef, gdpdef_1, gdpdef_2, gdpdef_3
```

**New way** (variable-specific):
```python
variable_lags={'payems': 6, 'gdpdef': 2}

# Results in:
payems: payems, payems_1, ..., payems_6  (6 lags)
gdpdef: gdpdef, gdpdef_1, gdpdef_2       (2 lags)
```

## Quick Start

Default behavior (nothing changes):
```python
config = NowcastConfig(n_lags=3)
```

Custom lags for specific variables:
```python
config = NowcastConfig(
    n_lags=3,
    variable_lags={
        'payems': 6,
        'indpro': 6,
        'unrate': 4
    }
)
```

That's it. The rest of the code stays the same.

## Full Example

```python
from nowcasting_framework import NowcastConfig, DataManager, ModelManager
from sklearn.linear_model import Ridge

config = NowcastConfig(
    target_variable="gdpc1",
    test_start_date="2005-03-01",
    test_end_date="2010-03-01",
    n_lags=3,
    variable_lags={
        'payems': 6,
        'indpro': 6,
        'unrate': 4,
        'gdpdef': 2
    }
)

data_manager = DataManager(config)
data_manager.load_data().prepare_test_data()

model = ModelManager(Ridge, {'alpha': 0.1}, config)
model.run_backtest(data_manager)
```

## Notes

- Completely optional—old code still works
- Backward compatible with everything
- Works in training, backtesting, and inference
- No performance overhead if you don't use it
