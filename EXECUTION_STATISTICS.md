# Notebook Execution Statistics

**Last Updated:** November 29, 2025  
**Platform:** Apple Silicon (M-series) Mac  
**Python:** 3.11.13 (.venv with uv)  
**R:** 4.4.2

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Notebooks | 18 | 100% |
| Successfully Executed | 9 | 50% |
| Failed/Incompatible | 6 | 33% |
| Skipped (Known Issues) | 3 | 17% |

## Execution Times by Category

### Regression Models (Fast)
| Notebook | Duration | Status | Notes |
|----------|----------|--------|-------|
| py_lasso.ipynb | 4.0s | ✅ Success | Fastest regression model |
| py_elasticnet.ipynb | 4.4s | ✅ Success | Very efficient |
| py_ols.ipynb | 4.5s | ✅ Success | Baseline model |
| py_ridge.ipynb | 5.2s | ✅ Success | Slightly slower than OLS |

**Category Average:** 4.5s  
**Success Rate:** 100% (4/4)

### Tree-Based Models (Medium)
| Notebook | Duration | Status | Notes |
|----------|----------|--------|-------|
| py_dt.ipynb | 15.1s | ✅ Success | Decision tree |
| py_rf.ipynb | 27.7s | ✅ Success | Random forest ensemble |
| py_gb.ipynb | N/A | ⏭️ Skipped | Too slow (>120s expected) |
| py_xgboost.ipynb | 2m 3.7s | ❌ Failed | Execution error |

**Category Average:** 21.4s (successful only)  
**Success Rate:** 50% (2/4)

### Neural Networks (Slow)
| Notebook | Duration | Status | Notes |
|----------|----------|--------|-------|
| py_lstm.ipynb | 2m 14.9s | ✅ Success | LSTM neural network |
| py_mlp.ipynb | 9m 14.2s | ✅ Success | Multilayer perceptron |
| py_deepvar.ipynb | N/A | ⏭️ Skipped | mxnet incompatible |

**Category Average:** 5m 44.6s  
**Success Rate:** 67% (2/3)

### Time Series Models
| Notebook | Duration | Status | Notes |
|----------|----------|--------|-------|
| py_arma.ipynb | 8.9s | ✅ Success | ARMA model |
| py_var.ipynb | N/A | ⏭️ Skipped | pyflux incompatible |

**Category Average:** 8.9s  
**Success Rate:** 50% (1/2)



## Performance Rankings

### Fastest Models (< 10s)
1. py_lasso.ipynb - 4.0s
2. py_elasticnet.ipynb - 4.4s
3. py_ols.ipynb - 4.5s
4. py_ridge.ipynb - 5.2s
5. py_arma.ipynb - 8.9s

### Medium Speed (10s - 60s)
1. py_dt.ipynb - 15.1s
2. py_rf.ipynb - 27.7s

### Slow Models (> 60s)
1. py_lstm.ipynb - 2m 14.9s (134.9s)
2. py_mlp.ipynb - 9m 14.2s (554.2s)

## Known Issues

### Platform Incompatibilities (Apple Silicon)
- **py_deepvar.ipynb**: Requires mxnet (no ARM64 support)
- **py_var.ipynb**: Requires pyflux (unmaintained, build failures)

### Performance Issues
- **py_gb.ipynb**: Gradient Boosting very slow (>120s), skipped for standard testing

### Pending R Kernel Setup
All R notebooks (r_*.ipynb) require R kernel installation:
```bash
# Install IRkernel in R
R -e 'install.packages("IRkernel"); IRkernel::installspec()'
```

## Total Execution Time

**Python Models (Successful):** 11m 49.8s (709.8s)  
**Python Models (Failed/Skipped):** 2m 3.7s (partial execution)  
**R Models:** Pending kernel setup

**Estimated Full Suite Time:** ~15-20 minutes (excluding very slow models)

## Configuration Details

Execution performed using:
- **Script:** `run_notebooks_with_cache.py`
- **Config:** `notebook_config.json`
- **Virtual Environment:** `.venv` (uv-managed)
- **Jupyter Kernel:** `nowcasting_venv`

### Timeout Settings
- Regression: 60s
- Tree: 120s
- Timeseries: 180s
- Neural: 240s
- Bayesian: 180s

## Recommendations

1. **For Quick Testing:** Run regression models (< 5s each)
2. **For Comprehensive Testing:** Include tree-based and LSTM (< 3 min total)
3. **Avoid for Speed:** MLP (9+ minutes), Gradient Boosting (skipped)
4. **Setup Required:** Install R kernel for r_*.ipynb notebooks

## Next Steps

- [ ] Install and configure R kernel for Jupyter
- [ ] Re-test failed Python notebooks (py_xgboost, py_mlp with latest cache)
- [ ] Investigate timeout increase for Gradient Boosting
- [ ] Consider alternatives for incompatible models
- [ ] Run full benchmark with R models included

---

*Statistics generated from execution cache and results as of November 29, 2025*
