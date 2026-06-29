"""
Improved Image Downloader with Better Rate Limiting
Handles 403 errors and resumes automatically
"""

import os
import requests
import pandas as pd
from pathlib import Path
import time
import sys
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

class UnsplashDownloader:
    def __init__(self, access_key: str):
        self.access_key = access_key
        self.base_url = "https://api.unsplash.com/search/photos"
        self.headers = {"Authorization": f"Client-ID {access_key}"}
        self.request_count = 0
        self.hour_start = time.time()
    
    def wait_if_needed(self):
        """Check rate limits and wait if necessary"""
        current_time = time.time()
        elapsed = current_time - self.hour_start
        
        # Reset counter after 1 hour
        if elapsed >= 3600:
            self.request_count = 0
            self.hour_start = current_time
            print("\n🔄 Rate limit window reset. Continuing...\n")
            return
        
        # If approaching limit (45 requests), wait
        if self.request_count >= 45:
            wait_time = 3600 - elapsed
            print(f"\n⏰ Rate limit approaching. Waiting {wait_time/60:.1f} minutes...")
            time.sleep(wait_time)
            self.request_count = 0
            self.hour_start = time.time()
    
    def download_images(self, query: str, num_images: int = 3, save_dir: str = "./images") -> list:
        """Download images with proper rate limit handling"""
        
        self.request_count += 1
        self.wait_if_needed()
        
        params = {
            "query": query,
            "per_page": min(num_images, 30),
            "page": 1,
            "orientation": "landscape"
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            
            if response.status_code == 403:
                print(f"⚠️ Rate limit hit. Waiting 1 hour...")
                time.sleep(3600)  # Wait 1 hour
                self.request_count = 0
                self.hour_start = time.time()
                return self.download_images(query, num_images, save_dir)  # Retry
            
            if response.status_code == 401:
                print("❌ Invalid API key!")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            downloaded_paths = []
            os.makedirs(save_dir, exist_ok=True)
            
            for idx, photo in enumerate(data.get("results", [])[:num_images]):
                image_url = photo.get("urls", {}).get("regular")
                if image_url:
                    img_response = requests.get(image_url)
                    img_response.raise_for_status()
                    
                    safe_query = "".join(c for c in query if c.isalnum() or c in " ").replace(" ", "_")
                    if len(safe_query) > 80:
                        safe_query = safe_query[:80]
                    filename = f"{safe_query}_{idx+1}.jpg"
                    filepath = os.path.join(save_dir, filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(img_response.content)
                    
                    downloaded_paths.append(filepath)
                    print(f"✅ Downloaded: {filename}")
                    time.sleep(0.5)
            
            return downloaded_paths
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def check_remaining_requests(self):
        """Check how many requests left this hour"""
        elapsed = time.time() - self.hour_start
        remaining_time = 3600 - elapsed
        remaining_requests = 50 - self.request_count
        return remaining_requests, remaining_time

def download_all_destinations(csv_path: str, access_key: str, start_from: int = 0):
    """Download images with resume capability"""
    
    if not access_key:
        print("❌ No API key found!")
        return
    
    downloader = UnsplashDownloader(access_key)
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    total = len(df)
    
    print(f"\n📸 Starting from destination {start_from + 1} of {total}")
    print(f"⏱️  This will take several hours due to rate limits")
    print(f"💡 Press Ctrl+C to save progress and resume later\n")
    
    # Create progress file
    progress_file = "download_progress.txt"
    
    for idx in range(start_from, total):
        row = df.iloc[idx]
        
        # Skip if already has images
        if pd.notna(row.get('image_paths')) and row.get('image_paths'):
            print(f"[{idx+1}/{total}] ⏭️ Skipping {row['city']} {row['place_name']} (already has images)")
            continue
        
        search_query = f"{row['city']} {row['place_name']} travel"
        
        safe_country = "".join(c for c in str(row['country']) if c.isalnum() or c in " ").strip()
        safe_city = "".join(c for c in str(row['city']) if c.isalnum() or c in " ").strip()
        
        if not safe_country:
            safe_country = "Unknown"
        if not safe_city:
            safe_city = "Unknown"
            
        save_dir = f"./images/{safe_country}/{safe_city}"
        
        remaining_req, remaining_time = downloader.check_remaining_requests()
        print(f"\n[{idx+1}/{total}] 🔍 {search_query}")
        print(f"   📊 {remaining_req} requests left this hour ({remaining_time/60:.0f} min remaining)")
        
        downloaded = downloader.download_images(search_query, num_images=2, save_dir=save_dir)
        
        if downloaded:
            df.at[idx, 'image_paths'] = ",".join(downloaded)
            # Save progress after each successful download
            df.to_csv(csv_path.replace('.csv', '_with_images.csv'), index=False)
            with open(progress_file, 'w') as f:
                f.write(str(idx + 1))
        
        time.sleep(2)  # Delay between requests
    
    output_path = csv_path.replace('.csv', '_with_images.csv')
    df.to_csv(output_path, index=False)
    
    # Count downloaded images
    images_count = sum(1 for _ in Path("./images").rglob("*.jpg"))
    print(f"\n✅ Complete! Downloaded {images_count} images")
    print(f"📄 Saved to: {output_path}")

def get_progress():
    """Get last completed destination"""
    progress_file = "download_progress.txt"
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return int(f.read().strip())
    return 0

if __name__ == "__main__":
    print("=" * 60)
    print("🏞️  UNSPLASH IMAGE DOWNLOADER (with Resume Support)")
    print("=" * 60)
    
    api_key = UNSPLASH_ACCESS_KEY
    
    if not api_key:
        print("\n❌ No API key found in .env file!")
        print("Create a .env file with: UNSPLASH_ACCESS_KEY=your_key")
        sys.exit(1)
    
    csv_path = input("\n📁 CSV file path [destinations_dataset.csv]: ").strip()
    if not csv_path:
        csv_path = "destinations_dataset.csv"
    
    last_position = get_progress()
    if last_position > 0:
        print(f"\n📌 Resume from destination {last_position + 1}?")
        resume = input("   Resume from last position? (yes/no): ").strip().lower()
        if resume != 'yes':
            last_position = 0
    
    download_all_destinations(csv_path, api_key, start_from=last_position)