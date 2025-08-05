"""
Sensory Neurons - Simple Learning Scraper
Simplified version for reliable GitHub Actions execution.
"""
import os
import json
import requests
from datetime import datetime
from pathlib import Path

def main():
    target_url = os.getenv('TARGET_URL', 'https://example.com')
    hub_url = os.getenv('SYNAPSE_HUB_URL')
    api_key = os.getenv('SENSORY_API_KEY')
    priority = os.getenv('PRIORITY', 'normal')
    
    print(f"🧠 Sensory Neurons starting...")
    print(f"Target URL: {target_url}")
    print(f"Hub URL: {hub_url}")
    print(f"Priority: {priority}")
    
    # Create directories
    Path("screenshots").mkdir(exist_ok=True)
    
    result = {
        "job_id": f"sensory-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "url": target_url,
        "status": "started",
        "component": "sensory-neurons",
        "timestamp": datetime.now().isoformat(),
        "data": {}
    }
    
    try:
        print(f"📄 Fetching page: {target_url}")
        
        # Simple HTTP request (no browser automation for now)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(target_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Page fetched successfully: {response.status_code}")
        
        # Simple content extraction
        content = response.text
        title = "Extracted Title"
        
        # Try to extract title from HTML
        if '<title>' in content:
            start = content.find('<title>') + 7
            end = content.find('</title>')
            if end > start:
                title = content[start:end].strip()
        
        # Create a simple "screenshot" placeholder
        screenshot_path = f"screenshots/page-{result['job_id']}.txt"
        with open(screenshot_path, 'w') as f:
            f.write(f"Screenshot placeholder for {target_url}\n")
            f.write(f"Captured at: {datetime.now().isoformat()}\n")
            f.write(f"Status: {response.status_code}\n")
            f.write(f"Content length: {len(content)} characters\n")
        
        print(f"📸 Screenshot placeholder saved: {screenshot_path}")
        
        # Update result
        result.update({
            "status": "completed",
            "data": {
                "title": title,
                "status_code": response.status_code,
                "content_length": len(content),
                "text_preview": content[:500] + "..." if len(content) > 500 else content,
                "screenshot": screenshot_path,
                "extraction_method": "simple_http_request"
            },
            "metrics": {
                "load_time": "< 30s",
                "success_rate": 1.0,
                "method": "requests_library"
            }
        })
        
        print("✅ Content extraction completed successfully")
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        result.update({
            "status": "failed",
            "error": str(e)
        })
    
    # Save results
    print("💾 Saving results...")
    with open("results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("📄 Results saved to results.json")
    
    # Send callback to hub if configured
    if hub_url and api_key:
        try:
            print("📡 Sending callback to hub...")
            callback_response = requests.post(
                f"{hub_url}/api/v1/callbacks/sensory",
                json=result,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            if callback_response.status_code == 200:
                print("📡 Callback sent to hub successfully")
            else:
                print(f"⚠️ Callback failed: {callback_response.status_code}")
        except Exception as e:
            print(f"⚠️ Callback error: {e}")
    else:
        print("⚠️ Hub URL or API key not configured - skipping callback")
    
    print(f"🎯 Job completed: {result['status']}")
    return result

if __name__ == "__main__":
    main()
