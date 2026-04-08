"""
PromptML Studio - Model Builder Module
PyCaret 3.1.0 Fully Compatible - Production Ready
Supports:
- Classification
- Regression
- Clustering
"""
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import pandas as pd
import numpy as np
from typing import Dict, Any
import joblib
import warnings
warnings.filterwarnings("ignore")


class ModelBuilder:

    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.task_type = None
        self.metrics = {}
        self.feature_importance = None
        self.setup_config = None

    # ============================================================
    # MAIN ENTRY
    # ============================================================

    def build_model(
        self,
        df,
        target_column=None,
        task_type="classification",
        test_size=0.2,
        n_models=10
    ):
        self.task_type = task_type

        last_error = None
        for attempt in range(3):  # retry up to 3 times
            try:
                # Clear PyCaret global state before each attempt
                self._reset_pycaret(task_type)

                if task_type == "classification":
                    return self._build_classification_model(df, target_column, test_size)
                elif task_type == "regression":
                    return self._build_regression_model(df, target_column, test_size)
                elif task_type == "clustering":
                    return self._build_clustering_model(df)
                else:
                    raise ValueError(f"Unsupported task type: {task_type}")

            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed: {str(e)} — retrying...")
                continue

        raise Exception(f"Model building failed after 3 attempts: {str(last_error)}")

    def _reset_pycaret(self, task_type):
        """Clear PyCaret global state to prevent setup() conflicts"""
        try:
            if task_type == "classification":
                from pycaret.classification import ClassificationExperiment
                exp = ClassificationExperiment()
                exp._ml_usecase = None
            elif task_type == "regression":
                from pycaret.regression import RegressionExperiment
                exp = RegressionExperiment()
                exp._ml_usecase = None
        except Exception:
            pass  # if reset fails, just continue

    # ============================================================
    # CLASSIFICATION
    # ============================================================

    def _build_classification_model(self, df, target_column, test_size):

        from pycaret.classification import (
            setup,
            compare_models,
            finalize_model,
            predict_model,
            pull,
            get_config,
        )

        # Force clear any existing PyCaret session
        try:
            from pycaret.classification import ClassificationExperiment
            _exp = ClassificationExperiment()
        except Exception:
            pass
        
        # 1. Sample large datasets
        if len(df) > 5000:
            df = df.sample(n=5000, random_state=42)

        self.setup_config = setup(
            data=df,
            target=target_column,
            train_size=0.8,
            session_id=42,
            verbose=False,
            n_jobs=1,
            preprocess=True,
        )

        best_model = compare_models(
            n_select=1,
            sort="Accuracy",
            fold=3,
            exclude=["svm", "mlp", "gbc"],
            budget_time=1.0
        )

        comparison_df = pull()

        self.model = finalize_model(best_model)

        # ================= SAVE ARTIFACTS =================
        self._save_artifacts(
            model=self.model,
            feature_columns=[col for col in df.columns if col != target_column],
            task_type="classification",
        )

        test_data = get_config("X_test")
        test_labels = get_config("y_test")
        predictions = predict_model(self.model, data=test_data)

        self.metrics = self._extract_classification_metrics(
            predictions, test_labels, comparison_df
        )

        self.feature_importance = self._get_feature_importance(
            self.model, df, target_column
        )

        return {
            "model": self.model,
            "metrics": self.metrics,
            "feature_importance": self.feature_importance,
            "predictions": predictions,
            "comparison": comparison_df,
            "task_type": "classification",
        }

    # ============================================================
    # REGRESSION
    # ============================================================

    def _build_regression_model(self, df, target_column, test_size):

        from pycaret.regression import (
            setup,
            compare_models,
            finalize_model,
            predict_model,
            pull,
            get_config,
        )

        # Force clear any existing PyCaret session
        try:
            from pycaret.regression import RegressionExperiment
            _exp = RegressionExperiment()
        except Exception:
            pass

        # 1. Sample large datasets
        if len(df) > 5000:
            df = df.sample(n=5000, random_state=42)

        self.setup_config = setup(
            data=df,
            target=target_column,
            train_size=0.8,
            session_id=42,
            verbose=False,
            n_jobs=1,
            preprocess=True,
        )

        best_model = compare_models(
            n_select=1,
            sort="R2",
            fold=3,
            exclude=["svm", "mlp", "gbr"],
            budget_time=1.0
        )


        comparison_df = pull()

        self.model = finalize_model(best_model) 

        # ================= SAVE ARTIFACTS =================
        self._save_artifacts(
            model=self.model,
            feature_columns=[col for col in df.columns if col != target_column],
            task_type="regression",
        )

        test_data = get_config("X_test")
        test_labels = get_config("y_test")
        predictions = predict_model(self.model, data=test_data)

        self.metrics = self._extract_regression_metrics(
            predictions, test_labels, comparison_df
        )

        self.feature_importance = self._get_feature_importance(
            self.model, df, target_column
        )

        return {
            "model": self.model,
            "metrics": self.metrics,
            "feature_importance": self.feature_importance,
            "predictions": predictions,
            "comparison": comparison_df,
            "task_type": "regression",
        }

    # ============================================================
    # CLUSTERING
    # ============================================================

    def _build_clustering_model(self, df):

        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import silhouette_score
        from sklearn.decomposition import PCA

        X = df.select_dtypes(include=["int64", "float64"])

        if X.shape[1] < 2:
            raise ValueError("Clustering requires at least 2 numeric features")

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        k = min(5, max(2, len(X_scaled) // 10))
        model = KMeans(n_clusters=k, random_state=42)
        clusters = model.fit_predict(X_scaled)

        score = silhouette_score(X_scaled, clusters)

        self.model = model
        self.preprocessor = scaler

        # Save artifacts
        self._save_artifacts(
            model=model,
            feature_columns=list(X.columns),
            task_type="clustering",
            scaler=scaler,
        )

        df_with_clusters = df.copy()
        df_with_clusters["cluster"] = clusters

        pca = PCA(n_components=2)
        components = pca.fit_transform(X_scaled)

        viz_df = df_with_clusters.copy()
        viz_df["pca_1"] = components[:, 0]
        viz_df["pca_2"] = components[:, 1]

        self.metrics = {
            "n_clusters": k,
            "algorithm": "KMeans",
            "silhouette_score": round(score, 4),
        }

        return {
            "model": model,
            "metrics": self.metrics,
            "predictions": viz_df,  # Use viz_df to include PCA columns for ReportGenerator
            "viz_data": viz_df,
            "task_type": "clustering",
            "comparison": pd.DataFrame(),  # Added to prevent KeyError in app.py
            "feature_importance": pd.DataFrame()  # Added to prevent KeyError in app.py
        }

    # ============================================================
    # ARTIFACT SAVER
    # ============================================================

    def _save_artifacts(self, model, feature_columns, task_type, scaler=None):

        os.makedirs("artifacts", exist_ok=True)

        joblib.dump(model, "artifacts/model.pkl")
        joblib.dump(feature_columns, "artifacts/features.pkl")
        joblib.dump(task_type, "artifacts/task_type.pkl")

        if scaler:
            joblib.dump(scaler, "artifacts/scaler.pkl")

    # ============================================================
    # METRICS
    # ============================================================

    def _extract_classification_metrics(self, predictions, test_labels, comparison_df):

        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
        )

        y_pred = predictions["prediction_label"].values
        y_true = test_labels.values

        metrics = {
            "accuracy": round(accuracy_score(y_true, y_pred), 4),
            "precision": round(precision_score(y_true, y_pred, average="weighted"), 4),
            "recall": round(recall_score(y_true, y_pred, average="weighted"), 4),
            "f1_score": round(f1_score(y_true, y_pred, average="weighted"), 4),
        }

        if not comparison_df.empty:
            metrics["model_name"] = comparison_df.index[0]

        return metrics

    def _extract_regression_metrics(self, predictions, test_labels, comparison_df):

        from sklearn.metrics import (
            mean_squared_error,
            mean_absolute_error,
            r2_score,
        )

        y_pred = predictions["prediction_label"].values
        y_true = test_labels.values

        mse = mean_squared_error(y_true, y_pred)

        metrics = {
            "r2_score": round(r2_score(y_true, y_pred), 4),
            "rmse": round(np.sqrt(mse), 4),
            "mae": round(mean_absolute_error(y_true, y_pred), 4),
        }

        if not comparison_df.empty:
            metrics["model_name"] = comparison_df.index[0]

        return metrics

    # ============================================================
    # FEATURE IMPORTANCE (PIPELINE SAFE)
    # ============================================================

    def _get_feature_importance(self, model, df, target_column):

        try:
            feature_names = [col for col in df.columns if col != target_column]

            # Handle PyCaret pipeline
            if hasattr(model, "named_steps"):
                for step in model.named_steps.values():
                    if hasattr(step, "feature_importances_"):
                        model = step
                        break

            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_

            elif hasattr(model, "coef_"):
                importances = np.abs(model.coef_).flatten()

            else:
                return pd.DataFrame({
                    "feature": feature_names,
                    "importance": [1 / len(feature_names)] * len(feature_names),
                })

            importance_df = pd.DataFrame({
                "feature": feature_names[: len(importances)],
                "importance": importances,
            }).sort_values("importance", ascending=False)

            return importance_df

        except:
            return pd.DataFrame(columns=["feature", "importance"])
