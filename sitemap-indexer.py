import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time
import argparse
from typing import List, Set
from urllib.parse import urljoin

# ============================================================================
# CONFIGURATION: Update these values with your credentials
# ============================================================================

SERVICE_ACCOUNT_FILE = 'service-account.json'  # Path to your service account JSON file
BATCH_SIZE = 200  # Maximum URLs to index per run (Google default quota: 200/day)
DELAY_SECONDS = 1.0  # Delay between API requests to avoid rate limiting

# ============================================================================


class SitemapIndexer:
    def __init__(self, service_account_file: str):
        """
        Initialize the Sitemap Indexer with Google Service Account credentials.
        
        Args:
            service_account_file: Path to the service account JSON file
        """
        self.service_account_file = service_account_file
        self.indexed_urls = set()
        self.failed_urls = []
        
    def get_indexing_service(self):
        """Create and return Google Indexing API service."""
        credentials = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/indexing']
        )
        return build('indexing', 'v3', credentials=credentials)
    
    def fetch_sitemap(self, sitemap_url: str) -> str:
        """
        Fetch sitemap content from URL.
        
        Args:
            sitemap_url: URL of the sitemap
            
        Returns:
            XML content as string
        """
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching sitemap {sitemap_url}: {e}")
            return None
    
    def extract_urls_from_sitemap(self, xml_content: str, base_url: str = None) -> tuple[List[str], List[str]]:
        """
        Extract URLs and nested sitemap URLs from sitemap XML.
        
        Args:
            xml_content: XML content of the sitemap
            base_url: Base URL for resolving relative URLs
            
        Returns:
            Tuple of (page_urls, sitemap_urls)
        """
        page_urls = []
        sitemap_urls = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespaces
            namespaces = {
                'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                'xhtml': 'http://www.w3.org/1999/xhtml'
            }
            
            # Check if it's a sitemap index
            sitemap_elements = root.findall('.//sm:sitemap/sm:loc', namespaces)
            if sitemap_elements:
                # This is a sitemap index containing other sitemaps
                for elem in sitemap_elements:
                    url = elem.text.strip()
                    if base_url:
                        url = urljoin(base_url, url)
                    sitemap_urls.append(url)
                print(f"Found {len(sitemap_urls)} nested sitemaps")
            
            # Extract regular URLs
            url_elements = root.findall('.//sm:url/sm:loc', namespaces)
            for elem in url_elements:
                url = elem.text.strip()
                if base_url:
                    url = urljoin(base_url, url)
                page_urls.append(url)
            
            if page_urls:
                print(f"Found {len(page_urls)} URLs")
                
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
        
        return page_urls, sitemap_urls
    
    def crawl_sitemaps(self, sitemap_url: str, visited_sitemaps: Set[str] = None) -> List[str]:
        """
        Recursively crawl sitemaps and extract all URLs.
        
        Args:
            sitemap_url: Starting sitemap URL
            visited_sitemaps: Set of already visited sitemap URLs
            
        Returns:
            List of all extracted URLs
        """
        if visited_sitemaps is None:
            visited_sitemaps = set()
        
        if sitemap_url in visited_sitemaps:
            return []
        
        visited_sitemaps.add(sitemap_url)
        all_urls = []
        
        print(f"\nProcessing sitemap: {sitemap_url}")
        xml_content = self.fetch_sitemap(sitemap_url)
        
        if not xml_content:
            return []
        
        page_urls, nested_sitemaps = self.extract_urls_from_sitemap(xml_content, sitemap_url)
        all_urls.extend(page_urls)
        
        # Recursively process nested sitemaps
        for nested_sitemap in nested_sitemaps:
            nested_urls = self.crawl_sitemaps(nested_sitemap, visited_sitemaps)
            all_urls.extend(nested_urls)
        
        return all_urls
    
    def index_url(self, service, url: str) -> bool:
        """
        Submit a single URL to Google Indexing API.
        
        Args:
            service: Google Indexing API service
            url: URL to index
            
        Returns:
            True if successful, False otherwise
        """
        try:
            body = {
                'url': url,
                'type': 'URL_UPDATED'
            }
            response = service.urlNotifications().publish(body=body).execute()
            print(f"✓ Indexed: {url}")
            return True
        except HttpError as e:
            print(f"✗ Failed to index {url}: {e}")
            self.failed_urls.append(url)
            return False
        except Exception as e:
            print(f"✗ Error indexing {url}: {e}")
            self.failed_urls.append(url)
            return False
    
    def index_urls(self, urls: List[str], batch_size: int = 200, delay: float = 1.0):
        """
        Index multiple URLs using Google Indexing API with rate limiting.
        
        Args:
            urls: List of URLs to index
            batch_size: Maximum number of URLs to process
            delay: Delay between requests in seconds
        """
        service = self.get_indexing_service()
        
        print(f"\n{'='*60}")
        print(f"Starting indexing process for {len(urls)} URLs")
        print(f"{'='*60}\n")
        
        urls_to_process = urls[:batch_size] if batch_size else urls
        success_count = 0
        
        for i, url in enumerate(urls_to_process, 1):
            print(f"[{i}/{len(urls_to_process)}] ", end="")
            
            if self.index_url(service, url):
                success_count += 1
                self.indexed_urls.add(url)
            
            # Rate limiting
            if i < len(urls_to_process):
                time.sleep(delay)
        
        print(f"\n{'='*60}")
        print(f"Indexing Summary:")
        print(f"Total URLs: {len(urls_to_process)}")
        print(f"Successfully indexed: {success_count}")
        print(f"Failed: {len(self.failed_urls)}")
        print(f"{'='*60}\n")
        
        if self.failed_urls:
            print("Failed URLs:")
            for url in self.failed_urls:
                print(f"  - {url}")
    
    def process_sitemap(self, sitemap_url: str, batch_size: int = 200, delay: float = 1.0):
        """
        Main method to process sitemap and index all URLs.
        
        Args:
            sitemap_url: Main sitemap URL
            batch_size: Maximum URLs to index in one run
            delay: Delay between indexing requests
        """
        print(f"Starting sitemap processing...")
        print(f"Main sitemap: {sitemap_url}\n")
        
        # Extract all URLs from sitemaps
        all_urls = self.crawl_sitemaps(sitemap_url)
        
        # Remove duplicates
        unique_urls = list(set(all_urls))
        
        print(f"\n{'='*60}")
        print(f"Total unique URLs found: {len(unique_urls)}")
        print(f"{'='*60}\n")
        
        if not unique_urls:
            print("No URLs found to index.")
            return
        
        # Index the URLs
        self.index_urls(unique_urls, batch_size, delay)


def main():
    """
    Main function to run the sitemap indexer with command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Extract URLs from sitemaps and submit to Google Indexing API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sitemap_indexer.py -u https://example.com/sitemap.xml
  python sitemap_indexer.py -u https://example.com/sitemap.xml --batch 100
  python sitemap_indexer.py -u https://example.com/sitemap.xml --delay 2.0

Before running:
  1. Update SERVICE_ACCOUNT_FILE path in the script
  2. Make sure service account email is added to Google Search Console as Owner
        """
    )
    
    parser.add_argument(
        '-u', '--url',
        required=True,
        help='Sitemap URL to process (e.g., https://example.com/sitemap.xml)'
    )
    
    parser.add_argument(
        '--batch',
        type=int,
        default=BATCH_SIZE,
        help=f'Maximum URLs to index per run (default: {BATCH_SIZE})'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=DELAY_SECONDS,
        help=f'Delay between requests in seconds (default: {DELAY_SECONDS})'
    )
    
    args = parser.parse_args()
    
    print()
    print("="*60)
    print("Google Sitemap Indexer")
    print("="*60)
    print(f"Service Account: {SERVICE_ACCOUNT_FILE}")
    print(f"Sitemap URL: {args.url}")
    print(f"Batch Size: {args.batch}")
    print(f"Delay: {args.delay}s")
    print("="*60)
    print()
    
    try:
        # Create indexer instance
        indexer = SitemapIndexer(SERVICE_ACCOUNT_FILE)
        
        # Process sitemap and index URLs
        indexer.process_sitemap(
            sitemap_url=args.url,
            batch_size=args.batch,
            delay=args.delay
        )
    except FileNotFoundError:
        print(f"\nError: Service account file '{SERVICE_ACCOUNT_FILE}' not found!")
        print("Please update SERVICE_ACCOUNT_FILE path in the script.")
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Check if service account email is added to Search Console as Owner")
        print("2. Verify the Web Search Indexing API is enabled in Google Cloud")
        print("3. Make sure the service account JSON file is valid")


if __name__ == '__main__':
    main()
