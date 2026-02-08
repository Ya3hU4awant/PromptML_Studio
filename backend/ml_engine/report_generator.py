"""
PromptML Studio - Report Generator Module
Generates professional PDF reports and visualizations
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import seaborn as sns


class ReportGenerator:
    """
    Generates comprehensive ML model reports with visualizations
    """
    
    def __init__(self):
        self.charts = {}
        
    def generate_visualizations(
        self,
        metrics: Dict[str, Any],
        feature_importance: pd.DataFrame,
        predictions: pd.DataFrame,
        task_type: str
    ) -> Dict[str, go.Figure]:
        """
        Generate all visualizations for the model
        
        Args:
            metrics: Model performance metrics
            feature_importance: Feature importance DataFrame
            predictions: Prediction results
            task_type: 'classification' or 'regression'
            
        Returns:
            Dictionary of Plotly figures
        """
        charts = {}
        
        # Feature importance chart
        if not feature_importance.empty:
            charts['feature_importance'] = self._create_feature_importance_chart(feature_importance)
        
        # Task-specific charts
        if task_type == 'classification':
            charts.update(self._create_classification_charts(metrics, predictions))
        elif task_type == "clustering":
            charts = {}
            charts["clusters"] = self.generate_clustering_visualization(viz_data)
            return charts
        else:
            charts.update(self._create_regression_charts(metrics, predictions))
        
        # Metrics summary chart
        charts['metrics_summary'] = self._create_metrics_summary_chart(metrics, task_type)
        
        self.charts = charts
        return charts
    
    def _create_feature_importance_chart(self, feature_importance: pd.DataFrame) -> go.Figure:
        """Create feature importance bar chart"""
        
        # Take top 15 features
        top_features = feature_importance.head(15)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=top_features['importance'],
            y=top_features['feature'],
            orientation='h',
            marker=dict(
                color=top_features['importance'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Importance")
            ),
            text=top_features['importance'].round(3),
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Top Feature Importance',
            xaxis_title='Importance Score',
            yaxis_title='Features',
            height=500,
            template='plotly_dark',
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def _create_classification_charts(
        self,
        metrics: Dict[str, Any],
        predictions: pd.DataFrame
    ) -> Dict[str, go.Figure]:
        """Create classification-specific charts"""
        
        charts = {}
        
        # Confusion Matrix
        if 'confusion_matrix' in metrics:
            charts['confusion_matrix'] = self._create_confusion_matrix(metrics['confusion_matrix'])
        
        # Metrics comparison
        charts['metrics_comparison'] = self._create_classification_metrics_chart(metrics)
        
        return charts
    
    def _create_confusion_matrix(self, cm: List[List[int]]) -> go.Figure:
        """Create confusion matrix heatmap"""
        
        cm_array = np.array(cm)
        
        # Create labels
        labels = [f'Class {i}' for i in range(len(cm_array))]
        
        fig = go.Figure(data=go.Heatmap(
            z=cm_array,
            x=labels,
            y=labels,
            colorscale='Blues',
            text=cm_array,
            texttemplate='%{text}',
            textfont={"size": 16},
            showscale=True
        ))
        
        fig.update_layout(
            title='Confusion Matrix',
            xaxis_title='Predicted Label',
            yaxis_title='True Label',
            height=500,
            template='plotly_dark'
        )
        
        return fig
    
    def _create_classification_metrics_chart(self, metrics: Dict[str, Any]) -> go.Figure:
        """Create bar chart of classification metrics"""
        
        metric_names = []
        metric_values = []
        
        for key in ['accuracy', 'precision', 'recall', 'f1_score']:
            if key in metrics:
                metric_names.append(key.replace('_', ' ').title())
                metric_values.append(metrics[key])
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=metric_names,
            y=metric_values,
            marker=dict(
                color=metric_values,
                colorscale='Viridis',
                showscale=False
            ),
            text=[f'{v:.2%}' for v in metric_values],
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Classification Metrics',
            xaxis_title='Metric',
            yaxis_title='Score',
            yaxis=dict(range=[0, 1]),
            height=400,
            template='plotly_dark'
        )
        
        return fig
    
    def _create_regression_charts(
        self,
        metrics: Dict[str, Any],
        predictions: pd.DataFrame
    ) -> Dict[str, go.Figure]:
        """Create regression-specific charts"""
        
        charts = {}
        
        # Actual vs Predicted scatter plot
        if 'prediction_label' in predictions.columns:
            charts['actual_vs_predicted'] = self._create_actual_vs_predicted_chart(predictions)
        
        # Residuals plot
        if 'prediction_label' in predictions.columns:
            charts['residuals'] = self._create_residuals_chart(predictions)
        
        return charts

    #Visualization for clustering
    def generate_clustering_visualization(self, viz_df):
        import plotly.express as px

        fig = px.scatter(
            viz_df,
            x="pca_1",
            y="pca_2",
            color="cluster",
            title="Cluster Visualization (PCA)"
        )
        return fig

    
    def _create_actual_vs_predicted_chart(self, predictions: pd.DataFrame) -> go.Figure:
        """Create actual vs predicted scatter plot"""
        
        # Get actual and predicted values
        y_true = predictions.iloc[:, 0].values  # First column is usually actual
        y_pred = predictions['prediction_label'].values
        
        fig = go.Figure()
        
        # Scatter plot
        fig.add_trace(go.Scatter(
            x=y_true,
            y=y_pred,
            mode='markers',
            marker=dict(
                size=8,
                color=y_pred,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Predicted")
            ),
            name='Predictions'
        ))
        
        # Perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Perfect Prediction'
        ))
        
        fig.update_layout(
            title='Actual vs Predicted Values',
            xaxis_title='Actual Values',
            yaxis_title='Predicted Values',
            height=500,
            template='plotly_dark'
        )
        
        return fig
    
    def _create_residuals_chart(self, predictions: pd.DataFrame) -> go.Figure:
        """Create residuals plot"""
        
        # Calculate residuals
        y_true = predictions.iloc[:, 0].values
        y_pred = predictions['prediction_label'].values
        residuals = y_true - y_pred
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=y_pred,
            y=residuals,
            mode='markers',
            marker=dict(
                size=8,
                color=np.abs(residuals),
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Abs Residual")
            )
        ))
        
        # Zero line
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        
        fig.update_layout(
            title='Residuals Plot',
            xaxis_title='Predicted Values',
            yaxis_title='Residuals',
            height=500,
            template='plotly_dark'
        )
        
        return fig
    
    def _create_metrics_summary_chart(self, metrics: Dict[str, Any], task_type: str) -> go.Figure:
        """Create summary metrics gauge chart"""
        
        if task_type == 'classification':
            primary_metric = metrics.get('accuracy', 0)
            metric_name = 'Accuracy'
        else:
            primary_metric = metrics.get('r2_score', 0)
            metric_name = 'R² Score'
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=primary_metric,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Model {metric_name}"},
            delta={'reference': 0.8},
            gauge={
                'axis': {'range': [None, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.5], 'color': "lightgray"},
                    {'range': [0.5, 0.75], 'color': "gray"},
                    {'range': [0.75, 1], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.9
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            template='plotly_dark'
        )
        
        return fig
    
    def generate_pdf_report(
        self,
        output_path: str,
        metrics: Dict[str, Any],
        feature_importance: pd.DataFrame,
        task_type: str,
        dataset_info: Dict[str, Any] = None
    ) -> str:
        """
        Generate comprehensive PDF report
        
        Args:
            output_path: Path to save PDF
            metrics: Model metrics
            feature_importance: Feature importance data
            task_type: 'classification' or 'regression'
            dataset_info: Optional dataset information
            
        Returns:
            Path to generated PDF
        """
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("PromptML Studio", title_style))
        story.append(Paragraph("ML Model Performance Report", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Task Type: {task_type.title()}", styles['Normal']))
        story.append(Paragraph(f"Model: {metrics.get('model_name', 'Unknown')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Dataset Information
        if dataset_info:
            story.append(Paragraph("Dataset Information", heading_style))
            dataset_data = [
                ['Property', 'Value'],
                ['Total Samples', str(dataset_info.get('n_samples', 'N/A'))],
                ['Features', str(dataset_info.get('n_features', 'N/A'))],
                ['Target Column', str(dataset_info.get('target_column', 'N/A'))]
            ]
            dataset_table = Table(dataset_data, colWidths=[3*inch, 3*inch])
            dataset_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(dataset_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Model Performance Metrics
        story.append(Paragraph("Model Performance Metrics", heading_style))
        
        if task_type == 'classification':
            metrics_data = [
                ['Metric', 'Value'],
                ['Accuracy', f"{metrics.get('accuracy', 0):.2%}"],
                ['Precision', f"{metrics.get('precision', 0):.2%}"],
                ['Recall', f"{metrics.get('recall', 0):.2%}"],
                ['F1 Score', f"{metrics.get('f1_score', 0):.2%}"]
            ]
            if 'auc' in metrics:
                metrics_data.append(['AUC', f"{metrics.get('auc', 0):.4f}"])
        else:
            metrics_data = [
                ['Metric', 'Value'],
                ['R² Score', f"{metrics.get('r2_score', 0):.4f}"],
                ['RMSE', f"{metrics.get('rmse', 0):.4f}"],
                ['MAE', f"{metrics.get('mae', 0):.4f}"],
                ['MSE', f"{metrics.get('mse', 0):.4f}"]
            ]
            if 'mape' in metrics:
                metrics_data.append(['MAPE', f"{metrics.get('mape', 0):.2f}%"])
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Feature Importance
        if not feature_importance.empty:
            story.append(PageBreak())
            story.append(Paragraph("Top Feature Importance", heading_style))
            
            top_features = feature_importance.head(10)
            feature_data = [['Feature', 'Importance Score']]
            for _, row in top_features.iterrows():
                feature_data.append([row['feature'], f"{row['importance']:.4f}"])
            
            feature_table = Table(feature_data, colWidths=[3*inch, 3*inch])
            feature_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(feature_table)
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Generated by PromptML Studio - AI-Powered AutoML Platform", 
                              styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return output_path


if __name__ == "__main__":
    # Test report generator
    print("🧪 Testing Report Generator\n")
    
    # Sample metrics
    metrics = {
        'model_name': 'Random Forest Classifier',
        'accuracy': 0.92,
        'precision': 0.89,
        'recall': 0.91,
        'f1_score': 0.90,
        'confusion_matrix': [[45, 5], [3, 47]]
    }
    
    # Sample feature importance
    feature_importance = pd.DataFrame({
        'feature': ['feature_1', 'feature_2', 'feature_3'],
        'importance': [0.45, 0.35, 0.20]
    })
    
    # Generate report
    generator = ReportGenerator()
    pdf_path = "test_report.pdf"
    generator.generate_pdf_report(pdf_path, metrics, feature_importance, 'classification')
    
    print(f"✅ Report generated: {pdf_path}")
