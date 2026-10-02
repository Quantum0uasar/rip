import httpx
from pathlib import Path
import hashlib
import time

def download_file(url: str, source: str, date_str: str = None, max_retries: int = 3):
    """Download file with browser headers and retry logic"""
    # Create raw directory if it doesn't exist
    raw_dir = Path(f"raw/{source}")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Browser-like headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.aer.ca/"
    }
    
    # Retry logic
    for attempt in range(max_retries):
        try:
            # Increase timeout to 60 seconds
            with httpx.Client(headers=headers, timeout=60.0) as client:
                print(f"Attempt {attempt + 1}/{max_retries}: Downloading from {url}")
                response = client.get(url)
                response.raise_for_status()
                
                # Generate checksum
                checksum = hashlib.sha256(response.content).hexdigest()
                
                # Determine filename
                if date_str:
                    filename = f"{date_str}_{source}_{checksum[:8]}.csv"
                else:
                    filename = f"{source}_{checksum[:8]}.csv"
                    
                filepath = raw_dir / filename
                
                # Save file
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                print(f"Successfully downloaded to: {filepath}")
                print(f"File size: {len(response.content):,} bytes")
                return filepath, checksum
                
        except httpx.ReadTimeout:
            print(f"Timeout on attempt {attempt + 1}, retrying...")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
