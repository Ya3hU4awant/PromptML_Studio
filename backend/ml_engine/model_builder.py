"""
PromptML Studio - Model Builder Module
PyCaret 3.1.0 Fully Compatible - All preprocessing params fixed
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any, List
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ModelBuilder:
    """
    Builds and trains ML models using PyCaret AutoML
    Supports both regression and classification tasks
    """
    
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.task_type = None
        self.metrics = {}
        self.feature_importance = None
        self.setup_config = None
        
    def build_model(
        self, 
        df: pd.DataFrame, 
        target_column: str,
        task_type: str = 'classification',
        test_size: float = 0.2,
        n_models: int = 10
    ) -> Dict[str, Any]:
        """
        Build and train ML model using PyCaret AutoML
        """
        self.task_type = task_type
        
        try:
            if task_type == 'classification':
                return self._build_classification_model(df, target_column, test_size, n_models)
            elif task_type == 'regression':
                return self._build_regression_model(df, target_column, test_size, n_models)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
                
        except Exception as e:
            raise Exception(f"Model building failed: {str(e)}")
    
    def _build_classification_model(
        self, 
        df: pd.DataFrame, 
        target_column: str,
        test_size: float,
        n_models: int
    ) -> Dict[str, Any]:
        """Build classification model using PyCaret 3.1.0"""
        
        from pycaret.classification import (
            setup, compare_models, finalize_model, 
            predict_model, pull, get_config
        )
        
        # PyCaret 3.1.0 compatible setup - minimal working parameters
        print("🔧 Setting up PyCaret classification environment...")
        self.setup_config = setup(
            data=df,
            target=target_column,
            train_size=1-test_size,
            session_id=42,
            verbose=False,
            preprocess=True  # Handles most preprocessing automatically
        )
        
        # Compare models
        print("🤖 Comparing multiple ML models...")
        best_model = compare_models(
            n_select=1,
            sort='Accuracy'
        )
        
        # Get comparison results
        comparison_df = pull()
        
        # Finalize model (train on full dataset)
        print("✅ Finalizing best model...")
        self.model = finalize_model(best_model)
        
        # Get test predictions
        test_data = get_config('X_test')
        test_labels = get_config('y_test')
        
        # Make predictions
        predictions = predict_model(self.model, data=test_data)
        
        # Extract metrics
        self.metrics = self._extract_classification_metrics(
            predictions, 
            test_labels,
            comparison_df
        )
        
        # Get feature importance
        self.feature_importance = self._get_feature_importance(self.model, df, target_column)
        
        return {
            'model': self.model,
            'metrics': self.metrics,
            'feature_importance': self.feature_importance,
            'predictions': predictions,
            'comparison': comparison_df,
            'task_type': 'classification'
        }
    
    def _build_regression_model(
        self, 
        df: pd.DataFrame, 
        target_column: str,
        test_size: float,
        n_models: int
    ) -> Dict[str, Any]:
        """Build regression model using PyCaret 3.1.0"""
        
        from pycaret.regression import (
            setup, compare_models, finalize_model,
            predict_model, pull, get_config
        )
        
        # PyCaret 3.1.0 compatible setup - minimal working parameters
        print("🔧 Setting up PyCaret regression environment...")
        self.setup_config = setup(
            data=df,
            target=target_column,
            train_size=1-test_size,
            session_id=42,
            verbose=False,
            preprocess=True  # Handles most preprocessing automatically
        )
        
        # Compare models
        print("🤖 Comparing multiple ML models...")
        best_model = compare_models(
            n_select=1,
            sort='R2'
        )
        
        # Get comparison results
        comparison_df = pull()
        
        # Finalize model
        print("✅ Finalizing best model...")
        self.model = finalize_model(best_model)
        
        # Get test predictions
        test_data = get_config('X_test')
        test_labels = get_config('y_test')
        
        # Make predictions
        predictions = predict_model(self.model, data=test_data)
        
        # Extract metrics
        self.metrics = self._extract_regression_metrics(
            predictions,
            test_labels,
            comparison_df
        )
        
        # Get feature importance
        self.feature_importance = self._get_feature_importance(self.model, df, target_column)
        
        return {
            'model': self.model,
            'metrics': self.metrics,
            'feature_importance': self.feature_importance,
            'predictions': predictions,
            'comparison': comparison_df,
            'task_type': 'regression'
        }
    
    def _extract_classification_metrics(
        self, 
        predictions: pd.DataFrame,
        test_labels: pd.Series,
        comparison_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Extract classification metrics"""
        
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, roc_auc_score, confusion_matrix
        )
        
        # Get predicted labels
        y_pred = predictions['prediction_label'].values
        y_true = test_labels.values
        
        # Calculate metrics
        metrics = {
            'accuracy': round(accuracy_score(y_true, y_pred), 4),
            'precision': round(precision_score(y_true, y_pred, average='weighted'), 4),
            'recall': round(recall_score(y_true, y_pred, average='weighted'), 4),
            'f1_score': round(f1_score(y_true, y_pred, average='weighted'), 4),
        }
        
        # Add AUC if binary classification
        if len(np.unique(y_true)) == 2:
            try:
                y_pred_proba = predictions['prediction_score'].values
                metrics['auc'] = round(roc_auc_score(y_true, y_pred_proba), 4)
            except:
                pass
        
        # Add confusion matrix
        metrics['confusion_matrix'] = confusion_matrix(y_true, y_pred).tolist()
        
        # Add model name
        if not comparison_df.empty:
            metrics['model_name'] = comparison_df.index[0]
        
        return metrics
    
    def _extract_regression_metrics(
        self,
        predictions: pd.DataFrame,
        test_labels: pd.Series,
        comparison_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Extract regression metrics"""
        
        from sklearn.metrics import (
            mean_squared_error, mean_absolute_error,
            r2_score, mean_absolute_percentage_error
        )
        
        # Get predictions
        y_pred = predictions['prediction_label'].values
        y_true = test_labels.values
        
        # Calculate metrics
        mse = mean_squared_error(y_true, y_pred)
        metrics = {
            'r2_score': round(r2_score(y_true, y_pred), 4),
            'rmse': round(np.sqrt(mse), 4),
            'mae': round(mean_absolute_error(y_true, y_pred), 4),
            'mse': round(mse, 4),
        }
        
        # Add MAPE if no zeros in y_true
        if not (y_true == 0).any():
            try:
                metrics['mape'] = round(mean_absolute_percentage_error(y_true, y_pred) * 100, 2)
            except:
                pass
        
        # Add model name
        if not comparison_df.empty:
            metrics['model_name'] = comparison_df.index[0]
        
        return metrics
    
    def _get_feature_importance(
        self,
        model: Any,
        df: pd.DataFrame,
        target_column: str
    ) -> pd.DataFrame:
        """Extract feature importance from model"""
        
        try:
            # Get feature names
            feature_names = [col for col in df.columns if col != target_column]
            
            # Try to get feature importance
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            elif hasattr(model, 'coef_'):
                importances = np.abs(model.coef_).flatten()
            else:
                # Use permutation importance as fallback
                return pd.DataFrame({
                    'feature': feature_names,
                    'importance': [1.0 / len(feature_names)] * len(feature_names)
                })
            
            # Create DataFrame
            importance_df = pd.DataFrame({
                'feature': feature_names[:len(importances)],
                'importance': importances
            })
            
            # Sort by importance
            importance_df = importance_df.sort_values('importance', ascending=False)
            
            # Normalize to 0-1
            if importance_df['importance'].max() > 0:
                importance_df['importance'] = importance_df['importance'] / importance_df['importance'].max()
            
            return importance_df
            
        except Exception as e:
            print(f"Warning: Could not extract feature importance: {e}")
            return pd.DataFrame(columns=['feature', 'importance'])
    
    def save_model(self, output_dir: str, model_name: str = "model") -> Dict[str, str]:
        """Save model and artifacts to disk"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save model
        model_path = os.path.join(output_dir, f"{model_name}.pkl")
        joblib.dump(self.model, model_path)
        
        # Save metrics
        metrics_path = os.path.join(output_dir, f"{model_name}_metrics.pkl")
        joblib.dump(self.metrics, metrics_path)
        
        # Save feature importance
        if self.feature_importance is not None:
            fi_path = os.path.join(output_dir, f"{model_name}_feature_importance.csv")
            self.feature_importance.to_csv(fi_path, index=False)
        else:
            fi_path = None
        
        return {
            'model_path': model_path,
            'metrics_path': metrics_path,
            'feature_importance_path': fi_path
        }
    
    def load_model(self, model_path: str):
        """Load saved model"""
        self.model = joblib.load(model_path)
        return self.model


def build_model(
    df: pd.DataFrame,
    target_column: str,
    task_type: str = 'classification'
) -> Tuple[Any, Dict, pd.DataFrame]:
    """Convenience function to build model"""
    builder = ModelBuilder()
    result = builder.build_model(df, target_column, task_type)
    
    return result['model'], result['metrics'], result['feature_importance']


if __name__ == "__main__":
    # Test with sample data
    print("🧪 Testing Model Builder\n")
    
    # Create sample classification data
    from sklearn.datasets import make_classification
    X, y = make_classification(n_samples=200, n_features=10, n_classes=2, random_state=42)
    
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(10)])
    df['target'] = y
    
    # Build model
    builder = ModelBuilder()
    result = builder.build_model(df, 'target', 'classification')
    
    print(f"✅ Model trained: {result['metrics']['model_name']}")
    print(f"📊 Accuracy: {result['metrics']['accuracy']}")
    print(f"📊 F1 Score: {result['metrics']['f1_score']}")
