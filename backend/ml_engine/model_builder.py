"""
PromptML Studio - Model Builder
Optimised for Streamlit Cloud + Render Free Tier
- Uses include= to prevent OOM/Broken Pipe
- Removes nb (Naive Bayes) — overfits tiny datasets → fake 100% scores
- Adds knn, svm_rbf alternatives that are still memory-safe
- Overfitting detection with warning flag in metrics
- Adaptive train/test split for small datasets
- Auto-clean missing target values
"""
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import gc
import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings("ignore")


# ── Model pools ──────────────────────────────────────────────────
# nb (Naive Bayes) REMOVED — memorizes tiny datasets → always 100%
# knn added — good on small data without memorizing
# ada added — light boosting, good quality
#
# Classification: 8 models, all memory-safe
CLASSIFICATION_INCLUDE = ["lr", "dt", "rf", "et", "ridge", "lda", "knn", "ada"]

# Regression: 8 models, all memory-safe
REGRESSION_INCLUDE = ["lr", "dt", "rf", "et", "ridge", "lasso", "en", "knn"]


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

    def build_model(self, df, target_column=None, task_type="classification",
                    test_size=0.2, n_models=10):
        self.task_type = task_type
        last_error = None

        for attempt in range(3):
            try:
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
                print(f"[WARN] Attempt {attempt + 1} failed: {str(e)}")
                gc.collect()
                continue

        raise Exception(f"Model building failed after 3 attempts: {str(last_error)}")

    def _reset_pycaret(self, task_type):
        try:
            if task_type == "classification":
                from pycaret.classification import ClassificationExperiment
                ClassificationExperiment()
            elif task_type == "regression":
                from pycaret.regression import RegressionExperiment
                RegressionExperiment()
        except Exception:
            pass

    # ============================================================
    # SHARED DATA PREP
    # ============================================================

    def _prepare_df(self, df, target_column):
        """Sample + clean target NaNs + free memory before training."""
        if len(df) > 5000:
            df = df.sample(n=5000, random_state=42)

        original_count = len(df)
        df = df.dropna(subset=[target_column])
        dropped = original_count - len(df)
        if dropped > 0:
            print(f"[INFO] Dropped {dropped} rows with missing target values in '{target_column}'")
        if len(df) < 10:
            raise Exception(
                f"Only {len(df)} rows remain after removing missing target values. "
                "Please provide a cleaner dataset."
            )
        gc.collect()
        return df

    def _get_train_size(self, df):
        """
        Adaptive train/test split based on dataset size.
        Small datasets → larger train set to avoid tiny test sets.
        Tiny test sets cause fake 100% scores.
        """
        n = len(df)
        if n < 50:
            return 0.7      # 70/30 split for very small data
        elif n < 200:
            return 0.75     # 75/25 split for small data
        else:
            return 0.8      # Standard 80/20 for normal data

    def _check_overfitting(self, metrics, df, task_type):
        """
        Detect suspicious perfect scores and add warning to metrics.
        Perfect scores on tiny datasets = overfitting, not real performance.
        """
        n = len(df)
        warning = None

        if task_type == "classification":
            acc = metrics.get("accuracy", 0)
            f1 = metrics.get("f1_score", 0)
            if (acc >= 0.99 or f1 >= 0.99) and n < 200:
                warning = (
                    f"⚠️ Perfect score on only {n} rows likely means overfitting — "
                    "not a reliable result. Validate on a larger dataset."
                )
            elif acc >= 0.99 or f1 >= 0.99:
                warning = (
                    "⚠️ Perfect scores detected — verify your dataset has no "
                    "data leakage (target column info in features)."
                )

        elif task_type == "regression":
            r2 = metrics.get("r2_score", 0)
            if r2 >= 0.99 and n < 200:
                warning = (
                    f"⚠️ R² of {r2:.2f} on only {n} rows likely means overfitting — "
                    "not a reliable result. Validate on a larger dataset."
                )

        if warning:
            metrics["overfitting_warning"] = warning

        return metrics

    # ============================================================
    # CLASSIFICATION
    # ============================================================

    def _build_classification_model(self, df, target_column, test_size):
        from pycaret.classification import (
            setup, compare_models, finalize_model,
            predict_model, pull, get_config,
        )

        df = self._prepare_df(df, target_column)
        n_folds = min(3, max(2, len(df) // 10))
        train_size = self._get_train_size(df)

        self.setup_config = setup(
            data=df,
            target=target_column,
            train_size=train_size,
            session_id=42,
            verbose=False,
            n_jobs=1,
            preprocess=True,
            normalize=True,
            transformation=False,
            pca=False,
            remove_multicollinearity=False,
            polynomial_features=False,
        )

        best_model = compare_models(
            n_select=1,
            sort="F1",
            fold=n_folds,
            include=CLASSIFICATION_INCLUDE,
            budget_time=2.0,
            turbo=True,
            errors="ignore",
        )

        comparison_df = pull()
        self.model = finalize_model(best_model)

        self._save_artifacts(
            model=self.model,
            feature_columns=[c for c in df.columns if c != target_column],
            task_type="classification",
        )

        test_data = get_config("X_test")
        test_labels = get_config("y_test")
        predictions = predict_model(self.model, data=test_data)

        self.metrics = self._extract_classification_metrics(predictions, test_labels, comparison_df)
        self.metrics = self._check_overfitting(self.metrics, df, "classification")
        self.feature_importance = self._get_feature_importance(self.model, df, target_column)

        gc.collect()

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
            setup, compare_models, finalize_model,
            predict_model, pull, get_config,
        )

        df = self._prepare_df(df, target_column)
        n_folds = min(3, max(2, len(df) // 10))
        train_size = self._get_train_size(df)

        self.setup_config = setup(
            data=df,
            target=target_column,
            train_size=train_size,
            session_id=42,
            verbose=False,
            n_jobs=1,
            preprocess=True,
            normalize=True,
            transformation=False,
            pca=False,
            remove_multicollinearity=False,
            polynomial_features=False,
        )

        best_model = compare_models(
            n_select=1,
            sort="R2",
            fold=n_folds,
            include=REGRESSION_INCLUDE,
            budget_time=2.0,
            turbo=True,
            errors="ignore",
        )

        comparison_df = pull()
        self.model = finalize_model(best_model)

        self._save_artifacts(
            model=self.model,
            feature_columns=[c for c in df.columns if c != target_column],
            task_type="regression",
        )

        test_data = get_config("X_test")
        test_labels = get_config("y_test")
        predictions = predict_model(self.model, data=test_data)

        self.metrics = self._extract_regression_metrics(predictions, test_labels, comparison_df)
        self.metrics = self._check_overfitting(self.metrics, df, "regression")
        self.feature_importance = self._get_feature_importance(self.model, df, target_column)

        gc.collect()

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
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = model.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, clusters)

        self.model = model
        self.preprocessor = scaler
        self._save_artifacts(model=model, feature_columns=list(X.columns),
                             task_type="clustering", scaler=scaler)

        df_out = df.copy()
        df_out["cluster"] = clusters

        pca = PCA(n_components=2)
        components = pca.fit_transform(X_scaled)
        df_out["pca_1"] = components[:, 0]
        df_out["pca_2"] = components[:, 1]

        self.metrics = {"n_clusters": k, "algorithm": "KMeans",
                        "silhouette_score": round(score, 4)}

        return {
            "model": model,
            "metrics": self.metrics,
            "predictions": df_out,
            "viz_data": df_out,
            "task_type": "clustering",
            "comparison": pd.DataFrame(),
            "feature_importance": pd.DataFrame(),
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
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        y_pred = predictions["prediction_label"].values
        y_true = test_labels.values

        metrics = {
            "accuracy": round(accuracy_score(y_true, y_pred), 4),
            "precision": round(precision_score(y_true, y_pred, average="weighted", zero_division=0), 4),
            "recall": round(recall_score(y_true, y_pred, average="weighted", zero_division=0), 4),
            "f1_score": round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 4),
        }
        if not comparison_df.empty:
            metrics["model_name"] = comparison_df.index[0]
        return metrics

    def _extract_regression_metrics(self, predictions, test_labels, comparison_df):
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

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
    # FEATURE IMPORTANCE
    # ============================================================

    def _get_feature_importance(self, model, df, target_column):
        try:
            feature_names = [c for c in df.columns if c != target_column]
            actual_model = model
            if hasattr(model, "named_steps"):
                for step in model.named_steps.values():
                    if hasattr(step, "feature_importances_") or hasattr(step, "coef_"):
                        actual_model = step
                        break

            if hasattr(actual_model, "feature_importances_"):
                importances = actual_model.feature_importances_
            elif hasattr(actual_model, "coef_"):
                importances = np.abs(actual_model.coef_).flatten()
            else:
                return pd.DataFrame({
                    "feature": feature_names,
                    "importance": [1 / len(feature_names)] * len(feature_names),
                })

            min_len = min(len(feature_names), len(importances))
            return pd.DataFrame({
                "feature": feature_names[:min_len],
                "importance": importances[:min_len],
            }).sort_values("importance", ascending=False)

        except Exception:
            return pd.DataFrame(columns=["feature", "importance"])