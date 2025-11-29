# Reproduction Notes

## Apple Silicon (M1/M2/M3) Compatibility

This repository contains nowcasting benchmark models. Most models work on Apple Silicon Macs, but there is one exception:

### ❌ Not Compatible
- **model_deepvar.ipynb** - Requires `mxnet` which doesn't support ARM64 architecture

### ✅ Compatible Models
All other models work fine on Apple Silicon:
- model_arma.ipynb
- model_bvar.ipynb
- model_dfm.ipynb
- model_dt.ipynb
- model_elasticnet.ipynb
- model_gb.ipynb
- model_lasso.ipynb
- model_lstm.ipynb
- model_lstm_r.ipynb
- model_midas.ipynb
- model_midasml.ipynb
- model_mlp.ipynb
- model_ols.ipynb
- model_rf.ipynb
- model_ridge.ipynb
- model_var.ipynb
- model_xgboost.ipynb

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

## Workarounds for DeepVAR

If you need to run the DeepVAR model on Apple Silicon:
1. Use Docker with `--platform linux/amd64`
2. Use a cloud instance (AWS, GCP, Azure)
3. Use GitHub Codespaces
