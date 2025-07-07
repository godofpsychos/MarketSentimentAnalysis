#!/usr/bin/env python3
"""
Test script to verify environment variable paths are working correctly
This script loads environment variables and checks if all paths are resolved properly
"""

import os
import sys
from pathlib import Path

def load_env_file(env_file_path):
    """Load environment variables from a .env file"""
    if not os.path.exists(env_file_path):
        print(f"❌ Environment file not found: {env_file_path}")
        return False
    
    print(f"📄 Loading environment from: {env_file_path}")
    
    with open(env_file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Simple variable substitution for ${BASE_DIR}
                if '${BASE_DIR}' in value:
                    base_dir = os.getenv('BASE_DIR', '/home/tarun/MarketSentimentAnalysis')
                    value = value.replace('${BASE_DIR}', base_dir)
                os.environ[key] = value
    
    return True

def test_paths():
    """Test all path environment variables"""
    print("\n🔍 Testing Environment Variable Paths")
    print("=" * 50)
    
    # Path variables to test
    path_vars = [
        'BASE_DIR',
        'SENTIMENT_DB_PATH',
        'AUTH_DB_PATH',
        'FUNDAMENTAL_BASE_DIR',
        'PROFITABILITY_FILE',
        'VALUATION_FILE',
        'GROWTH_FILE',
        'LIQUIDITY_FILE',
        'CCC_FILE',
        'REPORT_CSV_PATH',
        'STOCKS_LIST_PATH',
        'NEWS_JSON_PATH',
        'RECENT_NEWS_PATH',
        'SENTIMENT_RESULTS_PATH',
        'LOG_FILE',
        'ACCESS_LOG_FILE',
        'ERROR_LOG_FILE'
    ]
    
    all_good = True
    
    for var in path_vars:
        path = os.getenv(var)
        if path:
            # Check if path exists or if parent directory exists
            path_obj = Path(path)
            parent_exists = path_obj.parent.exists()
            file_exists = path_obj.exists()
            
            if file_exists:
                status = "✅ EXISTS"
            elif parent_exists:
                status = "📁 PARENT EXISTS"
            else:
                status = "❌ MISSING"
                all_good = False
            
            print(f"{var:<25} = {path}")
            print(f"{'Status:':<25} {status}")
            print("-" * 50)
        else:
            print(f"{var:<25} = NOT SET ❌")
            all_good = False
            print("-" * 50)
    
    return all_good

def main():
    """Main function"""
    print("🧪 Environment Variable Path Tester")
    print("=" * 50)
    
    # Test different environment files
    env_files = [
        'backend.env.local',
        'backend.env',
        'cpanel.env'
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"\n📋 Testing {env_file}")
            print("=" * 30)
            
            # Clear environment for clean test
            for key in list(os.environ.keys()):
                if key.startswith(('BASE_DIR', 'SENTIMENT_', 'AUTH_', 'FUNDAMENTAL_', 
                                 'PROFITABILITY_', 'VALUATION_', 'GROWTH_', 'LIQUIDITY_',
                                 'CCC_', 'REPORT_', 'STOCKS_', 'NEWS_', 'RECENT_',
                                 'LOG_', 'ACCESS_', 'ERROR_')):
                    del os.environ[key]
            
            # Load environment file
            if load_env_file(env_file):
                all_good = test_paths()
                if all_good:
                    print(f"✅ All paths in {env_file} are configured correctly!")
                else:
                    print(f"⚠️  Some paths in {env_file} need attention")
            print("\n" + "=" * 50)
    
    print("\n🎉 Environment testing complete!")
    print("💡 Tips:")
    print("   - Make sure BASE_DIR is set correctly for your environment")
    print("   - Create missing directories as needed")
    print("   - Update paths in environment files if you move the project")

if __name__ == "__main__":
    main() 