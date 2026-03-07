"""
PromptML Studio - Model Builder
Optimised for Streamlit Cloud + Render Free Tier:
- Uses include= instead of exclude= to prevent OOM (Broken pipe)
- gc.collect() after data prep to free memory before training
- Correct model selection (rf/et wins over lr on real datasets)
- Auto-clean missing target values
- Adaptive fold count for tiny datasets
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


# ── Lightweight model pools ──────────────────────────────────────
# Using include= (not exclude=) so PyCaret ONLY loads these models
# into memory — prevents the Broken Pipe / OOM kill on free tier.
#
# Classification pool — 7 fast, accurate, memory-light models:
#   lr    = Logistic Regression
#   dt    = Decision Tree
#   rf    = Random Forest      ← usually wins on real datasets
#   et    = Extra Trees        ← usually wins on real datasets
#   ridge = Ridge Classifier
#   lda   = Linear Discriminant Analysis
#   nb    = Naive Bayes
CLASSIFICATION_INCLUDE = ["lr", "dt", "rf", "et", "ridge", "lda", "nb"]

# Regression pool — 7 fast, accurate, memory-light models:
#   lr    = Linear Regression
#   dt    = Decision Tree
#   rf    = Random Forest
#   et    = Extra Trees
#   ridge = Ridge Regression
#   lasso = Lasso Regression
#   en    = ElasticNet
REGRESSION_INCLUDE = ["lr", "dt", "rf", "et", "ridge", "lasso", "en"]


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

        # Free memory before heavy PyCaret setup
        gc.collect()
        return df

    # ============================================================
    # CLASSIFICATION
    # ============================================================

    def _build_classification_model(self, df, target_column, test_size):
        from pycaret.classification import (
            setup, compare_models, finalize_model,
            predict_model, pull, get_config,
        )

        df = self._prepare_df(df, target_column)

        # Adaptive fold count — prevents CV error on tiny datasets
        n_folds = min(3, max(2, len(df) // 10))

        self.setup_config = setup(
            data=df,
            target=target_column,
            train_size=0.8,
            session_id=42,
            verbose=False,
            n_jobs=1,
            preprocess=True,
            normalize=True,
            transformation=False,       # skip — saves memory + time
            pca=False,                  # skip — not needed for < 50 features
            remove_multicollinearity=False,
            polynomial_features=False,
        )

        # include= loads ONLY these 7 models — prevents OOM/Broken pipe
        best_model = compare_models(
            n_select=1,
            sort="F1",              # F1 avoids class-imbalance bias vs Accuracy
            fold=n_folds,
            include=CLASSIFICATION_INCLUDE,
            budget_time=2.0,
            turbo=True,
            errors="ignore",        # skip any model that crashes instead of failing all
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

        self.setup_config = setup(
            data=df,
            target=target_column,
            train_size=0.8,
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

        # include= loads ONLY these 7 models — prevents OOM/Broken pipe
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

        gc.collect()

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

            # Unwrap PyCaret pipeline
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