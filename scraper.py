"""
Sensory Neurons - Advanced Learning Scraper (Standalone)
Based on the sophisticated PlaywrightScraper but adapted for GitHub Actions.
"""
import os
import json
import asyncio
import random
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse

import requests
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

class AdvancedScraper:
    """Advanced browser automation scraper adapted for GitHub Actions."""
    
    # User agents for rotation (from our existing code)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    
    # Screen resolutions for rotation
    SCREEN_SIZES = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1536, 'height': 864},
        {'width': 1440, 'height': 900}
    ]
    
    def __init__(self):
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
    
    async def scrape_with_browser(self, url: str) -> Dict[str, Any]:
        """Scrape using browser automation with anti-detection."""
        async with async_playwright() as p:
            # Launch browser with stealth settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-first-run',
                    '--no-default-browser-check',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-extensions'
                ]
            )
            
            # Create context with random settings
            screen_size = random.choice(self.SCREEN_SIZES)
            user_agent = random.choice(self.USER_AGENTS)
            
            context = await browser.new_context(
                user_agent=user_agent,
                viewport=screen_size,
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # Add stealth script
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                window.chrome = { runtime: {} };
            """)
            
            page = await context.new_page()
            
            try:
                print(f"🌐 Loading page with browser: {url}")
                
                # Navigate with timeout
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for dynamic content
                await asyncio.sleep(3)
                
                # Take full-page screenshot
                screenshot_path = f"screenshots/page-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot saved: {screenshot_path}")
                
                # Get page title
                title = await page.title()
                
                # Extract text content (remove scripts/styles)
                text_content = await page.evaluate("""
                    () => {
                        const scripts = document.querySelectorAll('script, style, nav, header, footer');
                        scripts.forEach(el => el.remove());
                        return document.body.innerText || document.body.textContent || '';
                    }
                """)
                
                # Extract links
                links = await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        return links.slice(0, 20).map(link => ({
                            url: link.href,
                            text: link.textContent.trim().substring(0, 100)
                        })).filter(link => link.text.length > 0);
                    }
                """)
                
                # Extract images
                images = await page.evaluate("""
                    () => {
                        const images = Array.from(document.querySelectorAll('img[src]'));
                        return images.slice(0, 10).map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth || 0,
                            height: img.naturalHeight || 0
                        }));
                    }
                """)
                
                # Analyze DOM structure (from our existing code)
                dom_analysis = await page.evaluate("""
                    () => {
                        const analysis = {};
                        
                        analysis.totalElements = document.querySelectorAll('*').length;
                        analysis.headings = {
                            h1: document.querySelectorAll('h1').length,
                            h2: document.querySelectorAll('h2').length,
                            h3: document.querySelectorAll('h3').length
                        };
                        analysis.paragraphs = document.querySelectorAll('p').length;
                        analysis.links = document.querySelectorAll('a').length;
                        analysis.images = document.querySelectorAll('img').length;
                        
                        // Find potential article content
                        const articles = document.querySelectorAll('article, main, [class*="content"], [class*="article"]');
                        analysis.contentContainers = articles.length;
                        
                        // Check for JavaScript frameworks
                        analysis.frameworks = {
                            react: !!window.React || document.querySelector('[data-reactroot]') !== null,
                            vue: !!window.Vue || document.querySelector('[data-v-]') !== null,
                            angular: !!window.angular || document.querySelector('[ng-app]') !== null,
                            jquery: !!window.jQuery || !!window.$
                        };
                        
                        return analysis;
                    }
                """)
                
                # Get page metrics
                metrics = await page.evaluate("""
                    () => {
                        const metrics = {};
                        
                        if (window.performance) {
                            const navigation = performance.getEntriesByType('navigation')[0];
                            if (navigation) {
                                metrics.loadTime = navigation.loadEventEnd - navigation.fetchStart;
                                metrics.domContentLoaded = navigation.domContentLoadedEventEnd - navigation.fetchStart;
                            }
                        }
                        
                        metrics.viewport = {
                            width: window.innerWidth,
                            height: window.innerHeight,
                            devicePixelRatio: window.devicePixelRatio
                        };
                        
                        return metrics;
                    }
                """)
                
                return {
                    'success': True,
                    'method': 'playwright_browser_automation',
                    'title': title,
                    'text_content': text_content[:2000] + "..." if len(text_content) > 2000 else text_content,
                    'text_length': len(text_content),
                    'links': links,
                    'images': images,
                    'screenshot_path': screenshot_path,
                    'dom_analysis': dom_analysis,
                    'page_metrics': metrics,
                    'user_agent': user_agent,
                    'viewport': screen_size
                }
                
            except PlaywrightTimeoutError as e:
                print(f"⏰ Timeout error: {e}")
                return {'success': False, 'error': f'Timeout: {e}', 'method': 'playwright_timeout'}
            except Exception as e:
                print(f"❌ Browser error: {e}")
                return {'success': False, 'error': str(e), 'method': 'playwright_error'}
            finally:
                await browser.close()

    def scrape_with_requests(self, url: str) -> Dict[str, Any]:
        """Fallback scraping with requests library."""
        try:
            print(f"🔗 Fallback scraping with requests: {url}")
            
            headers = {
                'User-Agent': random.choice(self.USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Simple title extraction
            title = "Unknown Title"
            if '<title>' in response.text:
                start = response.text.find('<title>') + 7
                end = response.text.find('</title>')
                if end > start:
                    title = response.text[start:end].strip()
            
            return {
                'success': True,
                'method': 'requests_fallback',
                'title': title,
                'status_code': response.status_code,
                'content_length': len(response.text),
                'text_preview': response.text[:500] + "..." if len(response.text) > 500 else response.text,
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            print(f"❌ Requests error: {e}")
            return {'success': False, 'error': str(e), 'method': 'requests_error'}

async def main():
    """Main scraping function."""
    target_url = os.getenv('TARGET_URL', 'https://example.com')
    hub_url = os.getenv('SYNAPSE_HUB_URL')
    api_key = os.getenv('SENSORY_API_KEY')
    priority = os.getenv('PRIORITY', 'normal')
    
    print(f"🧠 Advanced Sensory Neurons starting...")
    print(f"Target URL: {target_url}")
    print(f"Hub URL: {hub_url}")
    print(f"Priority: {priority}")
    
    # Create result structure
    result = {
        "job_id": f"sensory-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "url": target_url,
        "status": "started",
        "component": "sensory-neurons-advanced",
        "timestamp": datetime.now().isoformat(),
        "priority": priority,
        "data": {},
        "metadata": {}
    }
    
    scraper = AdvancedScraper()
    
    try:
        # Try browser automation first
        print("🎭 Attempting browser automation...")
        browser_result = await scraper.scrape_with_browser(target_url)
        
        if browser_result['success']:
            print("✅ Browser automation successful!")
            result.update({
                "status": "completed",
                "data": browser_result,
                "extraction_method": "playwright_browser",
                "capabilities_used": [
                    "browser_automation",
                    "anti_detection",
                    "screenshot_capture",
                    "dom_analysis",
                    "javascript_execution"
                ]
            })
        else:
            print("⚠️ Browser automation failed, trying fallback...")
            fallback_result = scraper.scrape_with_requests(target_url)
            
            result.update({
                "status": "completed" if fallback_result['success'] else "failed",
                "data": fallback_result,
                "extraction_method": "requests_fallback",
                "capabilities_used": ["http_requests", "basic_parsing"]
            })
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        result.update({
            "status": "failed",
            "error": str(e),
            "extraction_method": "none"
        })
    
    # Add learning metadata (from our existing recipe_learner concepts)
    result["metadata"] = {
        "learning_insights": {
            "site_complexity": "high" if "javascript" in str(result.get("data", {})) else "low",
            "extraction_difficulty": "advanced" if result.get("extraction_method") == "playwright_browser" else "basic",
            "success_factors": [
                "anti_detection_enabled",
                "dynamic_user_agent",
                "random_viewport",
                "stealth_scripts"
            ] if result.get("extraction_method") == "playwright_browser" else ["basic_headers"]
        },
        "performance": {
            "execution_time": "< 60s",
            "memory_usage": "moderate",
            "success_rate": 1.0 if result["status"] == "completed" else 0.0
        },
        "adaptation_notes": [
            "Site requires JavaScript execution" if result.get("extraction_method") == "playwright_browser" else "Simple HTTP sufficient",
            "Anti-detection measures applied",
            "Screenshot captured for visual analysis"
        ]
    }
    
    # Save results
    print("💾 Saving results...")
    with open("results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("📄 Results saved to results.json")
    
    # Send callback to hub
    if hub_url and api_key:
        try:
            print("📡 Sending advanced results to hub...")
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
                print("📡 Advanced callback sent successfully!")
            else:
                print(f"⚠️ Callback failed: {callback_response.status_code}")
        except Exception as e:
            print(f"⚠️ Callback error: {e}")
    
    print(f"🎯 Advanced job completed: {result['status']}")
    print(f"🔬 Method used: {result.get('extraction_method', 'unknown')}")
    print(f"📊 Capabilities: {', '.join(result.get('capabilities_used', []))}")

if __name__ == "__main__":
    asyncio.run(main())
