from playwright.sync_api import sync_playwright
from pathlib import Path
import hashlib

def download_with_browser(url: str, source: str, date_str: str = None):
    """Download file using browser automation"""
    # Create raw directory if it doesn't exist
    raw_dir = Path(f"raw/{source}")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set user agent
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        print(f"Navigating to {url}")
        
        # Handle the download
        with page.expect_download() as download_info:
            page.goto(url)
        
        download = download_info.value
        
        # Generate checksum
        with open(download.path(), "rb") as f:
            content = f.read()
        checksum = hashlib.sha256(content).hexdigest()
        
        # Determine filename
        if date_str:
            filename = f"{date_str}_{source}_{checksum[:8]}.csv"
        else:
            filename = f"{source}_{checksum[:8]}.csv"
            
        filepath = raw_dir / filename
        
        # Save file
        download.save_as(filepath)
        
        print(f"Successfully downloaded to: {filepath}")
        print(f"File size: {len(content):,} bytes")
        
        browser.close()
        return filepath, checksum

if __name__ == "__main__":
    url = "https://www2.aer.ca/t/Production/views/COM-WellLicenceAllList/WellLicenceAllAB.csv"
    filepath, checksum = download_with_browser(url, "st37")
    print(f"Downloaded to: {filepath}")
    print(f"Checksum: {checksum}")
