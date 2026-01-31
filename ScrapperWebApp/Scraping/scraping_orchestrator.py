"""
Main orchestrator for the scraping process.

CLI USAGE:
    python scraping_orchestrator.py --input urls.txt [OPTIONS]

QUICK START:
    1. Create a text file with URLs (one per line):
       https://www.amazon.com/your-product-url
       https://www.wayfair.com/another-product-url
    
    2. Run the scraper:
       python scraping_orchestrator.py -i your_urls.txt
    
    3. Check the output directory for scraped data and images

OPTIONS:
    -i, --input     Text file with URLs (REQUIRED)
    -o, --output    Custom output directory
    -d, --delay     Seconds between requests (default: 5)
    --max-images    Max images per product (default: 20)

EXAMPLES:
    python scraping_orchestrator.py -i links.txt
    python scraping_orchestrator.py -i links.txt -o "C:/Output" -d 3
    python scraping_orchestrator.py -i links.txt --max-images 10
"""
import time
import sys
import io
from typing import List, Optional
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from .base_scraper import ScraperConfig, ScrapingResult
from .scraper_factory import ScraperFactory


class ScrapingOrchestrator:
    """Main class that orchestrates the scraping of multiple URLs."""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.results = []
        self.unsupported_urls = []
    
    def _progress_countdown(self, duration: int, message: str = "Waiting"):
        """Display a countdown timer for delays."""
        print(f"⏳ {message} ({duration}s)", end="", flush=True)
        
        for remaining in range(duration, 0, -1):
            print(f"\r⏳ {message} ({remaining}s)" + "." * (duration - remaining + 1), end="", flush=True)
            time.sleep(1)
        
        print(f"\r✅ {message} completed!" + " " * 20)  # Clear the line
        print()  # New line for next output
    
    def scrape_urls(self, urls: List[str], delay_between_requests: int = 5) -> List[ScrapingResult]:
        """Scrape multiple URLs with delay between requests."""
        results = []
        
        print(f"🚀 Starting scraping process for {len(urls)} URLs")
        print(f"📁 Output directory: {self.config.output_path}")
        
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*60}")
            print(f"🔄 Processing URL {i}/{len(urls)}: {url}")
            print(f"{'='*60}")
            
            # Create appropriate scraper
            scraper = ScraperFactory.create_scraper(url, self.config)
            
            if not scraper:
                error_msg = f"No scraper available for URL: {url}"
                print(f"❌ {error_msg}")
                self.unsupported_urls.append(url)  # Track unsupported URL
                results.append(ScrapingResult(success=False, error=error_msg))
                continue
            
            # Perform scraping
            result = scraper.scrape()
            results.append(result)
            
            # Add delay between requests (except for last URL)
            if i < len(urls):
                self._progress_countdown(delay_between_requests, f"Cooling down before next request ({i+1}/{len(urls)})")
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def scrape_from_file(self, file_path: str, delay_between_requests: int = 5) -> List[ScrapingResult]:
        """Scrape URLs from a text file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as file:
                urls = [line.strip() for line in file if line.strip()]
            
            if not urls:
                print("⚠️ No URLs found in file")
                return []
            
            return self.scrape_urls(urls, delay_between_requests)
            
        except Exception as e:
            error_msg = f"Failed to read URLs from file: {e}"
            print(f"❌ {error_msg}")
            return [ScrapingResult(success=False, error=error_msg)]
    
    def _print_summary(self, results: List[ScrapingResult]) -> None:
        """Print scraping summary."""
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        print(f"\n{'='*60}")
        print(f"📊 SCRAPING SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(results)}")
        
        if failed > 0:
            print(f"\n❌ Failed URLs:")
            for result in results:
                if not result.success:
                    print(f"   • Error: {result.error}")
        
        # Print unsupported URLs at the end
        if self.unsupported_urls:
            print(f"\n🚫 UNSUPPORTED URLs ({len(self.unsupported_urls)}):")
            for url in self.unsupported_urls:
                print(f"   • {url}")
            
            # Show supported domains
            from scraper_factory import ScraperFactory
            supported_domains = ScraperFactory.get_supported_domains()
            print(f"\nℹ️  Supported domains: {', '.join(supported_domains)}")
        
        print(f"{'='*60}")


# CLI interface
def main():
    """
    Main entry point for CLI usage.
    
    USAGE EXAMPLES:
    
    Basic usage with URL file:
        python scraping_orchestrator.py --input urls.txt
        python scraping_orchestrator.py -i urls.txt
    
    With custom output directory:
        python scraping_orchestrator.py -i urls.txt -o "C:/MyOutput"
        python scraping_orchestrator.py -i urls.txt --output "D:/ScrapedData"
    
    With custom delay between requests:
        python scraping_orchestrator.py -i urls.txt -d 3
        python scraping_orchestrator.py -i urls.txt --delay 10
    
    With custom maximum images per product:
        python scraping_orchestrator.py -i urls.txt --max-images 15
    
    Full example with all options:
        python scraping_orchestrator.py -i "C:/urls.txt" -o "D:/Output" -d 7 --max-images 25
    
    SUPPORTED DOMAINS:
        - Amazon: amazon.com, amazon.ca, amazon.co.uk
        - Wayfair: wayfair.com, wayfair.ca
    
    INPUT FILE FORMAT:
        Create a text file with one URL per line:
        https://www.amazon.com/product1
        https://www.amazon.ca/product2
        https://www.wayfair.com/product3
        
    NOTES:
        - Unsupported URLs will be listed at the end of scraping
        - Each product gets its own folder with images and data
        - Default delay is 5 seconds between requests (be respectful!)
        - Default output: "G:/My Drive/selling/not posted/"
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Web scraper for product data from Amazon and Wayfair",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  %(prog)s -i urls.txt
  %(prog)s -i urls.txt -o "C:/MyOutput" -d 3 --max-images 15
  %(prog)s --input "C:/my_urls.txt" --output "D:/ScrapedData" --delay 10

SUPPORTED SITES:
  Amazon (amazon.com, amazon.ca, amazon.co.uk)
  Wayfair (wayfair.com, wayfair.ca)
        """
    )
    
    parser.add_argument(
        "--input", "-i", 
        required=True, 
        help="Path to text file containing URLs (one per line)"
    )
    parser.add_argument(
        "--output", "-o", 
        help="Output directory path (default: G:/My Drive/selling/not posted/)"
    )
    parser.add_argument(
        "--delay", "-d", 
        type=int, 
        default=5, 
        help="Delay between requests in seconds (default: 5, min recommended: 2)"
    )
    parser.add_argument(
        "--max-images", 
        type=int, 
        default=20, 
        help="Maximum images to download per product (default: 20)"
    )
    
    args = parser.parse_args()
    
    # Create config
    config = ScraperConfig(
        output_path=args.output or "G:\\My Drive\\selling\\not posted\\",
        max_images=args.max_images
    )
    
    # Create orchestrator and run
    orchestrator = ScrapingOrchestrator(config)
    results = orchestrator.scrape_from_file(args.input, args.delay)
    
    # Exit with appropriate code
    successful = sum(1 for r in results if r.success)
    if successful == len(results):
        print("🎉 All scraping operations completed successfully!")
        exit(0)
    else:
        print("⚠️ Some scraping operations failed.")
        exit(1)


if __name__ == "__main__":
    main()
