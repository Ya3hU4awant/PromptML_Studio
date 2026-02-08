# backend/ml_engine/prompt_parser.py

from transformers import pipeline

class PromptParser:
    """
    Offline prompt parser using Hugging Face FLAN-T5.
    Supports:
    - classification
    - regression
    - clustering
    """

    def __init__(self):
        self.parser = pipeline(
            "text2text-generation",
            model="google/flan-t5-base"
        )

    def parse_prompt(self, prompt: str, df):
        columns = list(df.columns)

        instruction = f"""
You are an AI that extracts machine learning intent.

Dataset columns:
{columns}

User request:
"{prompt}"

Return output strictly in this format:
task_type: classification OR regression OR clustering
target_column: <column name OR NONE>
"""

        try:
            output = self.parser(
                instruction,
                max_length=64,
                clean_up_tokenization_spaces=True
            )[0]["generated_text"]

            task_type = self._extract_task_type(output)
            target_column = self._extract_target_column(output, columns)

            # Clustering has NO target
            if task_type == "clustering":
                target_column = None

            confidence = 0.9 if task_type else 0.5

        except Exception:
            task_type, target_column = self._fallback_logic(prompt, columns)
            confidence = 0.6

        return {
            "task_type": task_type,
            "target_column": target_column,
            "confidence": confidence
        }

    # ---------------- HELPERS ---------------- #

    def _extract_task_type(self, text):
        text = text.lower()

        if "clustering" in text:
            return "clustering"
        if "classification" in text:
            return "classification"
        if "regression" in text:
            return "regression"

        return None

    def _extract_target_column(self, text, columns):
        for col in columns:
            if col.lower() in text.lower():
                return col
        return None

    def _fallback_logic(self, prompt, columns):
        prompt = prompt.lower()

        # 🔹 CLUSTERING
        if any(word in prompt for word in [
            "cluster", "group", "segment", "segmentation",
            "unlabeled", "unsupervised", "find patterns"
        ]):
            return "clustering", None

        # 🔹 CLASSIFICATION
        if any(word in prompt for word in [
            "classify", "fraud", "churn", "yes/no", "category", "risk"
        ]):
            for col in columns:
                if col.lower() in prompt:
                    return "classification", col
            return "classification", columns[-1]

        # 🔹 REGRESSION (default)
        for col in columns:
            if col.lower() in prompt:
                return "regression", col

        return "regression", columns[-1]
