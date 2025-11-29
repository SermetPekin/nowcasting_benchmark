# Manual Setup for Running Notebooks Interactively

This guide is for users who want to run notebooks manually in Jupyter/VS Code without using the automated execution system.

## Python Notebooks Manual Setup

### Option 1: Using uv (Recommended - Faster)

```bash
# Install uv if you don't have it
# Method 1: Using curl (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Method 2: Using pip (if you can't use curl)
pip install uv

# Method 3: Using pipx (isolated installation)
pipx install uv

# Method 4: Using Homebrew (macOS)
brew install uv

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install packages using uv (much faster than pip)
uv pip install -r requirements-apple-silicon.txt

# For non-Apple Silicon systems, use:
# uv pip install -r requirements.txt
```

### Option 2: Using pip

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install packages
pip install -r requirements-apple-silicon.txt

# For non-Apple Silicon systems, use:
# pip install -r requirements.txt
```

### Running Python Notebooks

After setting up the environment:

1. **In VS Code:**
   - Open any Python notebook (`py_*.ipynb`)
   - Select kernel: Click "Select Kernel" → Choose Python environment → Select `.venv/bin/python3`
   - Run cells normally

2. **In Jupyter Lab/Notebook:**
   ```bash
   # Make sure venv is activated
   source .venv/bin/activate
   
   # Install Jupyter in venv (if not already installed)
   uv pip install jupyter jupyterlab
   
   # Start Jupyter
   jupyter lab
   # OR
   jupyter notebook
   ```

---

## R Notebooks Manual Setup

### Install R and Packages

```bash
# 1. Install R (via Homebrew on macOS)
brew install r

# 2. Install R packages - Use the automated script (recommended)
Rscript install_r_packages.R
```

The script will automatically:
- Install CRAN packages: `tidyverse`, `plyr`, `dplyr`, `midasr`, `midasml`, `imputeTS`, `Rmisc`, `mfbvar`, `devtools`
- Install GitHub packages: `dhopp1/nowcastDFM`, `dhopp1/nowcastLSTM`

### Manual R Package Installation (if script doesn't work)

```bash
# Install CRAN packages
R -e 'install.packages(c("tidyverse", "plyr", "dplyr", "midasr", "midasml", "imputeTS", "Rmisc", "mfbvar", "devtools"), repos="https://cran.r-project.org")'

# Install GitHub packages
R -e 'devtools::install_github(c("dhopp1/nowcastDFM", "dhopp1/nowcastLSTM"))'
```

### Running R Notebooks

After installing R packages:

1. **In VS Code:**
   - Install R extension for VS Code (if not already installed)
   - Open any R notebook (`r_*.ipynb`)
   - Select kernel: Click "Select Kernel" → Choose "R"
   - Run cells normally

2. **In Jupyter Lab/Notebook:**
   ```bash
   # Install IRkernel for Jupyter
   R -e 'IRkernel::installspec(user = TRUE)'
   
   # Start Jupyter
   jupyter lab
   # OR
   jupyter notebook
   ```

---

## Quick Reference

### Python Environment Activation

```bash
# Activate (run this every time you open a new terminal)
source .venv/bin/activate

# Deactivate (when done)
deactivate
```

### Check Installed Packages

**Python:**
```bash
# List all installed packages
pip list

# Check specific package
pip show pandas
```

**R:**
```r
# In R console
installed.packages()[, c("Package", "Version")]

# Check specific package
packageVersion("tidyverse")
```

### Verify Setup

**Python:**
```bash
# Should show your venv Python
which python3

# Test import
python3 -c "import pandas; import numpy; print('Python packages OK')"
```

**R:**
```bash
# Test R packages
R -e 'library(tidyverse); library(nowcastLSTM); print("R packages OK")'
```

---

## Troubleshooting

### Python: Kernel not showing .venv

If VS Code doesn't show your `.venv` environment:
1. Reload VS Code window: `Cmd+Shift+P` → "Reload Window"
2. Or manually specify interpreter: `Cmd+Shift+P` → "Python: Select Interpreter" → Enter path: `.venv/bin/python3`

### R: Package not found

Make sure IRkernel is installed:
```bash
R -e 'install.packages("IRkernel"); IRkernel::installspec(user = TRUE)'
```

### uv command not found

Install uv using one of these methods:

```bash
# Method 1: Using pip (most compatible)
pip install uv

# Method 2: Using curl (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Method 3: Using pipx (isolated installation)
pipx install uv

# Method 4: Using Homebrew (macOS only)
brew install uv

# Method 5: Using conda
conda install -c conda-forge uv
```

Then restart your terminal or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

---

## Notes

- **nest_asyncio**: Some Python notebooks have `nest_asyncio` imports. This is only needed for automated execution, not for manual/interactive runs. You can safely ignore or comment out these lines when running manually.

- **Incompatible Notebooks**: 
  - `py_var.ipynb` - Requires `pyflux` (not compatible with Apple Silicon)
  - `py_deepvar.ipynb` - Requires `gluonts/mxnet` (not compatible with Apple Silicon)
  - `py_gb.ipynb` - Takes very long to execute
  - `r_bvar.ipynb` - Can take very long to execute

- **Performance**: R notebooks (especially BVAR) can take significant time. Start with faster ones like `r_midas.ipynb` or `r_lstm.ipynb` for testing.
