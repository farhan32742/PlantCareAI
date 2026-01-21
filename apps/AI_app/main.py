import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from PlantCare_AI.utils.model_loader import ModelLoader


def check_model_loader():
    """
    Check if the ModelLoader is working correctly.
    Tests loading the LLM model.
    """
    print("=" * 60)
    print("🔍 MODEL LOADER CHECK")
    print("=" * 60)
    
    # Check 1: Initialize ModelLoader
    print("\n✓ Check 1: Initializing ModelLoader...")
    try:
        model_loader = ModelLoader(model_provider="groq")
        print(f"  ✅ ModelLoader initialized successfully!")
        print(f"  🤖 Provider: {model_loader.model_provider}")
    except Exception as e:
        print(f"  ❌ Error initializing ModelLoader: {str(e)}")
        return False
    
    # Check 2: Load LLM Model
    print("\n✓ Check 2: Loading LLM model...")
    try:
        llm = model_loader.load_llm()
        print(f"  ✅ LLM model loaded successfully!")
        print(f"  🔑 API Key Status: {'Loaded' if os.getenv('GROQ_API_KEY') else 'Not found'}")
        print(f"  📦 LLM Object: {type(llm).__name__}")
    except Exception as e:
        print(f"  ❌ Error loading LLM model: {str(e)}")
        return False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("✅ MODEL LOADER IS WORKING!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = check_model_loader()
    if not success:
        print("\n❌ Model loader check failed. Please check the errors above.")
        exit(1)
    else:
        print("\n🚀 ModelLoader is ready to use!")
