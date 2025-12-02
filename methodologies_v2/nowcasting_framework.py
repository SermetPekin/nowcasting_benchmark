"""
Nowcasting Framework - Professional Modular Architecture

This module provides a complete framework for GDP nowcasting with:
- Clean separation of concerns
- Object-oriented design
- Configuration-driven approach
- Production-ready inference pipeline

Author: Sermet Pekin
Date: November 2025
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from common import (
    load_data,
    setup_test_data,
    get_test_dates_and_actuals,
    gen_lagged_data,
    flatten_data,
    mean_fill_dataset,
    calculate_performance_metrics,
    plot_predictions,
    prepare_flat_data,
    add_future_dates
)

warnings.filterwarnings('ignore')


@dataclass
class NowcastConfig:
    """
    Configuration for nowcasting experiments.
    
    This dataclass encapsulates all parameters for reproducible experiments.
    
    Attributes:
        data_path: Path to main data CSV file
        metadata_path: Path to metadata CSV file
        target_variable: Name of target variable to predict
        train_start_date: Start date for training data
        test_start_date: Start date for test period
        test_end_date: End date for test period
        lags: List of vintage lags to evaluate
        n_lags: Number of lags to use in feature engineering (default for all variables)
        variable_lags: Optional dict mapping variable names to specific lag counts
        quarterly_only: Whether to use only quarterly data for training
        n_ensemble_models: Number of models in ensemble (for stochastic models)
    """
    # Data paths
    data_path: str = "../data/data_tf.csv"
    metadata_path: str = "../data/meta_data.csv"
    
    # Target and features
    target_variable: str = "gdpc1"
    
    # Time periods
    train_start_date: str = "1947-01-01"
    test_start_date: str = "2005-03-01"
    test_end_date: str = "2010-03-01"
    
    # Vintage configuration
    lags: List[int] = None
    
    # Model configuration
    n_lags: int = 4
    variable_lags: Optional[Dict[str, int]] = None
    quarterly_only: bool = True
    
    # Ensemble configuration (for stochastic models)
    n_ensemble_models: int = 1
    
    def __post_init__(self):
        """Set default lags if not provided."""
        if self.lags is None:
            self.lags = list(range(-2, 3))
    
    @classmethod
    def from_yaml(cls, filepath: str) -> 'NowcastConfig':
        """
        Load configuration from YAML file.
        
        Args:
            filepath: Path to YAML configuration file
            
        Returns:
            NowcastConfig instance
            
        Example:
            config = NowcastConfig.from_yaml("configs/ols_baseline.yaml")
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML support. Install with: pip install pyyaml")
        
        with open(filepath, 'r') as f:
            params = yaml.safe_load(f)
        
        return cls(**params)
    
    def to_yaml(self, filepath: str):
        """
        Save configuration to YAML file.
        
        Args:
            filepath: Path where YAML file will be saved
            
        Example:
            config.to_yaml("configs/my_experiment.yaml")
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML support. Install with: pip install pyyaml")
        
        # Convert to dict with all fields
        config_dict = {
            'data_path': self.data_path,
            'metadata_path': self.metadata_path,
            'target_variable': self.target_variable,
            'train_start_date': self.train_start_date,
            'test_start_date': self.test_start_date,
            'test_end_date': self.test_end_date,
            'lags': self.lags,
            'n_lags': self.n_lags,
            'quarterly_only': self.quarterly_only,
            'n_ensemble_models': self.n_ensemble_models
        }
        
        if self.variable_lags:
            config_dict['variable_lags'] = self.variable_lags
        
        with open(filepath, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert config to dictionary for logging.
        
        Returns:
            Dictionary with key configuration parameters
        """
        config_dict = {
            'target': self.target_variable,
            'test_period': f"{self.test_start_date} to {self.test_end_date}",
            'lags': self.lags,
            'n_lags': self.n_lags,
            'n_ensemble': self.n_ensemble_models
        }
        if self.variable_lags:
            config_dict['variable_lags'] = self.variable_lags
        return config_dict


class DataManager:
    """
    Manages data loading, preprocessing, and vintage generation.
    
    Encapsulates all data-related operations to ensure clean separation
    of data handling from modeling logic.
    
    Attributes:
        config: NowcastConfig instance
        data: Main dataset
        metadata: Metadata with publication lags
        test_data: Filtered test dataset
        test_dates: List of test period dates
        actuals: Actual values for test period
    """
    
    def __init__(self, config: NowcastConfig):
        """
        Initialize DataManager with configuration.
        
        Args:
            config: NowcastConfig instance with data paths and parameters
        """
        self.config = config
        self.data: Optional[pd.DataFrame] = None
        self.metadata: Optional[pd.DataFrame] = None
        self.test_data: Optional[pd.DataFrame] = None
        self.test_dates: Optional[List[str]] = None
        self.actuals: Optional[List[float]] = None
        
    def load_data(self) -> 'DataManager':
        """
        Load main data and metadata from CSV files.
        
        Returns:
            Self for method chaining
        """
        self.data, self.metadata = load_data(
            self.config.data_path,
            self.config.metadata_path
        )
        print(f"✓ Loaded data: {self.data.shape}")
        print(f"✓ Loaded metadata: {self.metadata.shape}")
        return self
    
    def prepare_test_data(self) -> 'DataManager':
        """
        Prepare test dataset based on configuration.
        
        Returns:
            Self for method chaining
        """
        self.test_data = self.data.loc[
            (self.data.date >= self.config.train_start_date) & 
            (self.data.date <= self.config.test_end_date), 
            :
        ].reset_index(drop=True)
        
        # Extract test dates and actuals
        self.test_dates, self.actuals = get_test_dates_and_actuals(
            self.test_data,
            self.config.test_start_date,
            self.config.test_end_date,
            self.config.target_variable
        )
        
        print(f"✓ Test data prepared: {len(self.test_dates)} periods")
        return self
    
    def get_train_data(self, cutoff_date: str) -> pd.DataFrame:
        """
        Get training data up to cutoff date.
        
        Args:
            cutoff_date: Date to cut off training data
            
        Returns:
            Training data as DataFrame
        """
        cutoff = pd.to_datetime(cutoff_date) - pd.tseries.offsets.DateOffset(months=3)
        return self.test_data.loc[
            self.test_data.date <= str(cutoff)[:10], :
        ]
    
    def get_vintage_data(self, date: str, lag: int) -> pd.DataFrame:
        """
        Generate vintage data for specific date and lag.
        
        Args:
            date: Target date for prediction
            lag: Vintage lag (negative = past, positive = future)
            
        Returns:
            Data as it would appear at the vintage
        """
        return gen_lagged_data(self.metadata, self.test_data, date, lag)
    
    def summary(self) -> pd.DataFrame:
        """
        Generate summary statistics of the data.
        
        Returns:
            DataFrame with summary statistics
        """
        summary_data = {
            'Metric': [
                'Total Observations',
                'Test Periods',
                'Variables',
                'Target Variable',
                'Missing in Target (%)'
            ],
            'Value': [
                len(self.data),
                len(self.test_dates) if self.test_dates else 0,
                len(self.data.columns) - 1,  # Exclude date
                self.config.target_variable,
                f"{self.data[self.config.target_variable].isna().sum() / len(self.data) * 100:.1f}%"
            ]
        }
        return pd.DataFrame(summary_data)


class ModelManager:
    """
    Manages model training, prediction, and ensemble operations.
    
    Supports both single models and ensemble averaging for stochastic models.
    
    Attributes:
        model_class: Scikit-learn compatible model class
        model_params: Dictionary of model hyperparameters
        config: NowcastConfig instance
        predictions: Dictionary mapping lags to prediction lists
        trained_models: List of trained model instances
    """
    
    def __init__(self, model_class, model_params: Dict[str, Any], config: NowcastConfig):
        """
        Initialize ModelManager.
        
        Args:
            model_class: Scikit-learn compatible model class
            model_params: Dictionary of model hyperparameters
            config: NowcastConfig instance
        """
        self.model_class = model_class
        self.model_params = model_params
        self.config = config
        self.predictions: Dict[int, List[float]] = {k: [] for k in config.lags}
        self.trained_models: List[Any] = []
        
    def train_ensemble(self, X: pd.DataFrame, y: pd.Series) -> List[Any]:
        """
        Train ensemble of models.
        
        Args:
            X: Training features
            y: Training target
            
        Returns:
            List of trained models
        """
        models = []
        for i in range(self.config.n_ensemble_models):
            model = self.model_class(**self.model_params)
            model.fit(X, y)
            models.append(model)
        return models
    
    def predict_ensemble(self, models: List[Any], X: pd.DataFrame) -> float:
        """
        Get ensemble prediction (average of all models).
        
        Args:
            models: List of trained models
            X: Features for prediction
            
        Returns:
            Averaged prediction
        """
        predictions = [model.predict(X)[0] for model in models]
        return np.nanmean(predictions)
    
    def run_backtest(self, data_manager: DataManager) -> 'ModelManager':
        """
        Run full backtest across all test dates and vintages.
        
        Args:
            data_manager: DataManager instance with prepared data
            
        Returns:
            Self for method chaining
        """
        print(f"\nRunning backtest with {self.config.n_ensemble_models} ensemble model(s)...")
        
        for idx, date in enumerate(data_manager.test_dates):
            # Progress indicator
            if (idx + 1) % 5 == 0:
                print(f"  Processing {idx + 1}/{len(data_manager.test_dates)} dates...")
            
            # Get training data
            train_data = data_manager.get_train_data(date)
            transformed_train = prepare_flat_data(
                train_data, 
                self.config.target_variable, 
                self.config.n_lags,
                self.config.quarterly_only,
                self.config.variable_lags
            )
            
            # Train ensemble
            X_train = transformed_train.drop(["date", self.config.target_variable], axis=1)
            y_train = transformed_train[self.config.target_variable]
            models = self.train_ensemble(X_train, y_train)
            
            # Predict for each vintage
            for lag in self.config.lags:
                vintage_data = data_manager.get_vintage_data(date, lag)
                vintage_data = mean_fill_dataset(train_data, vintage_data)
                vintage_data = flatten_data(vintage_data, self.config.target_variable, self.config.n_lags, self.config.variable_lags)
                
                X_pred = vintage_data.loc[
                    vintage_data.date == date, :
                ].drop(["date", self.config.target_variable], axis=1)
                
                prediction = self.predict_ensemble(models, X_pred)
                self.predictions[lag].append(prediction)
            
            # Store last models for inference
            if idx == len(data_manager.test_dates) - 1:
                self.trained_models = models
        
        print(f"✓ Backtest complete: {len(data_manager.test_dates)} periods processed")
        return self
    
    def get_predictions(self) -> Dict[int, List[float]]:
        """
        Get all predictions by vintage.
        
        Returns:
            Dictionary mapping lags to prediction lists
        """
        return self.predictions


class EvaluationManager:
    """
    Manages model evaluation, metrics calculation, and result comparison.
    
    Attributes:
        results: Dictionary mapping model names to their results
    """
    
    def __init__(self):
        """Initialize evaluation manager."""
        self.results: Dict[str, Dict] = {}
    
    def add_model_results(
        self, 
        model_name: str, 
        predictions: Dict[int, List[float]], 
        actuals: List[float],
        lags: List[int]
    ) -> 'EvaluationManager':
        """
        Add model results for evaluation.
        
        Args:
            model_name: Name identifier for the model
            predictions: Dictionary mapping lags to predictions
            actuals: List of actual values
            lags: List of lags evaluated
            
        Returns:
            Self for method chaining
        """
        # Calculate metrics
        performance = calculate_performance_metrics(actuals, predictions, lags)
        
        # Store results
        self.results[model_name] = {
            'predictions': predictions,
            'actuals': actuals,
            'performance': performance,
            'lags': lags
        }
        
        return self
    
    def get_performance_table(self) -> pd.DataFrame:
        """
        Create comparison table of all models' performance.
        
        Returns:
            DataFrame with performance metrics by model and vintage
        """
        dfs = []
        for model_name, results in self.results.items():
            perf = results['performance'].copy()
            perf['Model'] = model_name
            dfs.append(perf)
        
        if not dfs:
            return pd.DataFrame()
        
        combined = pd.concat(dfs, ignore_index=True)
        
        # Pivot for better comparison
        pivot = combined.pivot(index='Vintage', columns='Model', values='RMSE')
        
        # Only add 'Best Model' column if there are multiple models
        if len(pivot.columns) > 1:
            pivot['Best Model'] = pivot.idxmin(axis=1)
        
        return pivot.reset_index()
    
    def get_best_vintage(self, model_name: str) -> Tuple[int, float]:
        """
        Find best performing vintage for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Tuple of (best_lag, best_rmse)
        """
        perf = self.results[model_name]['performance']
        best_idx = perf['RMSE'].idxmin()
        return perf.loc[best_idx, 'Vintage'], perf.loc[best_idx, 'RMSE']
    
    def summary_report(self) -> str:
        """
        Generate text summary of evaluation results.
        
        Returns:
            Formatted summary string
        """
        lines = ["=" * 70, "MODEL EVALUATION SUMMARY", "=" * 70, ""]
        
        for model_name, results in self.results.items():
            best_lag, best_rmse = self.get_best_vintage(model_name)
            avg_rmse = results['performance']['RMSE'].mean()
            
            lines.append(f"Model: {model_name}")
            lines.append(f"  Average RMSE across vintages: {avg_rmse:.6f}")
            lines.append(f"  Best vintage: lag={best_lag} (RMSE={best_rmse:.6f})")
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)


class VisualizationManager:
    """
    Manages all visualizations for nowcasting results.
    
    Provides high-quality, publication-ready plots.
    
    Attributes:
        evaluator: EvaluationManager with results to visualize
    """
    
    def __init__(self, evaluation_manager: EvaluationManager):
        """
        Initialize visualization manager.
        
        Args:
            evaluation_manager: EvaluationManager with results to visualize
        """
        self.evaluator = evaluation_manager
    
    def plot_predictions_vs_actuals(
        self, 
        model_name: str, 
        figsize: Tuple[int, int] = (15, 8)
    ) -> plt.Figure:
        """
        Plot predictions vs actuals for all vintages.
        
        Args:
            model_name: Name of model to plot
            figsize: Figure size tuple
            
        Returns:
            Matplotlib figure object
        """
        results = self.evaluator.results[model_name]
        actuals = results['actuals']
        predictions = results['predictions']
        lags = results['lags']
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot actuals
        ax.plot(actuals, 'o-', label='Actuals', linewidth=2.5, 
                markersize=8, color='black', zorder=10)
        
        # Plot predictions for each vintage
        lag_names = {
            -2: "Two months back",
            -1: "One month back",
            0: "Current month",
            1: "One month ahead",
            2: "Two months ahead"
        }
        
        colors = sns.color_palette("husl", len(lags))
        for idx, lag in enumerate(lags):
            label = lag_names.get(lag, f"Lag {lag}")
            ax.plot(predictions[lag], 's--', label=label, 
                   linewidth=1.5, markersize=6, alpha=0.7, color=colors[idx])
        
        ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
        ax.set_ylabel('GDP Growth Rate', fontsize=12, fontweight='bold')
        ax.set_title(f'{model_name} - Predictions vs Actuals by Vintage', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', frameon=True, shadow=True, fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_performance_comparison(
        self, 
        figsize: Tuple[int, int] = (12, 6)
    ) -> plt.Figure:
        """
        Plot RMSE comparison across models and vintages.
        
        Args:
            figsize: Figure size tuple
            
        Returns:
            Matplotlib figure object
        """
        perf_table = self.evaluator.get_performance_table()
        
        if perf_table.empty or len(self.evaluator.results) < 2:
            print("Need at least 2 models for comparison plot")
            return None
        
        fig, ax = plt.subplots(figsize=figsize)
        
        model_cols = [col for col in perf_table.columns if col not in ['Vintage', 'Best Model']]
        x = perf_table['Vintage']
        
        for col in model_cols:
            ax.plot(x, perf_table[col], 'o-', label=col, linewidth=2, markersize=8)
        
        ax.set_xlabel('Vintage (Lag)', fontsize=12, fontweight='bold')
        ax.set_ylabel('RMSE', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Comparison by Vintage', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_error_distribution(
        self, 
        model_name: str,
        figsize: Tuple[int, int] = (14, 6)
    ) -> plt.Figure:
        """
        Plot error distribution for each vintage.
        
        Args:
            model_name: Name of model to analyze
            figsize: Figure size tuple
            
        Returns:
            Matplotlib figure object
        """
        results = self.evaluator.results[model_name]
        actuals = np.array(results['actuals'])
        predictions = results['predictions']
        lags = results['lags']
        
        fig, axes = plt.subplots(1, len(lags), figsize=figsize, sharey=True)
        
        lag_names = {-2: "Lag -2", -1: "Lag -1", 0: "Lag 0", 1: "Lag +1", 2: "Lag +2"}
        
        for idx, (ax, lag) in enumerate(zip(axes, lags)):
            errors = actuals - np.array(predictions[lag])
            
            ax.hist(errors, bins=15, alpha=0.7, edgecolor='black')
            ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Error')
            ax.set_xlabel('Prediction Error', fontsize=10)
            if idx == 0:
                ax.set_ylabel('Frequency', fontsize=10)
            ax.set_title(lag_names.get(lag, f'Lag {lag}'), fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
        
        fig.suptitle(f'{model_name} - Error Distribution by Vintage', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig


class InferencePipeline:
    """
    Production inference pipeline for new predictions.
    
    Encapsulates the entire prediction workflow for deployment.
    
    Attributes:
        model_manager: Trained ModelManager instance
        data_manager: DataManager with historical data
        config: NowcastConfig instance
    """
    
    def __init__(
        self, 
        model_manager: ModelManager, 
        data_manager: DataManager,
        config: NowcastConfig
    ):
        """
        Initialize inference pipeline.
        
        Args:
            model_manager: Trained ModelManager instance
            data_manager: DataManager with historical data
            config: NowcastConfig instance
        """
        self.model_manager = model_manager
        self.data_manager = data_manager
        self.config = config
    
    def predict_new_date(self, target_date: str) -> Dict[str, Any]:
        """
        Generate prediction for a new target date.
        
        Args:
            target_date: Date to predict (e.g., "2010-06-01")
            
        Returns:
            Dictionary with prediction and metadata
        """
        # Prepare data with future dates
        new_data = self.data_manager.test_data.copy()
        new_data = add_future_dates(new_data, target_date)
        
        # Transform data
        transformed_data = prepare_flat_data(
            new_data,
            self.config.target_variable,
            self.config.n_lags,
            quarterly_only=False,
            variable_lags=self.config.variable_lags
        )
        
        # Extract features for target date
        X_new = transformed_data.loc[
            transformed_data.date == target_date, :
        ].drop(["date", self.config.target_variable], axis=1)
        
        # Generate prediction
        prediction = self.model_manager.predict_ensemble(
            self.model_manager.trained_models,
            X_new
        )
        
        return {
            'target_date': target_date,
            'prediction': prediction,
            'target_variable': self.config.target_variable,
            'n_models': len(self.model_manager.trained_models),
            'model_class': self.model_manager.model_class.__name__
        }
    
    def batch_predict(self, target_dates: List[str]) -> pd.DataFrame:
        """
        Generate predictions for multiple dates.
        
        Args:
            target_dates: List of dates to predict
            
        Returns:
            DataFrame with predictions for all dates
        """
        results = []
        for date in target_dates:
            pred_info = self.predict_new_date(date)
            results.append(pred_info)
        
        return pd.DataFrame(results)


# Convenience function for quick setup
def quick_setup(
    target_variable: str = "gdpc1",
    n_lags: int = 4,
    test_start: str = "2005-03-01",
    test_end: str = "2010-03-01",
    n_ensemble: int = 1
) -> Tuple[NowcastConfig, DataManager]:
    """
    Quick setup for common use cases.
    
    Args:
        target_variable: Target variable name
        n_lags: Number of lags for features
        test_start: Test period start date
        test_end: Test period end date
        n_ensemble: Number of ensemble models
        
    Returns:
        Tuple of (config, data_manager) ready to use
    """
    config = NowcastConfig(
        target_variable=target_variable,
        n_lags=n_lags,
        test_start_date=test_start,
        test_end_date=test_end,
        n_ensemble_models=n_ensemble
    )
    
    data_manager = DataManager(config)
    data_manager.load_data().prepare_test_data()
    
    return config, data_manager
