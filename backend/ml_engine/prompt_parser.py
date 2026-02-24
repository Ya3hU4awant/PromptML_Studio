import streamlit as st

class PromptParser:
    def __init__(self):
        self.classification_keywords = [
            'classify', 'category', 'class', 'predict if', 'churn', 
            'spam', 'fraud', 'sentiment', 'risk', 'disease', 
            'type', 'binary', 'predict whether', 'detect', 'identify'
        ]
        self.regression_keywords = [
            'predict price', 'forecast', 'sales', 'revenue', 'value', 'amount', 
            'cost', 'how much', 'how many', 'predict value', 'estimate'
        ]
        self.clustering_keywords = [
            'cluster', 'group', 'segment', 'segmentation', 'anomalies', 
            'patterns', 'find groups'
        ]

    def detect_task_type(self, prompt: str):
        prompt_lower = prompt.lower()
        
        class_score = sum(1 for kw in self.classification_keywords if kw in prompt_lower)
        reg_score = sum(1 for kw in self.regression_keywords if kw in prompt_lower)
        clust_score = sum(1 for kw in self.clustering_keywords if kw in prompt_lower)

        scores = {
            "classification": class_score,
            "regression": reg_score,
            "clustering": clust_score
        }

        best_task = max(scores, key=scores.get)
        
        if scores[best_task] == 0:
            return "classification", 0.6
        
        confidence = min(0.6 + (scores[best_task] * 0.15), 0.95)
        return best_task, confidence

    def detect_target_column(self, prompt: str, df):
        """
        Detect target column using lightweight heuristic.
        """
        prompt_lower = prompt.lower()
        
        # Exact match
        for col in df.columns:
            if col.lower() in prompt_lower:
                return col
                
        # Word overlap match
        prompt_words = set(prompt_lower.replace(',', '').replace('.', '').replace('?', '').split())
        for col in df.columns:
            col_words = set(col.lower().replace('_', ' ').split())
            if prompt_words.intersection(col_words):
                return col
                
        # Intelligent fallback for target column
        return df.columns[-1]

    def parse_prompt(self, prompt: str, df):
        task_type, confidence = self.detect_task_type(prompt)

        if task_type in ["classification", "regression"]:
            target_column = self.detect_target_column(prompt, df)
        else:
            target_column = None

        return {
            "task_type": task_type,
            "target_column": target_column,
            "confidence": confidence
        }
