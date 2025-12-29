"""
PromptML Studio - Prompt Parser Module
Uses NLP to parse natural language prompts and detect ML task type
"""

import re
from typing import Dict, List, Optional
import pandas as pd


class PromptParser:
    """
    Parses natural language prompts to detect:
    - Task type (regression, classification, clustering)
    - Target column
    - Feature preferences
    """
    
    # Keywords for task detection
    REGRESSION_KEYWORDS = [
        'predict', 'forecast', 'estimate', 'price', 'sales', 'revenue',
        'cost', 'value', 'amount', 'score', 'rating', 'temperature',
        'age', 'salary', 'income', 'profit', 'loss', 'demand'
    ]
    
    CLASSIFICATION_KEYWORDS = [
        'classify', 'categorize', 'identify', 'detect', 'recognize',
        'churn', 'fraud', 'spam', 'sentiment', 'disease', 'diagnosis',
        'risk', 'default', 'approval', 'rejection', 'type', 'class',
        'category', 'label', 'group'
    ]
    
    CLUSTERING_KEYWORDS = [
        'cluster', 'segment', 'group', 'similar', 'pattern',
        'anomaly', 'outlier'
    ]
    
    def __init__(self):
        self.task_type = None
        self.target_column = None
        self.confidence = 0.0
    
    def parse_prompt(self, prompt: str, df: pd.DataFrame = None) -> Dict:
        """
        Parse natural language prompt to extract ML task information
        
        Args:
            prompt: User's natural language description
            df: Optional DataFrame to help identify target column
            
        Returns:
            Dictionary with task_type, target_column, and confidence
        """
        prompt_lower = prompt.lower()
        
        # Detect task type
        task_type = self._detect_task_type(prompt_lower)
        
        # Detect target column
        target_column = self._detect_target_column(prompt_lower, df)
        
        # Calculate confidence
        confidence = self._calculate_confidence(prompt_lower, task_type)
        
        return {
            'task_type': task_type,
            'target_column': target_column,
            'confidence': confidence,
            'original_prompt': prompt
        }
    
    def _detect_task_type(self, prompt: str) -> str:
        """
        Detect whether task is regression, classification, or clustering
        """
        regression_score = sum(1 for kw in self.REGRESSION_KEYWORDS if kw in prompt)
        classification_score = sum(1 for kw in self.CLASSIFICATION_KEYWORDS if kw in prompt)
        clustering_score = sum(1 for kw in self.CLUSTERING_KEYWORDS if kw in prompt)
        
        scores = {
            'regression': regression_score,
            'classification': classification_score,
            'clustering': clustering_score
        }
        
        # Return task with highest score
        task_type = max(scores, key=scores.get)
        
        # Default to classification if no clear winner
        if scores[task_type] == 0:
            task_type = 'classification'
        
        return task_type
    
    def _detect_target_column(self, prompt: str, df: pd.DataFrame = None) -> Optional[str]:
        """
        Try to identify the target column from prompt and DataFrame
        """
        if df is None:
            return None
        
        # Common target column names
        common_targets = {
            'regression': ['price', 'sales', 'revenue', 'cost', 'value', 'amount', 
                          'score', 'rating', 'salary', 'income', 'target'],
            'classification': ['churn', 'fraud', 'spam', 'label', 'class', 
                             'category', 'type', 'status', 'target', 'outcome']
        }
        
        # Get task type
        task_type = self._detect_task_type(prompt)
        
        # Check if any column name appears in prompt
        for col in df.columns:
            if col.lower() in prompt:
                return col
        
        # Check for common target names
        for target_name in common_targets.get(task_type, []):
            for col in df.columns:
                if target_name in col.lower():
                    return col
        
        # Check for columns with specific characteristics
        if task_type == 'classification':
            # Look for categorical columns with few unique values
            for col in df.columns:
                if df[col].dtype == 'object' or df[col].nunique() < 20:
                    return col
        
        elif task_type == 'regression':
            # Look for numeric columns
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if len(numeric_cols) > 0:
                # Return last numeric column (common convention)
                return numeric_cols[-1]
        
        # Default: return last column
        return df.columns[-1]
    
    def _calculate_confidence(self, prompt: str, task_type: str) -> float:
        """
        Calculate confidence score for task detection
        """
        if task_type == 'regression':
            keywords = self.REGRESSION_KEYWORDS
        elif task_type == 'classification':
            keywords = self.CLASSIFICATION_KEYWORDS
        else:
            keywords = self.CLUSTERING_KEYWORDS
        
        # Count matching keywords
        matches = sum(1 for kw in keywords if kw in prompt)
        
        # Calculate confidence (0-1 scale)
        confidence = min(matches / 3.0, 1.0)  # Cap at 1.0
        
        return round(confidence, 2)
    
    def suggest_features(self, df: pd.DataFrame, target_column: str) -> List[str]:
        """
        Suggest relevant features for modeling
        
        Args:
            df: Input DataFrame
            target_column: Target column name
            
        Returns:
            List of suggested feature columns
        """
        # Exclude target column
        features = [col for col in df.columns if col != target_column]
        
        # Remove ID-like columns
        features = [col for col in features if not self._is_id_column(col, df)]
        
        return features
    
    def _is_id_column(self, column: str, df: pd.DataFrame) -> bool:
        """
        Check if column is likely an ID column
        """
        id_patterns = ['id', 'index', 'key', 'uuid', 'guid']
        
        # Check column name
        if any(pattern in column.lower() for pattern in id_patterns):
            return True
        
        # Check if all values are unique (likely an ID)
        if df[column].nunique() == len(df):
            return True
        
        return False


def parse_prompt(prompt: str, df: pd.DataFrame = None) -> Dict:
    """
    Convenience function to parse prompt
    
    Args:
        prompt: Natural language description of ML task
        df: Optional DataFrame to help identify target column
        
    Returns:
        Dictionary with task information
        
    Example:
        >>> result = parse_prompt("Predict house prices based on features")
        >>> print(result['task_type'])  # 'regression'
    """
    parser = PromptParser()
    return parser.parse_prompt(prompt, df)


if __name__ == "__main__":
    # Test the parser
    test_prompts = [
        "Predict house prices based on location and size",
        "Classify customer churn risk",
        "Forecast sales for next quarter",
        "Detect fraudulent transactions",
        "Estimate employee salary based on experience"
    ]
    
    print("🧪 Testing Prompt Parser\n")
    for prompt in test_prompts:
        result = parse_prompt(prompt)
        print(f"Prompt: {prompt}")
        print(f"Task Type: {result['task_type']}")
        print(f"Confidence: {result['confidence']}")
        print("-" * 60)
