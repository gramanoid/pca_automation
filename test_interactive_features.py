"""
Test script to verify interactive features load correctly
Run this locally first before testing on Streamlit Cloud
"""

import sys
import importlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Features to test
FEATURES_TO_TEST = [
    {
        'name': 'Data Preview',
        'imports': [
            ('pandas', 'pd'),
        ],
        'ui_components': []
    },
    {
        'name': 'File Validation',
        'imports': [],
        'ui_components': [
            'ui_components.file_upload.FileUploadComponent'
        ]
    },
    {
        'name': 'Progress Tracking',
        'imports': [],
        'ui_components': [
            'ui_components.progress_display.ProgressDisplay'
        ]
    },
    {
        'name': 'Smart Caching',
        'imports': [],
        'ui_components': [
            'ui_components.smart_suggestions.SmartSuggestions'
        ]
    },
    {
        'name': 'Error Recovery',
        'imports': [],
        'ui_components': [
            'ui_components.error_recovery.ErrorRecoveryHandler',
            'ui_components.error_recovery.with_error_recovery'
        ]
    },
    {
        'name': 'Enhanced Validation',
        'imports': [
            ('plotly', None),
            ('plotly.graph_objects', 'go'),
            ('plotly.express', 'px')
        ],
        'ui_components': [
            'ui_components.validation_dashboard_enhanced.EnhancedValidationDashboard'
        ]
    }
]

def test_import(module_path, alias=None):
    """Test if a module can be imported"""
    try:
        if '.' in module_path and module_path.startswith('ui_components'):
            # Handle ui_components imports
            parts = module_path.split('.')
            module_name = '.'.join(parts[:-1])
            class_name = parts[-1]
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"  ✅ {module_path}")
                return True
            else:
                print(f"  ❌ {module_path} - Class {class_name} not found in module")
                return False
        else:
            # Regular imports
            module = importlib.import_module(module_path)
            print(f"  ✅ {module_path}")
            return True
    except ImportError as e:
        print(f"  ❌ {module_path} - ImportError: {e}")
        return False
    except Exception as e:
        print(f"  ❌ {module_path} - Error: {type(e).__name__}: {e}")
        return False

def main():
    print("Testing Interactive Features Import Compatibility")
    print("=" * 50)
    
    results = {}
    
    for feature in FEATURES_TO_TEST:
        print(f"\n{feature['name']}:")
        
        feature_ok = True
        
        # Test regular imports
        if feature['imports']:
            print("  Regular imports:")
            for import_spec in feature['imports']:
                if isinstance(import_spec, tuple):
                    module_path, alias = import_spec
                else:
                    module_path, alias = import_spec, None
                if not test_import(module_path, alias):
                    feature_ok = False
        
        # Test UI component imports
        if feature['ui_components']:
            print("  UI Components:")
            for component in feature['ui_components']:
                if not test_import(component):
                    feature_ok = False
        
        results[feature['name']] = feature_ok
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)
    
    working_features = [name for name, ok in results.items() if ok]
    failed_features = [name for name, ok in results.items() if not ok]
    
    print(f"\n✅ Working features ({len(working_features)}):")
    for feature in working_features:
        print(f"  - {feature}")
    
    print(f"\n❌ Failed features ({len(failed_features)}):")
    for feature in failed_features:
        print(f"  - {feature}")
    
    print("\nRecommendations:")
    if failed_features:
        print("1. Check requirements.txt for missing dependencies")
        print("2. Verify all __init__.py files exist in ui_components/")
        print("3. Test these features individually on Streamlit Cloud")
    else:
        print("All features should work on Streamlit Cloud!")

if __name__ == "__main__":
    main()