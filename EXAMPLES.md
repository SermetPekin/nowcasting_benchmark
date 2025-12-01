# Run Notebooks Examples

This guide covers both automated execution and manual setup for running notebooks.

## Setup Environment

### Python Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install packages (use uv for faster installation)
pip install uv
uv pip install -r requirements-apple-silicon.txt

# For Intel/Linux systems:
# uv pip install -r requirements.txt

# Install Jupyter kernel (for automated execution)
python3 -m ipykernel install --user --name=nowcasting_venv
```

### R Environment Setup (Optional)

```bash
# Install R
brew install r

# Install R packages
Rscript install_r_packages.R

# Or manually:
R -e 'install.packages(c("IRkernel", "tidyverse", "plyr", "dplyr", "midasr"), repos="https://cran.r-project.org")'
R -e 'IRkernel::installspec(user = TRUE)'
```

## Running Notebooks Manually

### In VS Code

1. Open any notebook (e.g., `methodologies/py_lasso.ipynb`)
2. Click "Select Kernel" in top right
3. Choose Python environment → `.venv/bin/python3`
4. Run cells normally with Shift+Enter

### In Jupyter

```bash
# Activate environment
source .venv/bin/activate

# Install Jupyter if needed
uv pip install jupyter jupyterlab

# Start Jupyter
jupyter lab
# or
jupyter notebook
```

## Automated Execution

### Quick Reference

```bash
# Run original methodologies/ notebooks
python3 run_notebooks.py --config config_methodologies.json

# Run refactored methodologies_v2/ framework notebooks
python3 run_notebooks.py --config config_framework.json

# Default (same as config_methodologies.json)
python3 run_notebooks.py
```

## Configuration Files

### `config_methodologies.json` - Original Methodologies
- **Target**: `methodologies/py_*.ipynb` and `methodologies/r_*.ipynb`
- **Timeouts**: Standard (regression: 60s, neural: 240s)
- **Skips**: `py_var`, `py_deepvar`, `py_gb` (compatibility issues)
- **Cache**: `.cache_methodologies.json`
- **Results**: `results_methodologies.csv`

### `config_framework.json` - Refactored Framework Notebooks
- **Target**: `methodologies_v2/py_*_framework.ipynb` and examples
- **Timeouts**: Reduced (regression: 30s, neural: 120s)
- **Skips**: None
- **Cache**: `.cache_framework.json`
- **Results**: `results_framework.csv`

## Example Usage

### 1. Run Original Methodologies

```bash
# Preview what would run
python3 run_notebooks.py --config config_methodologies.json --dry-run

# Run with caching
python3 run_notebooks.py --config config_methodologies.json

# Force fresh run without cache
python3 run_notebooks.py --config config_methodologies.json --force

# Increase timeouts by 2x
python3 run_notebooks.py --config config_methodologies.json --multiplier 2.0
```

### 2. Run Refactored Framework Notebooks

```bash
# Preview
python3 run_notebooks.py --config config_framework.json --dry-run

# Run framework notebooks
python3 run_notebooks.py --config config_framework.json

# Force fresh run
python3 run_notebooks.py --config config_framework.json --force
```

### 3. Run Both Sequentially

```bash
# Run original methodologies first
python3 run_notebooks.py --config config_methodologies.json

# Then run framework versions
python3 run_notebooks.py --config config_framework.json

# Compare results
diff results_methodologies.csv results_framework.csv
```

### 4. Only Python Notebooks (No R)

Edit `config_methodologies.json`:
```json
"notebook_patterns": {
  "include": ["methodologies/py_*.ipynb"],
  "exclude": []
}
```

Then run:
```bash
python3 run_notebooks.py --config config_methodologies.json
```

### 5. Run Only Regression Models

Edit `config_methodologies.json`:
```json
"notebook_patterns": {
  "include": [
    "methodologies/py_ols.ipynb",
    "methodologies/py_lasso.ipynb",
    "methodologies/py_ridge.ipynb",
    "methodologies/py_elasticnet.ipynb"
  ],
  "exclude": []
}
```

Run:
```bash
python3 run_notebooks.py --config config_methodologies.json
```

### 6. Compare Performance

```bash
# Run both with timing
time python3 run_notebooks.py --config config_methodologies.json
time python3 run_notebooks.py --config config_framework.json
```

## Typical Execution Times

### Original Methodologies
- Regression models (4 notebooks): ~20s
- Tree models (2 notebooks): ~45s
- Neural networks (2 notebooks): ~10min
- Full suite: ~15min

### Framework Notebooks
- Regression models (4 notebooks): ~10s
- Tree models (4 notebooks): ~25s
- Examples (2 notebooks): ~5s
- Full suite: ~40s

## Tips

- Start with `--dry-run` to preview execution
- Use `--multiplier 2.0` if timeouts occur
- Check cache files to see completed runs
- Separate caches avoid conflicts between configs

## Troubleshooting

### "ModuleNotFoundError" in notebooks
Environment not activated or kernel not selected:
```bash
# Activate environment
source .venv/bin/activate

# Verify kernel installed
jupyter kernelspec list | grep nowcasting_venv
```

### "Config file not found"
Make sure you're in the project root directory:
```bash
cd /path/to/nowcasting_benchmark
python3 run_notebooks.py --config config_framework.json
```

### Framework notebooks fail
Make sure the framework module exists:
```bash
ls -la methodologies_v2/nowcasting_framework.py
```

### Want to clear only one cache
```bash
# Clear methodologies cache
rm .cache_methodologies.json

# Clear framework cache  
rm .cache_framework.json
```

### Compare RMSE between original and framework
```bash
# Run both
python3 run_notebooks.py --config config_methodologies.json
python3 run_notebooks.py --config config_framework.json

# Check results
cat results_methodologies.csv | grep "py_lasso"
cat results_framework.csv | grep "py_lasso_framework"
```

## Quick Manual Testing

### Test Single Notebook in VS Code
1. Open `methodologies_v2/py_ridge_framework.ipynb`
2. Select `.venv` kernel
3. Run all cells (Shift+Enter or "Run All")
4. Check output and RMSE values

### Test Framework Module
```bash
# Activate environment
source .venv/bin/activate

# Test import
python3 -c "from methodologies_v2.nowcasting_framework import *; print('Framework loaded successfully')"

# Run quick test notebook
cd methodologies_v2
jupyter notebook example_using_framework.ipynb
```

### Common Manual Workflow
```bash
# 1. Setup (once)
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv pip install -r requirements-apple-silicon.txt

# 2. Each session
source .venv/bin/activate

# 3. Run notebooks in VS Code or Jupyter
# Select .venv as kernel and run cells
```
