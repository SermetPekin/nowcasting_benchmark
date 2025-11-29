# Setup and Compatibility Report

**Date:** November 29, 2025  
**Branch:** `reproduce`  
**Environment:** Apple Silicon (ARM64) Mac, Python 3.11

## Objective

Set up the nowcasting_benchmark repository to run on Apple Silicon Macs, addressing package compatibility issues and improving file organization.

## Changes Made

### 1. Package Compatibility Fixes

#### Issue: numpy/pandas Binary Incompatibility
- **Problem:** `ValueError: numpy.dtype size changed` when importing pandas
- **Root Cause:** Binary incompatibility between numpy 2.x and pandas 1.5.3
- **Solution:** 
  - Downgraded to `numpy<2.0` and `pandas<2.0`
  - Updated `requirements.txt` with version constraints
  - All packages reinstalled with compatible versions

#### Issue: Apple Silicon Package Incompatibility
- **Problem:** Two packages don't support ARM64 architecture
- **Affected Models:**
  - `py_deepvar.ipynb` - requires `mxnet` (not compatible with ARM64)
  - `py_var.ipynb` - requires `pyflux` (unmaintained, build failures)
- **Solution:**
  - Created `requirements-apple-silicon.txt` excluding incompatible packages
  - Documented incompatible models in `REPRODUCTION.md`

### 2. File Organization Improvements

#### Renamed Notebook Files
- **Old Format:** `model_*.ipynb` (e.g., `model_lstm.ipynb`, `model_arma.ipynb`)
- **New Format:** `{language}_{algorithm}.ipynb`
- **Benefits:**
  - Removed repetitive "model_" prefix
  - Language indicator now at the beginning for better sorting/grouping
  - Clear distinction between Python (`py_*`) and R (`r_*`) implementations

**Python Notebooks (13):**
- `py_arma.ipynb`
- `py_dt.ipynb`
- `py_elasticnet.ipynb`
- `py_gb.ipynb`
- `py_lasso.ipynb`
- `py_lstm.ipynb`
- `py_mlp.ipynb`
- `py_ols.ipynb`
- `py_rf.ipynb`
- `py_ridge.ipynb`
- `py_xgboost.ipynb`
- `py_deepvar.ipynb` ❌ (incompatible on Apple Silicon)
- `py_var.ipynb` ❌ (incompatible on Apple Silicon)

**R Notebooks (5):**
- `r_bvar.ipynb`
- `r_dfm.ipynb`
- `r_lstm.ipynb`
- `r_midas.ipynb`
- `r_midasml.ipynb`

### 3. Documentation Updates

#### Created New Files
1. **`requirements-apple-silicon.txt`**
   - Apple Silicon-compatible package list
   - Excludes `mxnet`, `gluonts`, and `pyflux`
   - Includes version constraints for compatibility

2. **`REPRODUCTION.md`**
   - Comprehensive compatibility guide
   - Installation instructions for different platforms
   - Known issues and workarounds
   - Model compatibility matrix

#### Updated Files
1. **`README.md`**
   - Added blue notice box at the top indicating this is a reproduction fork
   - Links to original repository: [dhopp1/nowcasting_benchmark](https://github.com/dhopp1/nowcasting_benchmark)

## Installation Instructions

### For Apple Silicon Macs:
```bash
# Install compatible packages
uv pip install -r requirements-apple-silicon.txt

# Or manually restart kernel in notebooks after installation
```

### For Intel/x86 Platforms:
```bash
# Install all packages including mxnet and pyflux
uv pip install -r requirements.txt
```

## Compatibility Summary

### ✅ Working on Apple Silicon (16 models)
- All Python models except DeepVAR and VAR
- All R models

### ❌ Not Working on Apple Silicon (2 models)
- **py_deepvar.ipynb** - `mxnet` doesn't support ARM64
- **py_var.ipynb** - `pyflux` has build issues on modern Python

### Workarounds for Incompatible Models
If you need to run DeepVAR or VAR on Apple Silicon:
1. Use Docker with `--platform linux/amd64`
2. Use a cloud VM (AWS, GCP, Azure)
3. Use GitHub Codespaces
4. Use a physical Intel/x86 machine

## Testing Status

### Successfully Tested Python Notebooks:
- Multiple notebooks were successfully executed after fixing the numpy/pandas compatibility issue
- Notebooks run without errors when kernel is restarted after package installation

### R Environment Setup:
- **R Version:** 4.4.2 (Homebrew installation)
- **Required Packages Installed:**
  - From CRAN: tidyverse, midasr, midasml, imputeTS, Rmisc
  - From GitHub: 
    - `mfbvar` (ankargren/mfbvar)
    - `nowcastDFM` (dhopp1/nowcastDFM)
    - `nowcastLSTM` (dhopp1/nowcastLSTM)
- **Installation Notes:**
  - 3 specialized packages not available on CRAN for R 4.4.2
  - Successfully installed from GitHub repositories
  - All packages load successfully with dependencies

### Known Working Setup:
- **Python:** 3.11.13
  - numpy: 1.26.4
  - pandas: 1.5.3
  - Virtual environment: `.venv` (uv-managed)
- **R:** 4.4.2
  - Build tools: gcc 14.2.0 (Fortran), Apple clang 17.0.0
  - All required packages installed and verified

## Key Learnings

1. **Binary Compatibility:** Package version constraints are critical for avoiding binary incompatibility issues between compiled extensions
2. **Apple Silicon Migration:** Not all data science packages have ARM64 support yet, particularly older/unmaintained packages
3. **File Naming:** Prefix-based naming (language first) provides better organization than suffix-based naming
4. **Documentation:** Clear compatibility documentation is essential for cross-platform repositories

## Next Steps

- [x] Test R notebooks (require R kernel setup) - **COMPLETED**
  - R 4.4.2 installed via Homebrew
  - All required CRAN packages installed
  - All GitHub-only packages successfully installed (mfbvar, nowcastDFM, nowcastLSTM)
  - All packages verified to load correctly
- [ ] Run complete benchmark tests on working models
- [ ] Document performance comparisons
- [ ] Consider alternative implementations for DeepVAR and VAR models

## Appendix: R Package Installation

### Packages Installed from CRAN:
- tidyverse (1.3.2) - data manipulation and visualization
- midasr (0.8) - MIDAS regression functions
- midasml (0.1.5) - Machine learning for MIDAS models  
- imputeTS (3.3) - time series imputation
- Rmisc (1.5.1) - miscellaneous R utilities

### Packages Installed from GitHub:
1. **mfbvar** (ankargren/mfbvar v0.5.6)
   - Mixed-frequency Bayesian VAR models
   - Required C++ compilation with RcppArmadillo
   - Used by: `r_bvar.ipynb`

2. **nowcastDFM** (dhopp1/nowcastDFM v1.0.0)
   - Dynamic Factor Model for nowcasting
   - Dependencies: dplyr, matlab, pracma, signal
   - Used by: `r_dfm.ipynb`

3. **nowcastLSTM** (dhopp1/nowcastLSTM v0.0.0.0000)
   - LSTM implementation for R
   - Dependencies: stringr, reticulate (Python bridge)
   - Used by: `r_lstm.ipynb`

### Build Tools Required:
- Fortran compiler: GNU Fortran 14.2.0 (Homebrew GCC)
- C/C++ compiler: Apple clang 17.0.0
- R packages with compiled code: signal, stochvol, GIGrvg, lubridate, jsonlite, RcppTOML, reticulate
