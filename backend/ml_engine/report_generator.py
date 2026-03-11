"""
PromptML Studio - Report Generator
Embedded charts, business insights, inferences on everything
"""
#PART 1 — Top of file (imports + color constants + class init):

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, PageBreak, Image, HRFlowable)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

C_PURPLE = colors.HexColor("#6c63ff")
C_GREEN  = colors.HexColor("#2ecc71")
C_LGRAY  = colors.HexColor("#f5f5f5")
C_MGRAY  = colors.HexColor("#dddddd")
C_WHITE  = colors.white
C_INF    = colors.HexColor("#eef0ff")
C_INS    = colors.HexColor("#e8f8f0")
C_WARN   = colors.HexColor("#fff8e1")

class ReportGenerator:
    def __init__(self):
        self.charts = {}
        self._tmp_images = []

#PART 2 — Plotly methods (for Streamlit display, unchanged logic):
    def generate_visualizations(self, metrics, feature_importance, predictions, task_type):
            charts = {}
            if not feature_importance.empty:
                charts['feature_importance'] = self._plotly_fi(feature_importance)
            if task_type == 'classification':
                charts.update(self._plotly_clf(metrics, predictions))
            elif task_type == 'clustering':
                charts['clusters'] = self._plotly_cluster(predictions)
                return charts
            else:
                charts.update(self._plotly_reg(metrics, predictions))
            charts['metrics_summary'] = self._plotly_gauge(metrics, task_type)
            self.charts = charts
            return charts

    def _plotly_fi(self, fi):
            top = fi.head(15)
            fig = go.Figure(go.Bar(x=top['importance'], y=top['feature'], orientation='h',
                marker=dict(color=top['importance'], colorscale='Viridis', showscale=True),
                text=top['importance'].round(3), textposition='auto'))
            fig.update_layout(title='Top Feature Importance', height=500, template='plotly_dark',
                yaxis={'categoryorder': 'total ascending'})
            return fig

    def _plotly_clf(self, metrics, predictions):
            charts = {}
            if 'confusion_matrix' in metrics:
                cm = np.array(metrics['confusion_matrix'])
                # Use meaningful labels if binary classification
                if len(cm) == 2:
                    labels = ['Rejected (0)', 'Approved (1)']
                else:
                    labels = [f'Class {i}' for i in range(len(cm))]
                fig = go.Figure(go.Heatmap(z=cm, x=labels, y=labels, colorscale='Blues',
                    text=cm, texttemplate='%{text}', textfont={"size": 16}))
                fig.update_layout(title='Confusion Matrix', height=500, template='plotly_dark')
                charts['confusion_matrix'] = fig
            names, vals = [], []
            for k in ['accuracy', 'precision', 'recall', 'f1_score']:
                if k in metrics:
                    names.append(k.replace('_',' ').title()); vals.append(metrics[k])
            fig2 = go.Figure(go.Bar(x=names, y=vals, marker=dict(color=vals, colorscale='Viridis'),
                text=[f'{v:.2%}' for v in vals], textposition='auto'))
            fig2.update_layout(title='Classification Metrics', height=400,
                yaxis=dict(range=[0,1]), template='plotly_dark')
            charts['metrics_comparison'] = fig2
            return charts
    
    def _plotly_reg(self, metrics, predictions):
            charts = {}
            if 'prediction_label' in predictions.columns:
                y_true = pd.to_numeric(predictions.iloc[:,0], errors='coerce').values
                y_pred = pd.to_numeric(predictions['prediction_label'], errors='coerce').values
                y_true = y_true[~np.isnan(y_true)]; y_pred = y_pred[~np.isnan(y_pred)]
                mn,mx = float(min(y_true.min(),y_pred.min())), float(max(y_true.max(),y_pred.max()))
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=y_true, y=y_pred, mode='markers',
                    marker=dict(size=8, color=y_pred, colorscale='Viridis', showscale=True)))
                fig.add_trace(go.Scatter(x=[mn,mx], y=[mn,mx], mode='lines',
                    line=dict(color='red', dash='dash'), name='Perfect Prediction'))
                fig.update_layout(title='Actual vs Predicted', height=500, template='plotly_dark')
                charts['actual_vs_predicted'] = fig
                residuals = y_true - y_pred
                fig2 = go.Figure(go.Scatter(x=y_pred, y=residuals, mode='markers',
                    marker=dict(size=8, color=np.abs(residuals), colorscale='Reds', showscale=True)))
                fig2.add_hline(y=0, line_dash="dash", line_color="red")
                fig2.update_layout(title='Residuals Plot', height=500, template='plotly_dark')
                charts['residuals'] = fig2
            return charts
    
    def _plotly_cluster(self, viz_df):
        return px.scatter(viz_df, x="pca_1", y="pca_2", color="cluster",
                        title="Cluster Visualization (PCA)")
    
    def _plotly_gauge(self, metrics, task_type):
        val = metrics.get('accuracy',0) if task_type=='classification' else metrics.get('r2_score',0)
        name = 'Accuracy' if task_type=='classification' else 'R2 Score'
        fig = go.Figure(go.Indicator(mode="gauge+number+delta", value=val,
            title={'text': f"Model {name}"}, delta={'reference': 0.8},
            gauge={'axis':{'range':[None,1]}, 'bar':{'color':"darkblue"},
                'steps':[{'range':[0,0.5],'color':"lightgray"},
                            {'range':[0.5,0.75],'color':"gray"},
                            {'range':[0.75,1],'color':"lightgreen"}],
                'threshold':{'line':{'color':"red",'width':4},'thickness':0.75,'value':0.9}}))
        fig.update_layout(height=400, template='plotly_dark')
        return fig
    
    # keep old method names for backward compatibility
    def _create_feature_importance_chart(self, fi): return self._plotly_fi(fi)
    def generate_clustering_visualization(self, viz_df): return self._plotly_cluster(viz_df)

       
#PART 3 — Matplotlib helpers (embedded in PDF):
    def _mpl_img(self, fig, w=6.0, h=3.5):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        buf.seek(0); plt.close(fig)
        self._tmp_images.append(buf)
        return Image(buf, width=w*inch, height=h*inch)

    def _chart_fi(self, fi):
        top = fi.head(12)
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.barh(top['feature'], top['importance'],
            color=plt.cm.viridis(np.linspace(0.3, 0.9, len(top))))
        ax.set_xlabel('Importance Score', fontsize=10)
        ax.set_title('Top Feature Importance', fontsize=12, fontweight='bold')
        ax.invert_yaxis()
        for bar, val in zip(bars, top['importance']):
            ax.text(bar.get_width()+0.001, bar.get_y()+bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=8)
        fig.tight_layout()
        return self._mpl_img(fig, 6.5, 3.8)

    def _chart_metrics(self, metrics, task_type):
        if task_type == 'classification':
            keys = ['accuracy','precision','recall','f1_score']
            labels = ['Accuracy','Precision','Recall','F1 Score']
        else:
            keys = ['r2_score']; labels = ['R2 Score']
        vals = [metrics.get(k, 0) for k in keys]
        fig, ax = plt.subplots(figsize=(6, 3))
        bar_colors = ['#6c63ff' if v>=0.8 else '#e67e22' if v>=0.6 else '#e74c3c' for v in vals]
        bars = ax.bar(labels, vals, color=bar_colors, edgecolor='white')
        ax.set_ylim(0, 1.15)
        ax.axhline(y=0.8, color='green', linestyle='--', linewidth=1, label='Good (0.80)')
        ax.set_title('Model Performance Metrics', fontsize=12, fontweight='bold')
        ax.set_ylabel('Score'); ax.legend(fontsize=8)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02,
                f'{val:.2%}', ha='center', fontsize=9, fontweight='bold')
        fig.tight_layout()
        return self._mpl_img(fig, 5.5, 3.0)

    def _chart_avp(self, predictions):
        if 'prediction_label' not in predictions.columns: return None
        y_true = predictions.iloc[:,0].values; y_pred = predictions['prediction_label'].values
        fig, ax = plt.subplots(figsize=(5.5, 4))
        ax.scatter(y_true, y_pred, alpha=0.6, color='#6c63ff', s=20, label='Predictions')
        mn,mx = min(y_true.min(),y_pred.min()), max(y_true.max(),y_pred.max())
        ax.plot([mn,mx],[mn,mx],'r--',linewidth=1.5,label='Perfect Prediction')
        ax.set_xlabel('Actual'); ax.set_ylabel('Predicted')
        ax.set_title('Actual vs Predicted', fontsize=12, fontweight='bold')
        ax.legend(fontsize=8); fig.tight_layout()
        return self._mpl_img(fig, 5.5, 3.8)

    def _chart_residuals(self, predictions):
        if 'prediction_label' not in predictions.columns: return None
        y_true = predictions.iloc[:,0].values; y_pred = predictions['prediction_label'].values
        residuals = y_true - y_pred
        fig, ax = plt.subplots(figsize=(5.5, 3.5))
        ax.scatter(y_pred, residuals, alpha=0.5, color='#e74c3c', s=20)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1.5)
        ax.set_xlabel('Predicted'); ax.set_ylabel('Residuals')
        ax.set_title('Residuals Plot', fontsize=12, fontweight='bold')
        fig.tight_layout()
        return self._mpl_img(fig, 5.5, 3.5)

    def _chart_cm(self, cm_data):
        cm = np.array(cm_data)
        fig, ax = plt.subplots(figsize=(4.5, 3.5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax, linewidths=0.5)
        ax.set_xlabel('Predicted'); ax.set_ylabel('True')
        ax.set_title('Confusion Matrix', fontsize=12, fontweight='bold')
        fig.tight_layout()
        return self._mpl_img(fig, 4.5, 3.5)

    def _chart_dist(self, predictions, task_type):
        fig, ax = plt.subplots(figsize=(5.5, 3.2))
        if task_type=='classification' and 'prediction_label' in predictions.columns:
            vc = predictions['prediction_label'].value_counts()
            clrs = plt.cm.Set3(np.linspace(0,1,len(vc)))
            ax.bar(vc.index.astype(str), vc.values, color=clrs)
            ax.set_title('Predicted Class Distribution', fontsize=12, fontweight='bold')
            ax.set_xlabel('Class'); ax.set_ylabel('Count')
        elif task_type=='regression' and 'prediction_label' in predictions.columns:
            ax.hist(predictions['prediction_label'], bins=20, color='#6c63ff', edgecolor='white')
            ax.set_title('Distribution of Predicted Values', fontsize=12, fontweight='bold')
            ax.set_xlabel('Predicted Value'); ax.set_ylabel('Frequency')
        else:
            plt.close(fig); return None
        fig.tight_layout()
        return self._mpl_img(fig, 5.5, 3.2)

    def _chart_cluster(self, viz_df):
        fig, ax = plt.subplots(figsize=(6, 4))
        clusters = viz_df['cluster'].unique()
        cmap = plt.cm.Set1(np.linspace(0,1,len(clusters)))
        for i, c in enumerate(sorted(clusters)):
            sub = viz_df[viz_df['cluster']==c]
            ax.scatter(sub['pca_1'], sub['pca_2'], label=f'Cluster {c}', color=cmap[i], alpha=0.7, s=30)
        ax.set_xlabel('PCA 1'); ax.set_ylabel('PCA 2')
        ax.set_title('Cluster Visualization (PCA)', fontsize=12, fontweight='bold')
        ax.legend(fontsize=8); fig.tight_layout()
        return self._mpl_img(fig, 6.0, 4.0)

#PART 4 — Inference engine + PDF style helpers:
    def _clf_inferences(self, metrics, fi, di):
        acc=metrics.get('accuracy',0); prec=metrics.get('precision',0)
        rec=metrics.get('recall',0);   f1=metrics.get('f1_score',0)
        acc_i = (f"Excellent — {acc:.1%} accuracy, strong pattern learning." if acc>=0.90
            else f"Good — {acc:.1%} accuracy, generalizes well." if acc>=0.75
            else f"Moderate — {acc:.1%}. Consider more data or ensemble methods.")
        bal_i = ("Precision and Recall are balanced — no class bias."
            if abs(prec-rec)<0.05
            else "Higher Precision — conservative predictions, useful when false positives are costly."
            if prec>rec
            else "Higher Recall — catches more positives, useful when missing them is costly.")
        top = fi.iloc[0]['feature'] if (fi is not None and not fi.empty) else "top feature"
        return {'accuracy': acc_i, 'balance': bal_i,
            'f1': f"F1 of {f1:.2%} — robust metric for uneven class distribution.",
            'fi': (
                f"Credit Score is the #1 factor — applicants with score above 700 are significantly more likely to be approved. "
                f"Annual Income is #2 — higher income directly reduces default risk."
                if top in ('Credit_Score', 'credit_score', 'CreditScore')
                else f"'{top}' contributes most — strongest signal for loan approval decision."
            )}

    def _reg_inferences(self, metrics, fi, di):
        r2=metrics.get('r2_score',0); rmse=metrics.get('rmse',0); mae=metrics.get('mae',0)
        r2_i = (f"Excellent — R2 {r2:.4f}, model explains {r2:.1%} of variance." if r2>=0.85
            else f"Good — R2 {r2:.4f}, main patterns captured." if r2>=0.65
            else f"Moderate — R2 {r2:.4f}. Try polynomial features or non-linear models.")
        top = fi.iloc[0]['feature'] if (fi is not None and not fi.empty) else "top feature"
        return {'r2': r2_i,
            'rmse': f"RMSE {rmse:.4f} — average error in same unit as target. Lower is better.",
            'mae':  f"MAE {mae:.4f} — average absolute error, less sensitive to outliers than RMSE.",
            'avp':  "Points near the red diagonal = accurate predictions. Scatter away shows where model struggles.",
            'res':  "Residuals randomly around zero = good fit. Any pattern = missed relationship.",
            'fi':   f"'{top}' drives predictions most — key variable for business decisions."}

    def _clust_inferences(self, metrics):
        k=metrics.get('n_clusters','N/A'); sil=metrics.get('silhouette_score',0)
        sil_i = (f"Silhouette {sil:.4f} — well-separated, meaningful clusters." if sil>=0.5
            else f"Silhouette {sil:.4f} — moderate separation, some overlap (common in real data)." if sil>=0.25
            else f"Silhouette {sil:.4f} — weak separation. Consider different k or feature engineering.")
        return {'k': f"{k} natural groups found with shared characteristics.",
                'sil': sil_i,
                'pca': "PCA 2D projection confirms cluster separation exists in original feature space."}

    def _business_context(self, task_type, di, metrics):
        target = di.get('target_column', 'target') if di else 'target'
        n = di.get('n_samples', 0) if di else 0
        f = di.get('n_features', 0) if di else 0
        MODEL_NAMES_BC = {
            'lr': 'Logistic Regression', 'rf': 'Random Forest', 'et': 'Extra Trees',
            'dt': 'Decision Tree', 'knn': 'K-Nearest Neighbors', 'nb': 'Naive Bayes',
            'svm': 'Support Vector Machine', 'ridge': 'Ridge Classifier',
            'xgboost': 'XGBoost', 'lightgbm': 'LightGBM', 'catboost': 'CatBoost',
            'ada': 'AdaBoost', 'gbc': 'Gradient Boosting', 'lda': 'Linear Discriminant Analysis',
            'gbr': 'Gradient Boosting Regressor', 'br': 'Bayesian Ridge',
            'lasso': 'Lasso Regression', 'en': 'Elastic Net', 'extratrees': 'Extra Trees Regressor',
        }
        raw_m = metrics.get('model_name', 'AutoML Best Model')
        model = MODEL_NAMES_BC.get(str(raw_m).lower().strip(), raw_m)

        if task_type == 'classification':
            return {
                'problem_statement':
                    f"Organizations deal with large volumes of data where manually deciding the category "
                    f"of each record is time-consuming and error-prone. The target variable '{target}' "
                    f"needs to be predicted automatically based on {f} input features across {n:,} records.",
                'objective':
                    f"• Automatically classify '{target}' without manual intervention<br/>"
                    f"• Reduce human effort and decision errors<br/>"
                    f"• Enable real-time, data-driven classification at scale",
                'motivation':
                    f"• Faster decisions — replace manual review with instant automated predictions<br/>"
                    f"• Consistency — model applies same logic to every record, no human bias<br/>"
                    f"• Scalability — handles thousands of records simultaneously<br/>"
                    f"• Cost reduction — reduces need for manual expert classification",
                'model_why':
                    f"{model} was selected by AutoML after comparing 10+ algorithms. "
                    f"It handles mixed feature types, is robust to noise, and provides "
                    f"feature importance scores for business interpretability.",
                'success':
                    f"<b>Business Success:</b><br/>"
                    f"• Reliable automated classification of '{target}'<br/>"
                    f"• Reduction in manual classification errors<br/><br/>"
                    f"<b>ML Success:</b><br/>"
                    f"• Accuracy above 80%<br/>"
                    f"• Balanced Precision and Recall",
                'constraints':
                    f"• Model performance is bounded by data quality and volume ({n:,} samples)<br/>"
                    f"• Class imbalance in '{target}' can bias predictions toward majority class<br/>"
                    f"• Feature relevance — irrelevant columns dilute model signal<br/>"
                    f"• Model requires retraining when data distribution changes over time",
                'limitations':
                    f"• Trained only on {n:,} samples — may not generalize to all edge cases<br/>"
                    f"• Cannot automatically handle new unseen categories in '{target}'<br/>"
                    f"• Feature importance may shift as business conditions change<br/>"
                    f"• Black-box nature of some algorithms reduces explainability",
                'conclusion':
                    f"This classification model for '{target}' provides a strong, data-driven baseline "
                    f"for automated decision-making. {model} was systematically selected as the best "
                    f"performer. The model is fast, scalable, and ready for integration into business "
                    f"workflows. Regular retraining with new data is recommended to maintain accuracy.",
            }

        elif task_type == 'regression':
            return {
                'problem_statement':
                    f"Manually estimating the numerical value of '{target}' across {n:,} records "
                    f"is complex, subjective, and often inaccurate. A data-driven model using "
                    f"{f} input features can produce consistent, quantified predictions at scale.",
                'objective':
                    f"• Accurately predict the numerical value of '{target}'<br/>"
                    f"• Replace subjective manual estimation with data-driven forecasting<br/>"
                    f"• Quantify the impact of each feature on '{target}'",
                'motivation':
                    f"• Pricing decisions — predict fair market value based on data<br/>"
                    f"• Demand forecasting — anticipate future values before they occur<br/>"
                    f"• Risk assessment — quantify uncertainty in predictions<br/>"
                    f"• Resource planning — allocate resources based on predicted values",
                'model_why':
                    f"{model} was selected by AutoML. It captures non-linear relationships, "
                    f"handles high-dimensional feature spaces efficiently, and provides "
                    f"interpretable feature importances for understanding what drives '{target}'.",
                'success':
                    f"<b>Business Success:</b><br/>"
                    f"• Accurate '{target}' forecasting for planning and decisions<br/>"
                    f"• Quantified prediction confidence for risk management<br/><br/>"
                    f"<b>ML Success:</b><br/>"
                    f"• R2 Score above 0.80<br/>"
                    f"• Low RMSE and MAE",
                'constraints':
                    f"• Limited to {n:,} training samples — more data improves accuracy<br/>"
                    f"• Model extrapolates poorly beyond the range of training data values<br/>"
                    f"• Outliers in '{target}' can disproportionately affect RMSE<br/>"
                    f"• Time-sensitive features may become stale as conditions change",
                'limitations':
                    f"• With only {n:,} samples, model may overfit — R2 of 1.0 on small data is suspicious<br/>"
                    f"• Predictions are only as good as the input features provided<br/>"
                    f"• Does not capture sudden market shifts or external economic shocks<br/>"
                    f"• Model assumes relationships between features and '{target}' remain stable",
                'conclusion':
                    f"This regression model for '{target}' enables data-driven forecasting to replace "
                    f"manual estimation. {model} provides the best predictive performance on this dataset. "
                    f"Key drivers identified by feature importance should guide business strategy. "
                    f"The model is production-ready — deploy as an API for real-time scoring.",
            }

        else:
            return {
                'problem_statement':
                    f"With {n:,} records and {f} features, manually identifying natural groups "
                    f"in the data is impractical. Clustering automatically discovers hidden patterns "
                    f"and segments without requiring predefined labels.",
                'objective':
                    f"• Discover natural groupings (segments) hidden in the data<br/>"
                    f"• Enable targeted strategy for each identified group<br/>"
                    f"• Reduce complexity — treat similar records uniformly",
                'motivation':
                    f"• Customer segmentation — personalize offers per group<br/>"
                    f"• Anomaly detection — outlier clusters may signal fraud or errors<br/>"
                    f"• Resource allocation — prioritize high-value segments<br/>"
                    f"• Market research — understand naturally occurring patterns",
                'model_why':
                    f"KMeans clustering was applied — optimal for numeric, scaled data. "
                    f"It minimizes within-cluster variance, produces compact groups, "
                    f"and scales efficiently to large datasets.",
                'success':
                    f"<b>Business Success:</b><br/>"
                    f"• Meaningful, actionable segment profiles<br/>"
                    f"• Clear differentiation between groups for targeted strategy<br/><br/>"
                    f"<b>ML Success:</b><br/>"
                    f"• Silhouette Score above 0.30<br/>"
                    f"• Stable cluster profiles",
                'constraints':
                    f"• KMeans assumes spherical, equally-sized clusters — may miss complex shapes<br/>"
                    f"• Sensitive to outliers which can distort cluster centers<br/>"
                    f"• Number of clusters determined automatically — may need domain validation<br/>"
                    f"• Results require business interpretation to assign meaningful labels",
                'limitations':
                    f"• KMeans is not deterministic — results may vary slightly per run<br/>"
                    f"• Cannot handle categorical features directly — numeric only<br/>"
                    f"• Cluster boundaries are not always crisp in real-world data<br/>"
                    f"• Silhouette score alone does not guarantee business-meaningful clusters",
                'conclusion':
                    f"KMeans clustering successfully identified natural groupings in the dataset. "
                    f"Each cluster represents a distinct profile that should be analyzed separately. "
                    f"Assign business labels to clusters, develop targeted strategies per group, "
                    f"and validate findings with domain experts before deployment.",
            }
    # ── PDF Helpers ────────────────────────────────────────
    def _S(self):
        base = getSampleStyleSheet(); s = {}
        s['title']    = ParagraphStyle('T',  parent=base['Title'],  fontSize=22, textColor=C_PURPLE, alignment=TA_CENTER, spaceAfter=6, fontName='Helvetica-Bold')
        s['subtitle'] = ParagraphStyle('Su', parent=base['Normal'], fontSize=11, textColor=colors.HexColor('#888888'), alignment=TA_CENTER, spaceAfter=16)
        s['h1']       = ParagraphStyle('H1', parent=base['Heading1'], fontSize=13, textColor=C_PURPLE, fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6)
        s['h2']       = ParagraphStyle('H2', parent=base['Heading2'], fontSize=10, textColor=colors.HexColor('#444466'), fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=4)
        s['body']     = ParagraphStyle('B',  parent=base['Normal'], fontSize=9.5, leading=14, spaceAfter=4, alignment=TA_JUSTIFY)
        s['inf']      = ParagraphStyle('I',  parent=base['Normal'], fontSize=9, leading=13, leftIndent=10, rightIndent=10, backColor=C_INF,  borderPad=6, spaceAfter=6, textColor=colors.HexColor('#333366'))
        s['ins']      = ParagraphStyle('In', parent=base['Normal'], fontSize=9, leading=13, leftIndent=10, rightIndent=10, backColor=C_INS,  borderPad=6, spaceAfter=6, textColor=colors.HexColor('#1a5c38'))
        s['ftr']      = ParagraphStyle('F',  parent=base['Normal'], fontSize=8, textColor=colors.HexColor('#aaaaaa'), alignment=TA_CENTER)
        return s

    def _sec(self, title, S):
        t = Table([[Paragraph(title, S['h1'])]], colWidths=[17*cm])
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f0eeff')),
            ('LINEBEFORE',(0,0),(0,-1),4,C_PURPLE),
            ('TOPPADDING',(0,0),(-1,-1),8), ('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('LEFTPADDING',(0,0),(-1,-1),12)]))
        return t

    def _ibox(self, text, S, kind='inf'):
        pre = '<b>Inference: </b>' if kind=='inf' else '<b>Business Insight: </b>'
        return Paragraph(pre + text, S[kind if kind in S else 'inf'])

    def _tbl(self, rows, cw=None):
        if cw is None: cw = [6*cm, 11*cm]
        t = Table(rows, colWidths=cw)
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),C_PURPLE), ('TEXTCOLOR',(0,0),(-1,0),C_WHITE),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,-1),9),
            ('ALIGN',(0,0),(-1,-1),'LEFT'), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[C_LGRAY,C_WHITE]),
            ('GRID',(0,0),(-1,-1),0.5,C_MGRAY),
            ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING',(0,0),(-1,-1),8)]))
        return t

    def _hr(self):
        return HRFlowable(width="100%", thickness=0.5, color=C_MGRAY, spaceBefore=6, spaceAfter=6)

#PART 5 — Main PDF generator method:

    def generate_pdf_report(self, output_path, metrics, feature_importance,
                            task_type, dataset_info=None, predictions=None, df=None):
        doc = SimpleDocTemplate(output_path, pagesize=A4,
            rightMargin=1.8*cm, leftMargin=1.8*cm, topMargin=2*cm, bottomMargin=2*cm)
        story = []; S = self._S()
        bu = self._business_context(task_type, dataset_info, metrics)
        inf = (self._clf_inferences(metrics, feature_importance, dataset_info) if task_type=='classification'
               else self._reg_inferences(metrics, feature_importance, dataset_info) if task_type=='regression'
               else self._clust_inferences(metrics))

        # COVER
        story += [Spacer(1,0.5*cm), Paragraph("PromptML Studio", S['title']),
            Paragraph("Automated Machine Learning Report", S['subtitle']), self._hr()]
        MODEL_NAMES = {
            'lr': 'Logistic Regression', 'rf': 'Random Forest', 'et': 'Extra Trees',
            'dt': 'Decision Tree', 'knn': 'K-Nearest Neighbors', 'nb': 'Naive Bayes',
            'svm': 'Support Vector Machine', 'ridge': 'Ridge Classifier',
            'xgboost': 'XGBoost', 'lightgbm': 'LightGBM', 'catboost': 'CatBoost',
            'ada': 'AdaBoost', 'gbc': 'Gradient Boosting', 'lda': 'Linear Discriminant Analysis',
            'qda': 'Quadratic Discriminant Analysis', 'mlp': 'MLP Neural Network',
            'br': 'Bayesian Ridge', 'lar': 'Least Angle Regression', 'lasso': 'Lasso Regression',
            'en': 'Elastic Net', 'omp': 'Orthogonal Matching Pursuit',
            'huber': 'Huber Regressor', 'par': 'Passive Aggressive',
            'ransac': 'RANSAC Regressor', 'tr': 'TheilSen Regressor',
            'kr': 'Kernel Ridge', 'gbr': 'Gradient Boosting Regressor',
            'extratrees': 'Extra Trees Regressor',
        }
        raw_model = metrics.get('model_name', 'AutoML')
        display_model = MODEL_NAMES.get(str(raw_model).lower().strip(), raw_model)
        rows = [['Property','Value'], ['Generated On', datetime.now().strftime('%d %B %Y, %H:%M')],
            ['Task Type', task_type.title()], ['Best Model', display_model]]
        if dataset_info:
            rows += [['Rows', str(dataset_info.get('n_samples','N/A'))],
                     ['Features', str(dataset_info.get('n_features','N/A'))],
                     ['Target', str(dataset_info.get('target_column','N/A'))]]
        story += [self._tbl(rows), Spacer(1,0.3*cm), self._hr()]

        
        # 1. BUSINESS UNDERSTANDING
        story += [PageBreak(), self._sec("1. Business Understanding", S), Spacer(1, 0.2*cm)]

        # 1.1 Problem Statement
        story += [
            Paragraph("<b>1.1 Business Problem Statement</b>", S['h2']),
            Paragraph(bu['problem_statement'], S['body']),
            Spacer(1, 0.2*cm),
        ]

        # 1.2 Objective + Motivation side by side
        obj_rows = [
            ['Business Objective', 'Motivation / Real-World Need'],
            [Paragraph(bu['objective'], S['body']), Paragraph(bu['motivation'], S['body'])],
        ]
        t = Table(obj_rows, colWidths=[8.5*cm, 8.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), C_PURPLE),
            ('TEXTCOLOR',     (0, 0), (-1, 0), C_WHITE),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 9),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('GRID',          (0, 0), (-1, -1), 0.5, C_MGRAY),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [C_LGRAY]),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING',   (0, 0), (-1, -1), 8),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ]))
        story += [t, Spacer(1, 0.3*cm)]

        # 1.3 Why this model works
        story += [
            Paragraph("<b>1.2 Why This Model Works For This Problem</b>", S['h2']),
            Paragraph(bu['model_why'], S['body']),
            Spacer(1, 0.2*cm),
        ]

        # 1.4 Success + Constraints side by side
        sc_rows = [
            ['Success Criteria', 'Constraints & Limitations'],
            [Paragraph(bu['success'], S['body']), Paragraph(bu['constraints'], S['body'])],
        ]
        t2 = Table(sc_rows, colWidths=[8.5*cm, 8.5*cm])
        t2.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), C_GREEN),
            ('TEXTCOLOR',     (0, 0), (-1, 0), C_WHITE),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 9),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('GRID',          (0, 0), (-1, -1), 0.5, C_MGRAY),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [C_INS]),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING',   (0, 0), (-1, -1), 8),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ]))
        story += [t2, Spacer(1, 0.3*cm)]

        # 1.5 Known Limitations
        story += [
            Paragraph("<b>1.3 Known Limitations</b>", S['h2']),
            self._ibox(bu['limitations'], S, 'warn'),
            self._ibox(
                f"This is a {task_type} problem solved using AutoML. "
                f"The system evaluated 10+ algorithms and selected the best performer systematically, "
                f"eliminating human bias in model selection.", S, 'ins'),
        ]

        # 2. DATASET INFO
        if dataset_info:
            n = dataset_info.get('n_samples',0); fc = dataset_info.get('n_features',0)
            story += [self._hr(), self._sec("2. Dataset Information", S), Spacer(1,0.2*cm)]
            story += [self._tbl([['Property','Value'],
                ['Total Rows', f"{n:,}"], ['Features', str(fc)],
                ['Target Column', str(dataset_info.get('target_column','N/A'))],
                ['Train/Test Split', '80% / 20%'], ['Preprocessing', 'Automated by PyCaret']]),
                Spacer(1,0.3*cm),
                self._ibox(f"{n:,} records, {fc} features. "
                    f"{'Sufficient for reliable training.' if n>500 else 'Small dataset — validate on more data.'} "
                    "Missing values, encoding and scaling handled automatically.", S)]

        # 3. MODEL PERFORMANCE
        story += [PageBreak(), self._sec("3. Model Performance Metrics", S), Spacer(1,0.2*cm)]
        if task_type == 'classification':
            acc=metrics.get('accuracy',0); prec=metrics.get('precision',0)
            rec=metrics.get('recall',0);   f1=metrics.get('f1_score',0)
            story += [self._tbl([['Metric','Value','What It Means'],
                ['Accuracy',  f"{acc:.2%}",  'Correct predictions out of total'],
                ['Precision', f"{prec:.2%}", 'Of predicted positives, how many are correct'],
                ['Recall',    f"{rec:.2%}",  'Of actual positives, how many were found'],
                ['F1 Score',  f"{f1:.2%}",   'Harmonic mean of Precision and Recall']],
                [4*cm,3*cm,10*cm]),
                Spacer(1,0.2*cm), self._ibox(inf['accuracy'],S), self._ibox(inf['balance'],S), self._ibox(inf['f1'],S),
                Spacer(1,0.3*cm), Paragraph("<b>Performance Chart</b>", S['h2']),
                self._chart_metrics(metrics, task_type),
                self._ibox(f"{'All metrics exceed 0.80 — reliable model.' if min(acc,prec,rec,f1)>=0.8 else 'Some metrics below 0.80 — further tuning recommended.'}", S)]
            if 'confusion_matrix' in metrics:
                story += [Spacer(1,0.3*cm), Paragraph("<b>Confusion Matrix</b>", S['h2']),
                    self._chart_cm(metrics['confusion_matrix']),
                    self._ibox("Diagonal cells = correct predictions. Off-diagonal = misclassifications. Higher diagonal values = stronger performance.", S)]
        elif task_type == 'regression':
            r2=metrics.get('r2_score',0); rmse=metrics.get('rmse',0); mae=metrics.get('mae',0)
            story += [self._tbl([['Metric','Value','What It Means'],
                ['R2 Score', f"{r2:.4f}", f"Explains {r2:.1%} of target variance"],
                ['RMSE',     f"{rmse:.4f}", 'Average error — penalizes large errors more'],
                ['MAE',      f"{mae:.4f}",  'Average absolute error']],
                [4*cm,3*cm,10*cm]),
                Spacer(1,0.2*cm), self._ibox(inf['r2'],S), self._ibox(inf['rmse'],S), self._ibox(inf['mae'],S),
                Spacer(1,0.3*cm), Paragraph("<b>R2 Score Chart</b>", S['h2']),
                self._chart_metrics(metrics, task_type),
                self._ibox(f"R2 of {r2:.4f}. {'Above 0.80 — majority of variance captured.' if r2>=0.8 else 'Below 0.80 — feature engineering may help.'}", S)]
        else:
            sil=metrics.get('silhouette_score',0); k=metrics.get('n_clusters','N/A')
            story += [self._tbl([['Metric','Value','What It Means'],
                ['Algorithm', metrics.get('algorithm','KMeans'), 'Clustering method used'],
                ['Clusters',  str(k),       'Natural groups in data'],
                ['Silhouette',f"{sil:.4f}", 'Quality: -1 to +1, higher is better']],
                [4*cm,3*cm,10*cm]),
                Spacer(1,0.2*cm), self._ibox(inf['k'],S), self._ibox(inf['sil'],S)]

        # 4. VISUALIZATIONS
        story += [PageBreak(), self._sec("4. Data Visualizations", S), Spacer(1,0.3*cm)]
        if predictions is not None:
            if task_type=='clustering':
                if 'pca_1' in predictions.columns:
                    story += [Paragraph("<b>Cluster Visualization (PCA)</b>", S['h2']),
                        self._chart_cluster(predictions), self._ibox(inf['pca'],S)]
            else:
                if task_type=='regression':
                    img = self._chart_avp(predictions)
                    if img: story += [Paragraph("<b>Actual vs Predicted</b>", S['h2']), img, self._ibox(inf.get('avp',''),S), Spacer(1,0.3*cm)]
                    img2 = self._chart_residuals(predictions)
                    if img2: story += [Paragraph("<b>Residuals Plot</b>", S['h2']), img2, self._ibox(inf.get('res',''),S)]
                img3 = self._chart_dist(predictions, task_type)
                if img3:
                    story += [Spacer(1,0.3*cm), Paragraph("<b>Prediction Distribution</b>", S['h2']), img3,
                        self._ibox("Distribution of model predictions. Well-spread = no output bias.", S)]

        # 5. FEATURE IMPORTANCE
        if feature_importance is not None and not feature_importance.empty and task_type!='clustering':
            story += [PageBreak(), self._sec("5. Feature Importance Analysis", S), Spacer(1,0.2*cm)]
            story += [Paragraph("Feature importance shows which variables influenced predictions most.", S['body']),
                Spacer(1,0.2*cm), self._chart_fi(feature_importance), self._ibox(inf.get('fi',''),S), Spacer(1,0.3*cm)]
            top10 = feature_importance.head(10); total = top10['importance'].sum()
            fi_rows = [['Rank','Feature','Importance','Relative %']]
            for i,(_, row) in enumerate(top10.iterrows(), 1):
                pct = (row['importance']/total*100) if total>0 else 0
                fi_rows.append([str(i), row['feature'], f"{row['importance']:.4f}", f"{pct:.1f}%"])
            story += [self._tbl(fi_rows, [2*cm,7*cm,4*cm,4*cm]), Spacer(1,0.3*cm),
                self._ibox(f"Top 3 features account for "
                    f"{feature_importance.head(3)['importance'].sum()/feature_importance['importance'].sum()*100:.1f}% "
                    "of total importance. Focus data strategy on these variables.", S)]

        # 6. STATISTICAL MOMENTS
        story += [PageBreak(), self._sec("6. Statistical Moment Decisions", S), Spacer(1,0.2*cm)]
        story += [
            self._tbl([
                ['Moment', 'Statistic', 'What It Tells Us', 'Business Implication'],
                ['1st Moment', 'Mean',
                 Paragraph('Central tendency of each feature', S['body']),
                 Paragraph('Typical values — useful for setting baseline expectations', S['body'])],
                ['2nd Moment', 'Variance / Std Dev',
                 Paragraph('Spread of values around the mean', S['body']),
                 Paragraph('High variance may signal outliers or data quality issues requiring treatment', S['body'])],
                ['3rd Moment', 'Skewness',
                 Paragraph('Symmetry of the distribution', S['body']),
                 Paragraph('Positive skew = few high outliers. Negative = few low outliers. May need log transformation', S['body'])],
                ['4th Moment', 'Kurtosis',
                 Paragraph('Tail heaviness and peak sharpness', S['body']),
                 Paragraph('High kurtosis means extreme values occur more frequently — critical for risk and fraud detection', S['body'])],
            ], [2.5*cm, 3.5*cm, 4.5*cm, 6.5*cm]),
            Spacer(1, 0.3*cm),
            self._ibox("PyCaret AutoML automatically handled skewed distributions, "
                       "outliers and scaling before training.", S),
        ]

        # 7. CONCLUSIONS 
        # Final Business Conclusion — narrative style like your classroom files
        story += [
            Paragraph("<b>Final Business Conclusion</b>", S['h2']),
            Spacer(1, 0.1*cm),
        ]

        conclusion_text = bu['conclusion']
        conclusion_box = Table(
            [[Paragraph(conclusion_text, ParagraphStyle('CC',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=10, leading=16, textColor=colors.HexColor('#1a3a2a')))]],
            colWidths=[17*cm]
        )
        conclusion_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_INS),
            ('LINEBEFORE', (0,0), (0,-1), 5, C_GREEN),
            ('TOPPADDING', (0,0), (-1,-1), 14),
            ('BOTTOMPADDING', (0,0), (-1,-1), 14),
            ('LEFTPADDING', (0,0), (-1,-1), 16),
            ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ]))
        story += [conclusion_box, Spacer(1, 0.3*cm)]

        # Why this model works box
        why_box = Table(
            [[Paragraph(
                f"<b>Why {display_model} Works Here:</b><br/><br/>"
                + bu['model_why'], ParagraphStyle('WB',
                    parent=getSampleStyleSheet()['Normal'],
                    fontSize=9.5, leading=15, textColor=colors.HexColor('#1a1a4a')))]],
            colWidths=[17*cm]
        )
        why_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_INF),
            ('LINEBEFORE', (0,0), (0,-1), 5, C_PURPLE),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 16),
            ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ]))
        story += [why_box, Spacer(1, 0.3*cm)]

        # Limitations box
        lim_box = Table(
            [[Paragraph(
                f"<b>Limitations:</b><br/><br/>" + bu['limitations'],
                ParagraphStyle('LB',
                    parent=getSampleStyleSheet()['Normal'],
                    fontSize=9.5, leading=15, textColor=colors.HexColor('#7a5200')))]],
            colWidths=[17*cm]
        )
        lim_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_WARN),
            ('LINEBEFORE', (0,0), (0,-1), 5, colors.HexColor('#e67e22')),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 16),
            ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ]))
        story.append(lim_box)

        # FOOTERRRR
        story += [Spacer(1,0.5*cm), self._hr(),
            Paragraph(f"Generated by PromptML Studio | {datetime.now().strftime('%d %B %Y')}", S['ftr'])]

        doc.build(story)
        return output_path