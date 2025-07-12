"""
Main orchestrator for the scraping process.
"""
import time
from typing import List, Optional
from pathlib import Path

from base_scraper import ScraperConfig, ScrapingResult
from scraper_factory import ScraperFactory


class ScrapingOrchestrator:
    """Main class that orchestrates the scraping of multiple URLs."""
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.results = []
    
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
                results.append(ScrapingResult(success=False, error=error_msg))
                continue
            
            # Perform scraping
            result = scraper.scrape()
            results.append(result)
            
            # Add delay between requests (except for last URL)
            if i < len(urls):
                print(f"⏳ Waiting {delay_between_requests} seconds before next request...")
                time.sleep(delay_between_requests)
        
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
        
        print(f"{'='*60}")


# CLI interface
def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Web scraper for product data")
    parser.add_argument("--input", "-i", required=True, help="Input file containing URLs")
    parser.add_argument("--output", "-o", help="Output directory path")
    parser.add_argument("--delay", "-d", type=int, default=5, help="Delay between requests (seconds)")
    parser.add_argument("--max-images", type=int, default=20, help="Maximum images to download per product")
    
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
