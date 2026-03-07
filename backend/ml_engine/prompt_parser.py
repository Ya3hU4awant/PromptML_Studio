# backend/ml_engine/prompt_parser.py

class PromptParser:
    """
    Lightweight, data-aware prompt parser.
    Detects:
    - classification
    - regression
    - clustering

    Uses:
    - keyword scoring
    - dataset statistics
    - intelligent fallback
    """

    def __init__(self):
        self.classification_keywords = [
            'classify', 'category', 'class', 'predict if', 'churn',
            'spam', 'fraud', 'sentiment', 'risk', 'disease',
            'type', 'binary', 'predict whether', 'detect', 'identify',
            'yes or no'
        ]

        self.regression_keywords = [
            'predict', 'forecast', 'sales', 'revenue', 'value',
            'amount', 'cost', 'how much', 'how many',
            'estimate', 'price', 'salary', 'income'
        ]

        self.clustering_keywords = [
            'cluster', 'group', 'segment', 'segmentation',
            'patterns', 'anomalies', 'unsupervised'
        ]

    # --------------------------------------------------
    # TASK TYPE DETECTION
    # --------------------------------------------------

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
            # Default to regression if prediction-like wording
            if "predict" in prompt_lower:
                return "regression", 0.7
            return "classification", 0.6

        confidence = min(0.65 + scores[best_task] * 0.1, 0.95)
        return best_task, confidence

    # --------------------------------------------------
    # TARGET COLUMN DETECTION
    # --------------------------------------------------

    def detect_target_column(self, prompt: str, df):
        prompt_lower = prompt.lower()

        # Exact column name match
        for col in df.columns:
            if col.lower() in prompt_lower:
                return col

        # Word overlap match
        prompt_words = set(prompt_lower.replace(',', '').replace('.', '').split())

        for col in df.columns:
            col_words = set(col.lower().replace('_', ' ').split())
            if prompt_words.intersection(col_words):
                return col

        # Fallback: last column (common ML convention)
        return df.columns[-1]

    # --------------------------------------------------
    # DATA-DRIVEN TASK OVERRIDE
    # --------------------------------------------------

    def override_with_data_logic(self, task_type, target_column, df):
        """
        Override task type using dataset statistics.
        THIS FIXES house-price classification bug.
        """

        if target_column is None or target_column not in df.columns:
            return task_type, 0.6

        column = df[target_column]

        # Clustering has no target
        if task_type == "clustering":
            return "clustering", 0.95

        # If numeric column
        if column.dtype in ['int64', 'float64']:

            unique_ratio = column.nunique() / len(column)

            # If many unique values → regression
            if column.nunique() > 20 or unique_ratio > 0.05:
                return "regression", 0.95
            else:
                return "classification", 0.85

        # If categorical/object
        else:
            return "classification", 0.95

    # --------------------------------------------------
    # MAIN PARSE FUNCTION
    # --------------------------------------------------

    def parse_prompt(self, prompt: str, df):
        task_type, confidence = self.detect_task_type(prompt)
        prompt_lower = prompt.lower()

        # Count explicit classification vs regression keyword hits
        class_hits = sum(1 for kw in self.classification_keywords if kw in prompt_lower)
        reg_hits   = sum(1 for kw in self.regression_keywords   if kw in prompt_lower)

        # User explicitly said "classify/class/detect" etc — trust the prompt
        # Only use data override when prompt is ambiguous (equal or zero scores)
        prompt_is_explicit = class_hits != reg_hits

        if task_type in ["classification", "regression"]:
            target_column = self.detect_target_column(prompt, df)
        else:
            target_column = None

        if prompt_is_explicit:
            # Prompt wins — just validate target column with data
            data_task, data_conf = self.override_with_data_logic(
                task_type, target_column, df
            )
            # If data strongly disagrees AND target column was auto-detected
            # (no column name in prompt), pick the best target for the task
            if data_task != task_type:
                target_column = self._best_target_for_task(task_type, df)
            final_confidence = confidence
        else:
            # Ambiguous prompt — let data decide
            task_type, data_conf = self.override_with_data_logic(
                task_type, target_column, df
            )
            final_confidence = max(confidence, data_conf)

        return {
            "task_type": task_type,
            "target_column": target_column,
            "confidence": round(final_confidence, 2)
        }

    # --------------------------------------------------
    # BEST TARGET COLUMN FOR TASK TYPE
    # --------------------------------------------------

    def _best_target_for_task(self, task_type, df):
        """
        When prompt specifies task but target is ambiguous,
        pick the most suitable column from the dataset.
        Classification → last column with few unique values
        Regression     → last numeric column with many unique values
        """
        if task_type == "classification":
            # Prefer columns with 2-20 unique values (class labels)
            for col in reversed(df.columns):
                u = df[col].nunique()
                if 2 <= u <= 20:
                    return col
        elif task_type == "regression":
            # Prefer numeric columns with many unique values
            for col in reversed(df.columns):
                if df[col].dtype in ["int64", "float64"] and df[col].nunique() > 20:
                    return col
        # Fallback to last column
        return df.columns[-1]