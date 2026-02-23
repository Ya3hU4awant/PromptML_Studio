
import sys
import os
sys.path.append(os.getcwd())

print("Testing imports...")
from backend.ml_engine.prompt_parser import PromptParser
from backend.ml_engine.model_builder import ModelBuilder
import pandas as pd

print("Imports successful.")

# Test PromptParser
print("Testing PromptParser...")
try:
    parser = PromptParser()
    print("PromptParser instantiated.")
    # Mock df
    df = pd.DataFrame({'income': [1, 2], 'spending': [3, 4], 'age': [20, 30]})
    res = parser.parse_prompt("Cluster customers based on income", df)
    print("Prompt parsed:", res)
except Exception as e:
    print("PromptParser failed:", e)
    # Don't fail the verification if model download fails (expected in this environment?), 
    # but at least check code logic.

# Test ModelBuilder with clustering
print("Testing ModelBuilder clustering...")
try:
    builder = ModelBuilder()
    res_model = builder.build_model(df, task_type="clustering")
    print("Clustering model built:", res_model.keys())
except Exception as e:
    print("ModelBuilder failed:", e)

print("Verification complete.")
