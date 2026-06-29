# update_image_paths.py
import mysql.connector
import os
from pathlib import Path

print("=" * 60)
print("🖼️ UPDATING DATABASE WITH IMAGE PATHS")
print("=" * 60)

# Connect to database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='tourism_app'
)
cursor = conn.cursor()

# Get all destinations
cursor.execute("SELECT id, country, city, place_name FROM destinations")
destinations = cursor.fetchall()
print(f"📊 Found {len(destinations)} destinations in database")

# Track progress
updated = 0
not_found = 0

for dest_id, country, city, place_name in destinations:
    # Clean folder names (remove special characters)
    safe_country = "".join(c for c in country if c.isalnum() or c in " ").strip()
    safe_city = "".join(c for c in city if c.isalnum() or c in " ").strip()
    
    # If city name is generic, use place_name for folder
    if safe_city in ["North", "South", "East", "West", "Region", "Area"]:
        safe_city = "".join(c for c in place_name.split()[0] if c.isalnum() or c in " ").strip()
    
    # Build path
    image_dir = Path(f"./images/{safe_country}/{safe_city}")
    
    if image_dir.exists():
        images = list(image_dir.glob("*.jpg"))
        if images:
            # Store relative paths (convert Windows backslashes to forward slashes)
            image_paths = ",".join([str(img).replace("\\", "/") for img in images[:3]])
            cursor.execute(
                "UPDATE destinations SET image_paths = %s WHERE id = %s",
                (image_paths, dest_id)
            )
            updated += 1
            print(f"✅ [{updated}] {country}/{city}: {place_name} ({len(images)} images)")
        else:
            print(f"⚠️ No JPG files in: {image_dir}")
            not_found += 1
    else:
        # Try alternative folder structure (place_name instead of city)
        alt_city = "".join(c for c in place_name.split()[0] if c.isalnum())
        alt_dir = Path(f"./images/{safe_country}/{alt_city}")
        
        if alt_dir.exists():
            images = list(alt_dir.glob("*.jpg"))
            if images:
                image_paths = ",".join([str(img).replace("\\", "/") for img in images[:3]])
                cursor.execute(
                    "UPDATE destinations SET image_paths = %s WHERE id = %s",
                    (image_paths, dest_id)
                )
                updated += 1
                print(f"✅ [{updated}] {country}/{alt_city}: {place_name} (found in alt folder)")
            else:
                print(f"❌ No images for: {country}/{city} - {place_name}")
                not_found += 1
        else:
            print(f"❌ No images for: {country}/{city} - {place_name}")
            not_found += 1

# Commit changes
conn.commit()
print("\n" + "=" * 60)
print("📊 RESULTS")
print("=" * 60)
print(f"✅ Destinations updated with images: {updated}")
print(f"❌ Destinations without images: {not_found}")
print(f"📊 Total processed: {updated + not_found}")

# Verify update
cursor.execute("SELECT COUNT(*) FROM destinations WHERE image_paths IS NOT NULL AND image_paths != ''")
count_with_images = cursor.fetchone()[0]
print(f"\n🖼️ Destinations now have image paths: {count_with_images}")

cursor.close()
conn.close()

# Show sample of what was updated
print("\n📋 Sample of updated destinations:")
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='tourism_app'
)
cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT country, city, place_name, image_paths FROM destinations WHERE image_paths IS NOT NULL AND image_paths != '' LIMIT 10")
samples = cursor.fetchall()
for sample in samples:
    paths = sample['image_paths'].split(',')
    print(f"   🖼️ {sample['country']}/{sample['city']}: {sample['place_name']} - {len(paths)} images")
cursor.close()
conn.close()