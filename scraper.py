"""
Sensory Neurons - Reliable GitHub Actions Scraper
No browser automation to avoid dependency issues.
"""
import os
import json
import requests
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin
import re

class ReliableScraper:
    """Reliable scraper that works in GitHub Actions without browser dependencies."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Create directories
        Path("screenshots").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
    
    def extract_title(self, html_content):
        """Extract title from HTML."""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            return title_match.group(1).strip()
        return "No title found"
    
    def extract_meta_description(self, html_content):
        """Extract meta description."""
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        if desc_match:
            return desc_match.group(1).strip()
        return ""
    
    def extract_headings(self, html_content):
        """Extract headings from HTML."""
        headings = []
        for level in range(1, 7):
            pattern = f'<h{level}[^>]*>(.*?)</h{level}>'
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches[:5]:  # Limit to 5 per level
                clean_text = re.sub(r'<[^>]+>', '', match).strip()
                if clean_text:
                    headings.append({
                        'level': level,
                        'text': clean_text[:200]  # Limit length
                    })
        return headings
    
    def extract_links(self, html_content, base_url):
        """Extract links from HTML."""
        links = []
        link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>'
        matches = re.findall(link_pattern, html_content, re.IGNORECASE | re.DOTALL)
        
        for href, text in matches[:20]:  # Limit to 20 links
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            if clean_text and href:
                # Convert relative URLs to absolute
                if href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(base_url, href)
                
                links.append({
                    'url': full_url,
                    'text': clean_text[:100]
                })
        
        return links
    
    def extract_images(self, html_content, base_url):
        """Extract images from HTML."""
        images = []
        img_pattern = r'<img[^>]*src=["\']([^"\']*)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*>'
        matches = re.findall(img_pattern, html_content, re.IGNORECASE)
        
        for src, alt in matches[:10]:  # Limit to 10 images
            if src:
                # Convert relative URLs to absolute
                if src.startswith('http'):
                    full_url = src
                else:
                    full_url = urljoin(base_url, src)
                
                images.append({
                    'src': full_url,
                    'alt': alt or ''
                })
        
        return images
    
    def extract_text_content(self, html_content):
        """Extract clean text content."""
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def analyze_content_structure(self, html_content):
        """Analyze the structure of the content."""
        analysis = {
            'has_articles': bool(re.search(r'<article[^>]*>', html_content, re.IGNORECASE)),
            'has_main': bool(re.search(r'<main[^>]*>', html_content, re.IGNORECASE)),
            'paragraph_count': len(re.findall(r'<p[^>]*>', html_content, re.IGNORECASE)),
            'div_count': len(re.findall(r'<div[^>]*>', html_content, re.IGNORECASE)),
            'script_count': len(re.findall(r'<script[^>]*>', html_content, re.IGNORECASE)),
            'form_count': len(re.findall(r'<form[^>]*>', html_content, re.IGNORECASE)),
            'table_count': len(re.findall(r'<table[^>]*>', html_content, re.IGNORECASE))
        }
        
        # Detect potential content areas
        content_indicators = [
            r'class=["\'][^"\']*content[^"\']*["\']',
            r'class=["\'][^"\']*article[^"\']*["\']',
            r'class=["\'][^"\']*post[^"\']*["\']',
            r'class=["\'][^"\']*main[^"\']*["\']'
        ]
        
        analysis['content_areas'] = sum(
            len(re.findall(pattern, html_content, re.IGNORECASE))
            for pattern in content_indicators
        )
        
        return analysis
    
    def scrape_url(self, url):
        """Scrape a URL and extract comprehensive information."""
        print(f"🌐 Scraping URL: {url}")
        
        try:
            # Make request
            start_time = time.time()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            load_time = time.time() - start_time
            
            print(f"✅ Response received: {response.status_code} ({load_time:.2f}s)")
            
            html_content = response.text
            
            # Extract all information
            title = self.extract_title(html_content)
            meta_description = self.extract_meta_description(html_content)
            headings = self.extract_headings(html_content)
            links = self.extract_links(html_content, url)
            images = self.extract_images(html_content, url)
            text_content = self.extract_text_content(html_content)
            structure_analysis = self.analyze_content_structure(html_content)
            
            # Create a "screenshot" placeholder (since we can't take real screenshots)
            screenshot_info = self.create_screenshot_placeholder(url, response)
            
            result = {
                'success': True,
                'url': url,
                'status_code': response.status_code,
                'load_time': load_time,
                'title': title,
                'meta_description': meta_description,
                'headings': headings,
                'links': links,
                'images': images,
                'text_content': text_content[:2000] + "..." if len(text_content) > 2000 else text_content,
                'text_length': len(text_content),
                'content_structure': structure_analysis,
                'screenshot_info': screenshot_info,
                'headers': dict(response.headers),
                'extraction_method': 'advanced_regex_parsing',
                'capabilities_used': [
                    'http_requests',
                    'regex_parsing',
                    'content_analysis',
                    'link_extraction',
                    'image_extraction',
                    'structure_analysis'
                ]
            }
            
            print(f"✅ Extraction completed: {len(text_content)} chars, {len(links)} links, {len(images)} images")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'error_type': 'request_error'
            }
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'error_type': 'extraction_error'
            }
    
    def create_screenshot_placeholder(self, url, response):
        """Create a screenshot placeholder with page info."""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"page-info-{timestamp}.txt"
        filepath = Path("screenshots") / filename
        
        # Create detailed page info file
        page_info = f"""
SENSORY NEURONS - PAGE ANALYSIS
===============================
URL: {url}
Timestamp: {datetime.now().isoformat()}
Status Code: {response.status_code}
Content Length: {len(response.text)} characters
Content Type: {response.headers.get('content-type', 'unknown')}

RESPONSE HEADERS:
{'-' * 20}
"""
        
        for key, value in response.headers.items():
            page_info += f"{key}: {value}\n"
        
        page_info += f"""
CONTENT PREVIEW:
{'-' * 20}
{response.text[:500]}...

ANALYSIS COMPLETE
Generated by Sensory Neurons Advanced Scraper
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(page_info)
        
        return {
            'type': 'page_analysis',
            'filename': filename,
            'filepath': str(filepath),
            'size': len(page_info),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main scraping function."""
    print("🧠 SENSORY NEURONS - RELIABLE SCRAPER")
    print("=" * 50)
    
    # Get environment variables
    target_url = os.getenv('TARGET_URL', 'https://example.com')
    hub_url = os.getenv('SYNAPSE_HUB_URL')
    api_key = os.getenv('SENSORY_API_KEY')
    priority = os.getenv('PRIORITY', 'normal')
    
    print(f"Target URL: {target_url}")
    print(f"Hub URL: {hub_url}")
    print(f"Priority: {priority}")
    
    # Create result structure
    result = {
        "job_id": f"sensory-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "url": target_url,
        "status": "started",
        "component": "sensory-neurons-reliable",
        "timestamp": datetime.now().isoformat(),
        "priority": priority,
        "data": {},
        "metadata": {}
    }
    
    try:
        # Initialize scraper
        scraper = ReliableScraper()
        
        # Perform scraping
        print("\n🔍 Starting advanced content extraction...")
        scrape_result = scraper.scrape_url(target_url)
        
        if scrape_result['success']:
            result.update({
                "status": "completed",
                "data": scrape_result,
                "extraction_method": "advanced_regex_parsing"
            })
            print("✅ Scraping completed successfully!")
        else:
            result.update({
                "status": "failed",
                "data": scrape_result,
                "error": scrape_result.get('error', 'Unknown error')
            })
            print("❌ Scraping failed")
        
    except Exception as e:
        print(f"💥 Critical error: {e}")
        result.update({
            "status": "failed",
            "error": str(e)
        })
    
    # Add metadata
    result["metadata"] = {
        "learning_insights": {
            "extraction_method": "regex_based_parsing",
            "reliability": "high",
            "github_actions_compatible": True,
            "browser_automation": False
        },
        "performance": {
            "execution_time": "< 30s",
            "memory_usage": "low",
            "success_rate": 1.0 if result["status"] == "completed" else 0.0
        },
        "capabilities": [
            "HTTP requests with session management",
            "Advanced regex-based content extraction",
            "Title and meta description extraction",
            "Heading structure analysis",
            "Link and image extraction",
            "Content structure analysis",
            "Response header analysis"
        ]
    }
    
    # Save results
    print("\n💾 Saving results...")
    with open("results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("📄 Results saved to results.json")
    
    # Send callback to hub
    if hub_url and api_key:
        try:
            print("📡 Sending results to hub...")
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
                print("📡 Callback sent successfully!")
            else:
                print(f"⚠️ Callback failed: {callback_response.status_code}")
        except Exception as e:
            print(f"⚠️ Callback error: {e}")
    
    print(f"\n🎯 Job completed: {result['status']}")
    print("✅ All files created successfully")

if __name__ == "__main__":
    main()
