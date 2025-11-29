#!/bin/bash
# Measurement script for nowcasting benchmark notebooks
# Original Repository: https://github.com/dhopp1/nowcasting_benchmark
# Reproduction/Extension: Sermet Pekin (https://github.com/SermetPekin/nowcasting_benchmark)
# Purpose: Testing and measurement helper script
# Date: November 2025
#
# This script runs the notebook execution system with a temporary config
# for testing and measurement purposes

python3 run_notebooks_with_cache.py --config tmp_config.json --force 

