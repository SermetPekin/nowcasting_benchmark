# Reproduction Notes

## Apple Silicon (M1/M2/M3) Compatibility

This repository contains nowcasting benchmark models. Most models work on Apple Silicon Macs, but there are two exceptions:

### ❌ Not Compatible
- **py_deepvar.ipynb** - Requires `mxnet` which doesn't support ARM64 architecture
- **py_var.ipynb** - Requires `pyflux` which is unmaintained and has build issues on modern Python

### ✅ Compatible Models
All other models work fine on Apple Silicon:
- py_arma.ipynb
- py_dt.ipynb
- py_elasticnet.ipynb
- py_gb.ipynb
- py_lasso.ipynb
- py_lstm.ipynb
- py_mlp.ipynb
- py_ols.ipynb
- py_rf.ipynb
- py_ridge.ipynb
- py_xgboost.ipynb
- r_bvar.ipynb
- r_dfm.ipynb
- r_lstm.ipynb
- r_midas.ipynb
- r_midasml.ipynb

## Installation

### For Apple Silicon Macs:
```bash
uv pip install -r requirements-apple-silicon.txt
```

### For x86/Intel Macs or Linux:
```bash
uv pip install -r requirements.txt
```

## Known Issues

1. **numpy/pandas compatibility**: Use numpy<2.0 and pandas<2.0 to avoid binary incompatibility issues
2. **mxnet/gluonts**: Not available for Apple Silicon - DeepVAR model cannot be run
3. **pyflux**: Unmaintained package with build issues - VAR model cannot be run

## Workarounds for DeepVAR and VAR

If you need to run the DeepVAR or VAR models on Apple Silicon:
1. Use Docker with `--platform linux/amd64`
2. Use a cloud instance (AWS, GCP, Azure)
3. Use GitHub Codespaces
