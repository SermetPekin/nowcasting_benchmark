# R Package Installation Script for Nowcasting Benchmark
#
# Original Repository: https://github.com/dhopp1/nowcasting_benchmark
# Reproduction/Extension: Sermet Pekin (https://github.com/SermetPekin/nowcasting_benchmark)
# Purpose: Automate R package installation for reproduction with modern package versions
# Date: November 2025
#
# This script installs all required R packages for the nowcasting benchmark
# notebooks, including CRAN packages and GitHub-hosted packages.

# CRAN packages
cran_packages <- c(
  "tidyverse",      # Data manipulation (all notebooks)
  "plyr",           # Data manipulation tools (r_bvar.ipynb)
  "dplyr",          # Data manipulation grammar (r_bvar.ipynb)
  "mfbvar",         # Bayesian VAR (r_bvar.ipynb)
  "midasr",         # MIDAS (r_midas.ipynb)
  "midasml",        # MIDAS ML (r_midasml.ipynb)
  "imputeTS",       # Time series imputation (r_bvar, r_midas, r_midasml)
  "Rmisc",          # Miscellaneous utilities (r_bvar)
  "devtools"        # For installing GitHub packages
)

# GitHub packages (not on CRAN)
github_packages <- c(
  "dhopp1/nowcastDFM",     # Dynamic Factor Model (r_dfm.ipynb)
  "dhopp1/nowcastLSTM"     # LSTM (r_lstm.ipynb)
)

# Function to install CRAN packages if not already installed
install_cran_if_missing <- function(packages) {
  for (pkg in packages) {
    if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
      cat(sprintf("Installing %s from CRAN...\n", pkg))
      install.packages(pkg, repos = "https://cloud.r-project.org/", dependencies = TRUE)
    } else {
      cat(sprintf("%s is already installed.\n", pkg))
    }
  }
}

# Function to install GitHub packages
install_github_packages <- function(packages) {
  if (!require("devtools", quietly = TRUE)) {
    install.packages("devtools", repos = "https://cloud.r-project.org/")
  }
  
  for (pkg_path in packages) {
    pkg_name <- basename(pkg_path)
    if (!require(pkg_name, character.only = TRUE, quietly = TRUE)) {
      cat(sprintf("Installing %s from GitHub...\n", pkg_path))
      devtools::install_github(pkg_path)
    } else {
      cat(sprintf("%s is already installed.\n", pkg_name))
    }
  }
}

# Install packages
cat("Installing R packages...\n\n")
cat("=== CRAN Packages ===\n")
install_cran_if_missing(cran_packages)

cat("\n=== GitHub Packages ===\n")
install_github_packages(github_packages)

cat("\n✓ All required R packages are installed!\n")
