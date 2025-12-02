"""
Nowkit - GDP Nowcasting Framework

A modular framework for GDP nowcasting with support for:
- Multiple model types (OLS, Ridge, Lasso, RF, XGBoost, etc.)
- Vintage data handling
- Variable-specific lag configurations
- YAML-based configuration
- Production inference pipelines
"""

from .nowcasting_framework import (
    NowcastConfig,
    DataManager,
    ModelManager,
    EvaluationManager,
    VisualizationManager,
    InferencePipeline
)

__all__ = [
    'NowcastConfig',
    'DataManager',
    'ModelManager',
    'EvaluationManager',
    'VisualizationManager',
    'InferencePipeline'
]

__version__ = '0.1.0'
