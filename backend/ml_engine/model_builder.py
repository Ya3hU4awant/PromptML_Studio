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
# Linear models (lr, ridge, lda) removed — they use coef_ as feature importance
# which is distorted by feature scale, giving wrong rankings (e.g. Dependents > Credit_Score)
# Tree-based models use information gain — honest, scale-independent feature importance
CLASSIFICATION_INCLUDE = ["dt", "rf", "et", "ada", "knn"]

# Regression: 8 models, all memory-safe
# Linear models removed for same reason — coef_ importance is scale-distorted
REGRESSION_INCLUDE = ["dt", "rf", "et", "ada", "knn"]


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
        Detect suspicious scores and add contextual warning to metrics.
        - Perfect scores on small data = likely overfitting
        - Very high scores on any size = possible data leakage
        - Low scores = model needs more/better data
        """
        n = len(df)
        warning = None

        if task_type == "classification":
            acc = metrics.get("accuracy", 0)
            f1 = metrics.get("f1_score", 0)
            best = max(acc, f1)
            if best >= 0.99 and n < 500:
                warning = (
                    f"⚠️ Score of {best:.0%} on only {n} rows likely means overfitting — "
                    "the model memorized training data. Validate on a larger, unseen dataset."
                )
            elif best >= 0.99:
                warning = (
                    f"⚠️ Perfect score detected — verify there is no data leakage "
                    "(target column information accidentally present in features)."
                )
            elif best < 0.60:
                warning = (
                    f"⚠️ Low score of {best:.0%} — model is struggling. "
                    "Try adding more rows, cleaning data, or improving your prompt."
                )

        elif task_type == "regression":
            r2 = metrics.get("r2_score", 0)
            if r2 >= 0.99 and n < 500:
                warning = (
                    f"⚠️ R² of {r2:.2f} on only {n} rows likely means overfitting — "
                    "the model memorized training data. Validate on a larger dataset."
                )
            elif r2 >= 0.99:
                warning = (
                    f"⚠️ Perfect R² detected — verify there is no data leakage "
                    "(target column information accidentally present in features)."
                )
            elif r2 < 0.40:
                warning = (
                    f"⚠️ Low R² of {r2:.2f} — model is struggling to find patterns. "
                    "Try adding more rows or relevant features."
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
            df=df,
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
            df=df,
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

    def _save_artifacts(self, model, feature_columns, task_type, scaler=None, df=None):
        os.makedirs("artifacts", exist_ok=True)
        joblib.dump(model, "artifacts/model.pkl")
        joblib.dump(feature_columns, "artifacts/features.pkl")
        joblib.dump(task_type, "artifacts/task_type.pkl")
        if scaler:
            joblib.dump(scaler, "artifacts/scaler.pkl")
        # Save categorical column options for smart UI generation
        if df is not None:
            cat_options = {}
            for col in feature_columns:
                if col in df.columns and df[col].dtype == object:
                    vals = sorted(df[col].dropna().unique().tolist())
                    if vals:
                        cat_options[col] = vals
            joblib.dump(cat_options, "artifacts/cat_options.pkl")

    # ============================================================
    # METRICS
    # ============================================================

    def _extract_classification_metrics(self, predictions, test_labels, comparison_df):
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        y_pred = predictions["prediction_label"].values
        y_true = test_labels.values

        from sklearn.metrics import confusion_matrix as sk_cm
        metrics = {
            "accuracy":  round(accuracy_score(y_true, y_pred), 4),
            "precision": round(precision_score(y_true, y_pred, average="weighted", zero_division=0), 4),
            "recall":    round(recall_score(y_true, y_pred, average="weighted", zero_division=0), 4),
            "f1_score":  round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 4),
            "confusion_matrix": sk_cm(y_true, y_pred).tolist(),
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
        """
        Compute feature importance INDEPENDENTLY from PyCaret using a clean
        sklearn pipeline on the ORIGINAL data.

        WHY NOT USE PYCARET'S MODEL DIRECTLY:
        PyCaret's internal preprocessing (NaN imputation → new category string,
        then one-hot encoding) changes the number of columns unpredictably.
        The model's feature_importances_ array maps to TRANSFORMED columns,
        not original column names. This causes wrong rankings on any dataset
        that has NaN values in categorical columns (e.g. Collateral has 186 NaN).

        THIS APPROACH IS SAFE FOR ALL DATASETS BECAUSE:
        - Handles NaN in both numeric (median) and categorical (fills 'Unknown')
        - Uses OrdinalEncoder — no column explosion, always same count as input
        - RF for classification, ExtraTreesRegressor for regression
        - Both are tree-based = scale-independent, honest importances
        - Works with any number of features, any mix of types
        """
        from sklearn.preprocessing import OrdinalEncoder

        feature_names = [c for c in df.columns if c != target_column]
        task = self.task_type  # "classification" or "regression"

        try:
            X = df[feature_names].copy()
            y = df[target_column].copy()

            # ── Step 1: Fill NaN safely ────────────────────────────────────
            cat_cols = X.select_dtypes(include='object').columns.tolist()
            num_cols = X.select_dtypes(exclude='object').columns.tolist()

            for c in num_cols:
                X[c] = X[c].fillna(X[c].median())
            for c in cat_cols:
                X[c] = X[c].fillna('Unknown')
                X[c] = OrdinalEncoder(
                    handle_unknown='use_encoded_value', unknown_value=-1
                ).fit_transform(X[[c]])

            # ── Step 2: Pick estimator based on task type ──────────────────
            if task == "regression":
                from sklearn.ensemble import ExtraTreesRegressor
                estimator = ExtraTreesRegressor(
                    n_estimators=100, random_state=42, n_jobs=1
                )
            else:
                # classification (default — also used as fallback)
                from sklearn.ensemble import RandomForestClassifier
                # For binary classification ensure y is int
                try:
                    y = y.astype(int)
                except Exception:
                    pass
                estimator = RandomForestClassifier(
                    n_estimators=100, random_state=42, n_jobs=1
                )

            estimator.fit(X, y)

            result_df = pd.DataFrame({
                "feature": feature_names,
                "importance": estimator.feature_importances_,
            }).sort_values("importance", ascending=False)

            # Normalise to sum = 1.0
            total = result_df["importance"].sum()
            if total > 0:
                result_df["importance"] = (result_df["importance"] / total).round(4)

            return result_df

        except Exception as e:
            print(f"[WARN] Feature importance extraction failed: {e}")
            return pd.DataFrame(columns=["feature", "importance"])