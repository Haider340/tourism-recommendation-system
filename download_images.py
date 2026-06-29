"""
Country Image Downloader - 1 Image Per Country (195 Countries)
Downloads one representative image for each country in your dataset
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
from urllib.parse import quote
import json

print("="*60)
print("🌍 COUNTRY IMAGE DOWNLOADER")
print("1 Image Per Country - 195 Countries")
print("="*60)

# Create directories
os.makedirs('images/countries', exist_ok=True)
os.makedirs('images/categories', exist_ok=True)

# Load destinations
df = pd.read_csv('data/raw/destinations.csv')
countries = sorted(df['country'].unique())
print(f"\n📊 Found {len(countries)} unique countries")

# ============================================
# DOWNLOAD ONE IMAGE PER COUNTRY
# ============================================

print("\n📸 Starting download...")
print("-" * 40)

downloaded = 0
failed = 0
failed_countries = []

for idx, country in enumerate(countries):
    # Create safe filename
    safe_name = country.replace(' ', '_').replace('/', '_')
    filename = f"images/countries/{safe_name}.jpg"
    
    # Skip if already exists
    if os.path.exists(filename) and os.path.getsize(filename) > 1000:
        downloaded += 1
        print(f"✅ [{idx+1}/{len(countries)}] {country} - Already exists")
        continue
    
    # Try different search queries to get the best image
    search_queries = [
        f"{country} landmark tourism",
        f"{country} famous place",
        f"{country} beautiful view",
        f"{country} travel destination"
    ]
    
    success = False
    for query in search_queries:
        try:
            # Try Unsplash direct URL
            encoded_query = quote(query)
            url = f"https://source.unsplash.com/featured/800x500?{encoded_query}"
            
            response = requests.get(url, timeout=15)
            
            # Check if we got a valid image
            if response.status_code == 200 and len(response.content) > 5000:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                success = True
                downloaded += 1
                print(f"✅ [{idx+1}/{len(countries)}] {country} - Downloaded")
                break
        except Exception as e:
            continue
        
        # Small delay between attempts
        time.sleep(0.5)
    
    if not success:
        failed += 1
        failed_countries.append(country)
        print(f"❌ [{idx+1}/{len(countries)}] {country} - Failed (using placeholder)")
        # Create a placeholder with country name
        try:
            # Use picsum as fallback
            fallback_url = f"https://picsum.photos/seed/{country}/800/500"
            response = requests.get(fallback_url, timeout=10)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                downloaded += 1
                print(f"   ✅ {country} - Using fallback image")
        except:
            pass
    
    # Rate limiting - be gentle
    time.sleep(0.5)
    
    # Show progress every 20 countries
    if (idx + 1) % 20 == 0:
        print(f"\n📊 Progress: {idx+1}/{len(countries)} | Downloaded: {downloaded} | Failed: {failed}\n")

# ============================================
# DOWNLOAD CATEGORY IMAGES (Fallback)
# ============================================

print("\n📸 Downloading category fallback images...")
print("-" * 40)

categories = ['Landmark', 'Museum', 'Nature', 'Activity', 'Cultural', 'Food', 'Shopping']

for category in categories:
    filename = f"images/categories/{category}.jpg"
    
    if os.path.exists(filename):
        print(f"✅ {category} - Already exists")
        continue
    
    try:
        url = f"https://source.unsplash.com/featured/800x500?{category},travel"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ {category} - Downloaded")
    except:
        print(f"❌ {category} - Failed")
    
    time.sleep(0.5)

# ============================================
# UPDATE CSV WITH IMAGE PATHS
# ============================================

print("\n📝 Updating CSV with image paths...")

# Map country to image path
def get_image_path(row):
    safe_name = row['country'].replace(' ', '_').replace('/', '_')
    country_path = f"images/countries/{safe_name}.jpg"
    
    if os.path.exists(country_path):
        return country_path
    
    # Fallback to category image
    category_path = f"images/categories/{row['category']}.jpg"
    if os.path.exists(category_path):
        return category_path
    
    return ""

df['image_paths'] = df.apply(get_image_path, axis=1)
df.to_csv('data/raw/destinations.csv', index=False)

print("✅ CSV updated with image paths")

# ============================================
# SUMMARY
# ============================================

print("\n" + "="*60)
print("📊 DOWNLOAD SUMMARY")
print("="*60)

print(f"\n✅ Country images downloaded: {downloaded}/{len(countries)}")
print(f"❌ Failed downloads: {failed}")

if failed_countries:
    print(f"\n⚠️ Failed countries ({len(failed_countries)}):")
    for i, country in enumerate(failed_countries[:10]):
        print(f"   {i+1}. {country}")
    if len(failed_countries) > 10:
        print(f"   ... and {len(failed_countries) - 10} more")

# Count images
country_images = len([f for f in os.listdir('images/categories') if f.endswith('.jpg')])
category_images = len([f for f in os.listdir('images/categories') if f.endswith('.jpg')])

print(f"\n📁 images/countries/ - {country_images} images")
print(f"📁 images/categories/ - {category_images} fallback images")

print("\n" + "="*60)
print("✅ Image download complete!")
print("="*60)