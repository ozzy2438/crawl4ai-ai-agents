import asyncio
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup
import re

class Crawler:
    def __init__(self, max_pages: int = 200):
        self.max_pages = max_pages
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True,
            user_data_dir=None
        )
        
    def extract_content(self, html_content: str) -> Dict:
        """Extract content and links from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract all text content
        text_content = []
        for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'article']):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out short snippets
                text_content.append(text)
        
        # Extract all links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if href and text and not href.startswith(('#', 'javascript:')):
                if not href.startswith('http'):
                    href = f"https://www.abc.net.au{href}"
                links.append({
                    'url': href,
                    'text': text
                })
        
        # Extract title and description
        title = soup.find('title')
        title = title.get_text() if title else ''
        
        meta_desc = soup.find('meta', {'name': 'description'})
        description = meta_desc['content'] if meta_desc else ''
        
        return {
            'content': '\n\n'.join(text_content),
            'links': links,
            'title': title,
            'description': description
        }
    
    def crawl(self, url: str) -> list:
        """Crawl the given URL and return the crawled data."""
        return asyncio.run(self._crawl(url))
    
    async def _crawl(self, url: str) -> list:
        """Asynchronously crawl the given URL and return the crawled data."""
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            js_code="""
            // Wait for initial load
            await new Promise(r => setTimeout(r, 2000));
            
            // Scroll to load lazy content
            let lastHeight = await document.body.scrollHeight;
            let scrollCount = 0;
            while (scrollCount < 10) {  // Scroll more times to load more content
                window.scrollBy(0, 800);
                await new Promise(r => setTimeout(r, 500));
                
                let newHeight = await document.body.scrollHeight;
                if (newHeight === lastHeight) {
                    break;
                }
                lastHeight = newHeight;
                scrollCount++;
            }
            
            // Click "See More" buttons if they exist
            const seeMoreButtons = document.querySelectorAll('button, a');
            for (const button of seeMoreButtons) {
                if (button.textContent.toLowerCase().includes('see more')) {
                    button.click();
                    await new Promise(r => setTimeout(r, 1000));
                }
            }
            """
        )
        
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=run_config,
                magic=True
            )
            
            if result and (result.html or result.content):
                # Extract content from HTML
                extracted = self.extract_content(result.html or result.content)
                
                return [{
                    'url': url,
                    'content': extracted['content'],
                    'title': extracted['title'],
                    'description': extracted['description'],
                    'links': extracted['links']
                }]
            return []

if __name__ == "__main__":
    # Example usage
    crawler = Crawler()
    start_url = "https://example.com"  # Replace with your target URL
    results = crawler.crawl(start_url)
    print(f"Crawled {len(results)} pages successfully") 