from transformers import pipeline
import streamlit as st

@st.cache_resource
def load_zero_shot():
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )

class PromptParser:

    def __init__(self):
        # Load zero-shot classifier once
        self.classifier = load_zero_shot()

        self.task_labels = [
            "classification",
            "regression",
            "clustering"
        ]

    def detect_task_type(self, prompt: str):
        result = self.classifier(prompt, self.task_labels)
        return result["labels"][0]

    def detect_target_column(self, prompt: str, df):
        """
        Try to find mentioned column in prompt.
        If not found, guess intelligently.
        """
        prompt_lower = prompt.lower()

        for col in df.columns:
            if col.lower() in prompt_lower:
                return col

        # fallback: last column (common ML pattern)
        return df.columns[-1]

    def parse_prompt(self, prompt: str, df):
        task_type = self.detect_task_type(prompt)

        if task_type in ["classification", "regression"]:
            target_column = self.detect_target_column(prompt, df)
        else:
            target_column = None

        return {
            "task_type": task_type,
            "target_column": target_column,
            "confidence": 0.9
        }
