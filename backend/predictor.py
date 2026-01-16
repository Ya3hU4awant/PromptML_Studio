"""
PromptML Studio - Predictor Module
Handles predictions on new data using trained models
"""

import pandas as pd
import numpy as np
import joblib
from typing import Union, Dict, Any
import os


class Predictor:
    """
    Makes predictions using trained ML models
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize predictor
        
        Args:
            model_path: Path to saved model file
        """
        self.model = None
        self.task_type = None
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """
        Load trained model from disk
        
        Args:
            model_path: Path to model file (.pkl)
        """
        try:
            self.model = joblib.load(model_path)
            print(f"✅ Model loaded from {model_path}")
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    
    def predict(
        self,
        data: Union[pd.DataFrame, dict, list],
        return_proba: bool = False
    ) -> pd.DataFrame:
        """
        Make predictions on new data
        
        Args:
            data: Input data (DataFrame, dict, or list)
            return_proba: Whether to return prediction probabilities
            
        Returns:
            DataFrame with predictions
        """
        if self.model is None:
            raise ValueError("No model loaded. Call load_model() first.")
        """
        # Convert input to DataFrame
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ValueError("Data must be DataFrame, dict, or list")
        """
        # Convert input to DataFrame
        if isinstance(data, dict):
           df = pd.DataFrame([data])
        elif isinstance(data, list):
           df = pd.DataFrame(data)
        else:
           df = data.copy()

        # ================= IRIS DATA FIX =================

        # Drop target column if present
        if 'Species' in df.columns:
           df = df.drop(columns=['Species'])

        # Ensure correct feature order (as used in training)
        expected_cols = [
        'Id',
        'SepalLengthCm',
        'SepalWidthCm',
        'PetalLengthCm',
        'PetalWidthCm'
]

       # Keep only required columns in correct order
       df = df[expected_cols]

       # =================================================


        # Make predictions using PyCaret
        try:
            # Try PyCaret prediction first
            from pycaret.classification import predict_model as predict_clf
            from pycaret.regression import predict_model as predict_reg
            
            # Detect task type
            if hasattr(self.model, 'predict_proba'):
                # Classification
                predictions = predict_clf(self.model, data=df)
            else:
                # Regression
                predictions = predict_reg(self.model, data=df)
            
            return predictions
            
        except Exception as e:
            # Fallback to sklearn prediction
            print(f"PyCaret prediction failed, using sklearn: {e}")
            return self._sklearn_predict(df, return_proba)
    
    def _sklearn_predict(self, df: pd.DataFrame, return_proba: bool = False) -> pd.DataFrame:
        """
        Fallback prediction using sklearn
        
        Args:
            df: Input DataFrame
            return_proba: Whether to return probabilities
            
        Returns:
            DataFrame with predictions
        """
        result_df = df.copy()
        
        # Make predictions
        predictions = self.model.predict(df)
        result_df['prediction'] = predictions
        
        # Add probabilities for classification
        if return_proba and hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(df)
            
            # Add probability columns
            for i in range(probabilities.shape[1]):
                result_df[f'probability_class_{i}'] = probabilities[:, i]
        
        return result_df
    
    def predict_single(self, data: dict) -> Dict[str, Any]:
        """
        Make prediction for a single instance
        
        Args:
            data: Dictionary with feature values
            
        Returns:
            Dictionary with prediction and metadata
        """
        df = pd.DataFrame([data])
        predictions = self.predict(df, return_proba=True)
        
        result = {
            'prediction': predictions['prediction_label'].values[0] if 'prediction_label' in predictions.columns else predictions['prediction'].values[0],
            'input_data': data
        }
        
        # Add probabilities if available
        if 'prediction_score' in predictions.columns:
            result['probability'] = predictions['prediction_score'].values[0]
        
        return result
    
    def batch_predict(self, csv_path: str, output_path: str = None) -> pd.DataFrame:
        """
        Make predictions on a CSV file
        
        Args:
            csv_path: Path to input CSV
            output_path: Optional path to save predictions
            
        Returns:
            DataFrame with predictions
        """
        # Load data
        df = pd.read_csv(csv_path)
        
        # Make predictions
        predictions = self.predict(df)
        
        # Save if output path provided
        if output_path:
            predictions.to_csv(output_path, index=False)
            print(f"✅ Predictions saved to {output_path}")
        
        return predictions


def predict_from_model(
    model_path: str,
    data: Union[pd.DataFrame, dict, str]
) -> pd.DataFrame:
    """
    Convenience function to make predictions
    
    Args:
        model_path: Path to saved model
        data: Input data (DataFrame, dict, or CSV path)
        
    Returns:
        DataFrame with predictions
        
    Example:
        >>> predictions = predict_from_model('model.pkl', 'new_data.csv')
    """
    predictor = Predictor(model_path)
    
    if isinstance(data, str) and data.endswith('.csv'):
        return predictor.batch_predict(data)
    else:
        return predictor.predict(data)


if __name__ == "__main__":
    # Test predictor
    print("🧪 Testing Predictor\n")
    
    # Create sample data
    sample_data = {
        'feature_0': 1.5,
        'feature_1': 2.3,
        'feature_2': -0.5,
        'feature_3': 0.8,
        'feature_4': 1.2
    }
    
    print("Sample prediction test:")
    print(f"Input: {sample_data}")
    print("\n⚠️  Note: Actual prediction requires a trained model file")
