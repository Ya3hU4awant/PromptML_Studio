"""
Quick Test Script for PromptML Studio
Tests core functionality without Streamlit
"""

import pandas as pd
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from backend.ml_engine.prompt_parser import PromptParser
from backend.ml_engine.model_builder import ModelBuilder
from backend.ml_engine.report_generator import ReportGenerator


def test_prompt_parser():
    """Test prompt parsing"""
    print("\n" + "="*60)
    print("🧪 Testing Prompt Parser")
    print("="*60)
    
    parser = PromptParser()
    
    test_cases = [
        "Predict house prices based on features",
        "Classify customer churn risk",
        "Forecast sales revenue",
        "Detect fraudulent transactions"
    ]
    
    for prompt in test_cases:
        result = parser.parse_prompt(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"  → Task Type: {result['task_type']}")
        print(f"  → Confidence: {result['confidence']:.0%}")
    
    print("\n✅ Prompt Parser Test Complete!")


def test_model_builder():
    """Test model building with sample data"""
    print("\n" + "="*60)
    print("🧪 Testing Model Builder")
    print("="*60)
    
    # Load sample data
    sample_path = Path(__file__).parent / "static" / "sample_data" / "house_prices.csv"
    
    if not sample_path.exists():
        print("❌ Sample data not found!")
        return
    
    print(f"\n📊 Loading data from: {sample_path}")
    df = pd.read_csv(sample_path)
    print(f"  → Loaded {len(df)} rows, {len(df.columns)} columns")
    
    # Parse prompt
    print("\n🔍 Parsing prompt...")
    parser = PromptParser()
    task_info = parser.parse_prompt("Predict house prices", df)
    
    print(f"  → Task Type: {task_info['task_type']}")
    print(f"  → Target Column: {task_info['target_column']}")
    
    # Build model (with smaller dataset for speed)
    print("\n🏗️ Building model (this may take 1-2 minutes)...")
    print("  Note: Using small sample for testing")
    
    # Use only first 100 rows for quick testing
    df_sample = df.head(100)
    
    try:
        builder = ModelBuilder()
        result = builder.build_model(
            df=df_sample,
            target_column=task_info['target_column'],
            task_type=task_info['task_type']
        )
        
        print("\n✅ Model trained successfully!")
        print(f"  → Model: {result['metrics'].get('model_name', 'Unknown')}")
        print(f"  → R² Score: {result['metrics'].get('r2_score', 0):.4f}")
        print(f"  → RMSE: {result['metrics'].get('rmse', 0):.2f}")
        
        # Test feature importance
        if not result['feature_importance'].empty:
            print(f"\n📊 Top 5 Important Features:")
            for idx, row in result['feature_importance'].head(5).iterrows():
                print(f"  {idx+1}. {row['feature']}: {row['importance']:.4f}")
        
        print("\n✅ Model Builder Test Complete!")
        return result
        
    except Exception as e:
        print(f"\n❌ Model building failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_report_generator(model_result):
    """Test report generation"""
    print("\n" + "="*60)
    print("🧪 Testing Report Generator")
    print("="*60)
    
    if model_result is None:
        print("⚠️  Skipping (no model result)")
        return
    
    try:
        generator = ReportGenerator()
        
        # Generate visualizations
        print("\n📊 Generating visualizations...")
        charts = generator.generate_visualizations(
            metrics=model_result['metrics'],
            feature_importance=model_result['feature_importance'],
            predictions=model_result['predictions'],
            task_type=model_result['task_type']
        )
        
        print(f"  → Generated {len(charts)} charts")
        
        # Generate PDF
        print("\n📄 Generating PDF report...")
        pdf_path = "test_report.pdf"
        
        dataset_info = {
            'n_samples': 100,
            'n_features': 10,
            'target_column': 'price'
        }
        
        generator.generate_pdf_report(
            output_path=pdf_path,
            metrics=model_result['metrics'],
            feature_importance=model_result['feature_importance'],
            task_type=model_result['task_type'],
            dataset_info=dataset_info
        )
        
        print(f"  → PDF saved to: {pdf_path}")
        print("\n✅ Report Generator Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Report generation failed: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 PromptML Studio - Component Tests")
    print("="*60)
    
    # Test 1: Prompt Parser
    test_prompt_parser()
    
    # Test 2: Model Builder
    model_result = test_model_builder()
    
    # Test 3: Report Generator
    test_report_generator(model_result)
    
    print("\n" + "="*60)
    print("🎉 All Tests Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Run the full app: streamlit run app.py")
    print("2. Upload your own data and test")
    print("3. Deploy to production (see DEPLOYMENT.md)")
    print("\n")


if __name__ == "__main__":
    main()
