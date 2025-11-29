# nowcasting_benchmark

> [!NOTE]
> **This is a reproduction fork for testing and compatibility improvements. For the original repository, see [dhopp1/nowcasting_benchmark](https://github.com/dhopp1/nowcasting_benchmark).**

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration System](#configuration-system)
- [Command Line Options](#command-line-options)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Original Repository Information](#original-repository-information)

## Overview

This fork provides an automated execution system for both **Python** and **R** Jupyter notebooks with intelligent kernel selection, caching, and configurable timeouts.

### Key Features

- ✅ **Dual Language Support**: Automatic kernel detection for Python (`py_*.ipynb`) and R (`r_*.ipynb`) notebooks
- ✅ **Caching**: Successful executions cached, skip re-running
- ✅ **Configurable Timeouts**: Different timeouts per category (regression, neural, timeseries, etc.)
- ✅ **Skip Lists**: Exclude incompatible or slow notebooks
- ✅ **Real-time Output**: See execution progress as it happens

### Architecture

```
run_notebooks_with_cache.py
    ├── Python notebooks → nowcasting_venv kernel
    └── R notebooks → ir kernel
```

The script automatically:
- Detects notebook type by filename prefix
- Selects appropriate Jupyter kernel
- Caches successful executions
- Reports timing statistics

---

## Prerequisites

### 1. Python Virtual Environment Setup (Required for Python notebooks)

The script automatically uses the `.venv` virtual environment if present. To set it up:

```bash
# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install packages with uv
uv pip install -r requirements-apple-silicon.txt

# Install the venv as a Jupyter kernel (IMPORTANT!)
python3 -m ipykernel install --user --name=nowcasting_venv --display-name="Python (nowcasting_venv)"
```

**Why the kernel installation is needed:**
- Jupyter notebooks need a registered kernel to execute code
- The script uses `--ExecutePreprocessor.kernel_name=nowcasting_venv` to ensure notebooks run with your venv packages
- Without this step, notebooks will use the system Python and fail with `ModuleNotFoundError`

### 2. R Kernel Setup (Required for R notebooks)

Install R and the IRkernel package:

```bash
# Install R (via Homebrew on macOS)
brew install r

# Install required R packages (automated script - recommended)
Rscript install_r_packages.R

# OR install manually:
# First install CRAN packages
R -e 'install.packages(c("IRkernel", "tidyverse", "plyr", "dplyr", "midasr", "midasml", "imputeTS", "Rmisc", "mfbvar", "devtools"), repos="https://cran.r-project.org")'

# Then install GitHub packages
R -e 'devtools::install_github(c("dhopp1/nowcastDFM", "dhopp1/nowcastLSTM"))'

# Install the R kernel for Jupyter
R -e 'IRkernel::installspec(user = TRUE)'
```

**The `install_r_packages.R` script:**
- Checks which packages are already installed
- Only installs missing packages
- Includes all dependencies needed for R notebooks (BVAR, DFM, LSTM, MIDAS, MIDASML)

**Verify both kernels are installed:**
```bash
jupyter kernelspec list
# Should show:
#   ir                 /Users/YOUR_USER/Library/Jupyter/kernels/ir
#   nowcasting_venv    /Users/YOUR_USER/Library/Jupyter/kernels/nowcasting_venv
```

---

## Quick Start

```bash
# Run all notebooks (uses cache, auto-detects Python/R)
python3 run_notebooks_with_cache.py

# Clear cache and re-run all
python3 run_notebooks_with_cache.py --force

# Preview execution plan without running
python3 run_notebooks_with_cache.py --dry-run

# Run with 2x timeout (for slow notebooks)
python3 run_notebooks_with_cache.py --multiplier 2.0
```

**How it works:**
- Script automatically detects notebook type by filename prefix (`py_*` vs `r_*`)
- Python notebooks execute with `nowcasting_venv` kernel
- R notebooks execute with `ir` kernel
- Results cached in `.notebook_execution_cache.json`

---

## Configuration System

All execution settings are controlled via `notebook_config.json`:

### Execution Settings

```json
"execution": {
  "default_timeout": 60,
  "timeout_by_category": {
    "regression": 60,
    "tree": 120,
    "timeseries": 180,
    "neural": 240,
    "bayesian": 600
  },
  "global_timeout_multiplier": 1.0
}
```

- **default_timeout**: Fallback timeout for notebooks without a category
- **timeout_by_category**: Specific timeouts per category (in seconds)
- **global_timeout_multiplier**: Multiply all timeouts (use `--multiplier` to override)

### Skip Lists

```json
"skip_notebooks": {
  "py_var.ipynb": "pyflux not compatible with Apple Silicon/modern Python",
  "py_deepvar.ipynb": "gluonts/mxnet not compatible with Apple Silicon",
  "py_gb.ipynb": "Gradient Boosting takes longer to execute"
}
```

Add notebooks to skip with a reason. Useful for:
- Incompatible packages
- Very slow notebooks
- Known broken notebooks
- Platform-specific issues

### Notebook Patterns

```json
"notebook_patterns": {
  "include": [
    "methodologies/py_*.ipynb",
    "methodologies/r_*.ipynb"
  ],
  "exclude": []
}
```

- **include**: Glob patterns for notebooks to execute
- **exclude**: Glob patterns to exclude (overrides include)

### Categories

```json
"categories": {
  "py_ols.ipynb": "regression",
  "py_lasso.ipynb": "regression",
  "py_dt.ipynb": "tree",
  "py_arma.ipynb": "timeseries",
  "py_lstm.ipynb": "neural",
  "r_bvar.ipynb": "bayesian",
  "r_dfm.ipynb": "timeseries",
  "r_midas.ipynb": "timeseries",
  "r_lstm.ipynb": "neural"
}
```

Assign each notebook to a category. Categories determine timeouts via `timeout_by_category`. Works for both Python and R notebooks.

### Cache Settings

```json
"cache": {
  "enabled": true,
  "cache_file": ".notebook_execution_cache.json",
  "force_fresh_run": false
}
```

### Output Settings

```json
"output": {
  "results_file": "notebook_execution_results.csv",
  "log_file": "NOTEBOOK_EXECUTION_LOG.md"
}
```

---

## Command Line Options

```
usage: run_notebooks_with_cache.py [-h] [--force] [--config FILE] 
                                   [--multiplier N] [--dry-run]

Options:
  --force           Clear cache and re-run all notebooks
  --config FILE     Use alternate configuration file (default: notebook_config.json)
  --multiplier N    Multiply all timeouts by N (e.g., 2.0 for double timeout)
  --dry-run         Show what would be executed without running
```

---

## Examples

### Example 1: Skip slow notebooks temporarily
Edit `notebook_config.json`:
```json
"skip_notebooks": {
  "py_gb.ipynb": "Too slow for quick testing"
}
```

### Example 2: Increase timeouts for longer-running notebooks
```bash
python3 run_notebooks_with_cache.py --multiplier 2.0
```

This doubles all timeouts (regression: 60→120s, neural: 240→480s, bayesian: 600→1200s, etc.)

**For very long notebooks (like BVAR):**
```bash
python3 run_notebooks_with_cache.py --multiplier 5.0
# bayesian: 600→3000s (50 minutes)
```

### Example 3: Test only Python notebooks
Edit `notebook_config.json`:
```json
"notebook_patterns": {
  "include": ["methodologies/py_*.ipynb"],
  "exclude": []
}
```

### Example 4: Test only R notebooks
Edit `notebook_config.json`:
```json
"notebook_patterns": {
  "include": ["methodologies/r_*.ipynb"],
  "exclude": []
}
```

### Example 5: Fresh run without cache
```bash
python3 run_notebooks_with_cache.py --force
```

### Example 6: Preview execution plan
```bash
python3 run_notebooks_with_cache.py --dry-run
```

Shows which notebooks would be executed, skipped, or cached.

### Example 7: Use custom config file
```bash
python3 run_notebooks_with_cache.py --config my_custom_config.json
```

---

## Output Files

1. **notebook_execution_results.csv**: Detailed results with status, duration, category, timestamp, and errors
2. **.notebook_execution_cache.json**: Cached successful executions (auto-managed)
3. **NOTEBOOK_EXECUTION_LOG.md**: Manual tracking log (optional)

## Workflow Tips

1. **First run**: Start with `--dry-run` to preview execution plan
2. **Add incompatible notebooks** to skip_notebooks with reasons
3. **Adjust timeouts** per category based on your hardware
4. **Use --force** when you update notebook code and need fresh execution
5. **Use --multiplier** to retry failed notebooks with more time

## Categories and Default Timeouts

| Category | Timeout | Description |
|----------|---------|-------------|
| regression | 60s | Linear models (OLS, Lasso, Ridge, ElasticNet) |
| tree | 120s | Tree-based (Decision Tree, Random Forest, XGBoost) |
| timeseries | 180s | Time series models (ARMA, VAR, DFM, MIDAS) |
| neural | 240s | Neural networks (MLP, LSTM, DeepVAR) |
| bayesian | 600s | Bayesian models (BVAR) - use `--multiplier 2.0` or higher for longer runs |

## Cache Behavior

- Successful executions are cached automatically
- Cache persists across runs (unless `--force` is used)
- Cached results show original execution time and timestamp
- Failed executions are NOT cached (will retry next run)
- Skipped notebooks appear in results but don't execute

---

## Troubleshooting

### "Config file not found"
Create `notebook_config.json` in the same directory as the script.

### Python: "ModuleNotFoundError: No module named 'pmdarima'" (or similar)
The notebook kernel isn't using your venv. Fix:
```bash
# Install the venv as a Jupyter kernel
.venv/bin/python3 -m ipykernel install --user --name=nowcasting_venv --display-name="Python (nowcasting_venv)"
```

Verify the kernel is installed:
```bash
jupyter kernelspec list
# Should show: nowcasting_venv    /Users/YOUR_USER/Library/Jupyter/kernels/nowcasting_venv
```

### R: "Error in library(XXX) : there is no package called 'XXX'"
The R kernel can't find required packages. Install them:
```bash
# Use the automated script (recommended)
Rscript install_r_packages.R

# OR install manually
# CRAN packages:
R -e 'install.packages(c("tidyverse", "plyr", "dplyr", "midasr", "midasml", "imputeTS", "Rmisc", "mfbvar", "devtools"), repos="https://cran.r-project.org")'

# GitHub packages (nowcastDFM, nowcastLSTM):
R -e 'devtools::install_github(c("dhopp1/nowcastDFM", "dhopp1/nowcastLSTM"))'
```

### R: "Kernel 'ir' not found"
Install the IRkernel:
```bash
R -e 'install.packages("IRkernel", repos="https://cran.r-project.org")'
R -e 'IRkernel::installspec(user = TRUE)'
```

Verify:
```bash
jupyter kernelspec list | grep ir
# Should show: ir    /Users/YOUR_USER/Library/Jupyter/kernels/ir
```

### "ModuleNotFoundError: No module named 'nest_asyncio'"
Some notebooks include `nest_asyncio` for automated execution via `jupyter nbconvert`. This is only needed when running notebooks programmatically, not when running interactively in Jupyter/VS Code.

**If running interactively:** You can safely remove or comment out these lines:
```python
# Fix for event loop issues in nbconvert
import nest_asyncio
nest_asyncio.apply()
```

**If using the automated script:** Install it:
```bash
uv pip install nest-asyncio
```

**Which notebooks have this:**
- py_arma.ipynb (pmdarima has async operations)
- py_lstm.ipynb (nowcast_lstm has async operations)
- py_xgboost.ipynb (xgboost has async operations)
- py_var.ipynb (pyflux has async operations)

### Notebook times out
1. Increase timeout in config: `"timeout_by_category": {"neural": 360}`
2. Or use `--multiplier 2.0` for a temporary increase
3. Or add to skip_notebooks if temporarily skipping

### Want to re-run specific notebook
Remove its entry from `.notebook_execution_cache.json` or use `--force` to re-run all.

### Cache getting stale
Use `--force` to clear cache and re-run all notebooks fresh.

### Check which Python is being used
The script will show:
```
📦 Using Python venv: /path/to/.venv/bin/python3
```

If you see `⚠️ No venv found`, create and activate the virtual environment.

### Check which R kernel is being used
The script will show:
```
📊 Using R kernel: ir
```

If R notebooks fail, verify the kernel:
```bash
jupyter kernelspec list | grep ir
```

---

## Original Repository Information

This repository is an accompaniment to an article (available [here](https://www.researchgate.net/publication/375338704_Benchmarking_econometric_and_machine_learning_methodologies_in_nowcasting_GDP) or [here](https://rdcu.be/dqh30)) benchmarking common nowcasting and machine learning methodologies. 

For complete details about the methodologies, data format, and original research, see [README_ORIGINAL.md](README_ORIGINAL.md).

### Compatibility Notes

#### Apple Silicon Support
- **requirements-apple-silicon.txt** - Apple Silicon compatible package versions
- Modified notebooks to work with `nest_asyncio` for event loop issues
- Identified incompatible packages: `pyflux` (py_var), `gluonts/mxnet` (py_deepvar)

#### Python Notebooks
- 9 working Python methodologies: OLS, Lasso, Ridge, ElasticNet, Decision Tree, Random Forest, XGBoost, ARMA, LSTM, MLP
- 3 incompatible: VAR (pyflux), DeepVAR (gluonts/mxnet), Gradient Boost (slow)

#### R Notebooks
- 5 R methodologies: BVAR, DFM, MIDAS, MIDASML, LSTM
- Note: `nowcastDFM` and `nowcastLSTM` installed from GitHub (`dhopp1/nowcastDFM`, `dhopp1/nowcastLSTM`)

---

## Additional Resources

- **[NOTEBOOK_EXECUTION_LOG.md](NOTEBOOK_EXECUTION_LOG.md)** - Manual execution tracking log
- **[EXECUTION_STATISTICS.md](EXECUTION_STATISTICS.md)** - Timing statistics for completed runs
- **[README_ORIGINAL.md](README_ORIGINAL.md)** - Complete original repository documentation
