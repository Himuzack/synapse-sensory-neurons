"""
Debug Version - Sensory Neurons Scraper
This version will show us exactly what's failing.
"""
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

def debug_environment():
    """Debug the environment and show what's available."""
    print("🔍 DEBUGGING ENVIRONMENT:")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    print("\n📋 ENVIRONMENT VARIABLES:")
    for key in ['TARGET_URL', 'SYNAPSE_HUB_URL', 'SENSORY_API_KEY', 'PRIORITY']:
        value = os.getenv(key, 'NOT SET')
        print(f"{key}: {value}")
    
    print("\n📦 CHECKING IMPORTS:")
    try:
        import requests
        print("✅ requests imported successfully")
    except Exception as e:
        print(f"❌ requests import failed: {e}")
    
    try:
        from playwright.async_api import async_playwright
        print("✅ playwright imported successfully")
    except Exception as e:
        print(f"❌ playwright import failed: {e}")
    
    try:
        import asyncio
        print("✅ asyncio imported successfully")
    except Exception as e:
        print(f"❌ asyncio import failed: {e}")

def create_test_files():
    """Create test files to ensure the workflow can find them."""
    print("\n📁 CREATING TEST FILES:")
    
    try:
        # Create screenshots directory
        screenshots_dir = Path("screenshots")
        screenshots_dir.mkdir(exist_ok=True)
        print(f"✅ Created directory: {screenshots_dir}")
        
        # Create a test screenshot file
        test_screenshot = screenshots_dir / "test-screenshot.txt"
        with open(test_screenshot, 'w') as f:
            f.write(f"Test screenshot created at {datetime.now()}")
        print(f"✅ Created test file: {test_screenshot}")
        
        # Create results.json
        import json
        test_result = {
            "status": "debug_test",
            "timestamp": datetime.now().isoformat(),
            "message": "This is a debug test to ensure files are created"
        }
        
        with open("results.json", 'w') as f:
            json.dump(test_result, f, indent=2)
        print("✅ Created results.json")
        
        # List all files created
        print(f"\n📂 Files in current directory: {os.listdir('.')}")
        print(f"📂 Files in screenshots: {os.listdir('screenshots')}")
        
    except Exception as e:
        print(f"❌ Error creating files: {e}")
        traceback.print_exc()

def simple_scrape_test():
    """Test simple scraping without complex dependencies."""
    print("\n🌐 TESTING SIMPLE SCRAPING:")
    
    target_url = os.getenv('TARGET_URL', 'https://httpbin.org/html')
    print(f"Target URL: {target_url}")
    
    try:
        import requests
        
        print("📡 Making HTTP request...")
        response = requests.get(target_url, timeout=10)
        print(f"✅ Response status: {response.status_code}")
        print(f"✅ Content length: {len(response.text)}")
        print(f"✅ Content preview: {response.text[:200]}...")
        
        return {
            "success": True,
            "status_code": response.status_code,
            "content_length": len(response.text),
            "url": target_url
        }
        
    except Exception as e:
        print(f"❌ Simple scraping failed: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "url": target_url
        }

def main():
    """Main debug function."""
    print("🧠 SENSORY NEURONS DEBUG MODE")
    print("=" * 50)
    
    try:
        # Step 1: Debug environment
        debug_environment()
        
        # Step 2: Create test files
        create_test_files()
        
        # Step 3: Test simple scraping
        scrape_result = simple_scrape_test()
        
        # Step 4: Update results with debug info
        import json
        
        final_result = {
            "debug_mode": True,
            "timestamp": datetime.now().isoformat(),
            "environment_check": "completed",
            "files_created": True,
            "scrape_test": scrape_result,
            "status": "debug_completed"
        }
        
        with open("results.json", 'w') as f:
            json.dump(final_result, f, indent=2)
        
        print("\n🎯 DEBUG COMPLETED SUCCESSFULLY!")
        print("✅ All files should now be created")
        print("✅ Check the artifacts for detailed debug info")
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR IN DEBUG:")
        print(f"Error: {e}")
        traceback.print_exc()
        
        # Still try to create a results file with the error
        try:
            import json
            error_result = {
                "debug_mode": True,
                "status": "debug_failed",
                "error": str(e),
                "traceback": traceback.format_exc(),
                "timestamp": datetime.now().isoformat()
            }
            
            with open("results.json", 'w') as f:
                json.dump(error_result, f, indent=2)
                
        except:
            print("❌ Could not even create error results file")
        
        # Exit with error code
        sys.exit(1)

if __name__ == "__main__":
    main()
