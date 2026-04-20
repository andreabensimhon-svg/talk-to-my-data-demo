"""
CEO Data Agent - Test Script
Validates the demo setup and connectivity
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print(f"\n{'═' * 60}")
    print(f"  {text}")
    print(f"{'═' * 60}")

def print_status(name, success, message=""):
    icon = "✅" if success else "❌"
    print(f"  {icon} {name}: {message}")
    return success

def test_data_files():
    """Check if demo data files exist"""
    print_header("Testing Data Files")
    
    data_dir = Path(__file__).parent.parent / "data" / "output"
    expected_files = [
        "dim_date.csv",
        "dim_geography.csv", 
        "dim_offer.csv",
        "dim_content.csv",
        "dim_customer.csv",
        "fact_subscriptions.csv",
        "fact_content_views.csv",
        "fact_marketing.csv",
        "fact_surveys.csv"
    ]
    
    all_exist = True
    for filename in expected_files:
        filepath = data_dir / filename
        exists = filepath.exists()
        if exists:
            size = filepath.stat().st_size / 1024  # KB
            print_status(filename, True, f"{size:.1f} KB")
        else:
            print_status(filename, False, "Not found - run generate_data.py")
            all_exist = False
    
    return all_exist

def test_environment_variables():
    """Check required environment variables"""
    print_header("Testing Environment Variables")
    
    env_vars = {
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint URL",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key (or use managed identity)",
        "FABRIC_WORKSPACE_ID": "Microsoft Fabric workspace GUID",
        "FABRIC_SEMANTIC_MODEL_ID": "Semantic model GUID"
    }
    
    all_set = True
    for var, desc in env_vars.items():
        value = os.environ.get(var)
        if value:
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print_status(var, True, masked)
        else:
            print_status(var, False, f"Not set ({desc})")
            all_set = False
    
    return all_set

def test_azure_openai():
    """Test Azure OpenAI connectivity"""
    print_header("Testing Azure OpenAI Connectivity")
    
    try:
        from openai import AzureOpenAI
        
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        
        if not endpoint or not api_key:
            print_status("Azure OpenAI", False, "Missing credentials")
            return False
        
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print_status("Azure OpenAI", True, f"Response: {result}")
        return True
        
    except ImportError:
        print_status("Azure OpenAI", False, "openai package not installed")
        return False
    except Exception as e:
        print_status("Azure OpenAI", False, str(e))
        return False

def test_fabric_connection():
    """Test Fabric semantic model connection (placeholder)"""
    print_header("Testing Fabric Connection")
    
    workspace_id = os.environ.get("FABRIC_WORKSPACE_ID")
    model_id = os.environ.get("FABRIC_SEMANTIC_MODEL_ID")
    
    if not workspace_id or not model_id:
        print_status("Fabric", False, "Missing workspace/model IDs")
        return False
    
    # Note: Full Fabric testing requires authentication
    print_status("Fabric Config", True, f"Workspace: {workspace_id[:8]}...")
    print_status("Semantic Model", True, f"Model: {model_id[:8]}...")
    print("  ℹ️ Full connectivity test requires Fabric access")
    
    return True

def main():
    """Run all tests"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║            CEO Data Agent - Validation Tests                  ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    results = []
    
    # Test 1: Data files
    results.append(("Data Files", test_data_files()))
    
    # Test 2: Environment variables
    results.append(("Environment", test_environment_variables()))
    
    # Test 3: Azure OpenAI (only if env vars are set)
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        results.append(("Azure OpenAI", test_azure_openai()))
    else:
        print_header("Skipping Azure OpenAI Test")
        print("  ℹ️ Set AZURE_OPENAI_ENDPOINT to enable")
    
    # Test 4: Fabric connection
    if os.environ.get("FABRIC_WORKSPACE_ID"):
        results.append(("Fabric", test_fabric_connection()))
    else:
        print_header("Skipping Fabric Test")
        print("  ℹ️ Set FABRIC_WORKSPACE_ID to enable")
    
    # Summary
    print_header("SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        icon = "✅" if success else "❌"
        print(f"  {icon} {name}")
    
    print(f"\n  Results: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready for demo.\n")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the issues above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
