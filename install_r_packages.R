# R Package Installation Script for Nowcasting Benchmark

# Required packages for R notebooks
required_packages <- c(
  "tidyverse",      # Data manipulation (all notebooks)
  "mfbvar",         # Bayesian VAR (r_bvar.ipynb)
  "nowcastDFM",     # Dynamic Factor Model (r_dfm.ipynb)
  "nowcastLSTM",    # LSTM (r_lstm.ipynb)
  "midasr",         # MIDAS (r_midas.ipynb)
  "midasml",        # MIDAS ML (r_midasml.ipynb)
  "imputeTS",       # Time series imputation (r_bvar, r_midas, r_midasml)
  "Rmisc"           # Miscellaneous utilities (r_bvar)
)

# Function to install packages if not already installed
install_if_missing <- function(packages) {
  for (pkg in packages) {
    if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
      cat(sprintf("Installing %s...\n", pkg))
      install.packages(pkg, repos = "https://cloud.r-project.org/", dependencies = TRUE)
    } else {
      cat(sprintf("%s is already installed.\n", pkg))
    }
  }
}

# Install packages
cat("Checking and installing R packages...\n\n")
install_if_missing(required_packages)

cat("\n✓ All required R packages are installed!\n")
