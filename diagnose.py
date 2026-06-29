"""
Diagnose why destinations aren't showing
Run this: python diagnose.py
"""

import os
import sys
import pandas as pd
from db_config import get_db_connection

print("=" * 60)
print("🔍 TOURISM APP DIAGNOSTIC TOOL")
print("=" * 60)

# 1. Check if CSV exists
print("\n1. Checking CSV file...")
csv_path = "destinations_dataset.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f"   ✅ CSV found: {csv_path}")
    print(f"   📊 Rows: {len(df)}")
    print(f"   📋 Columns: {list(df.columns)[:5]}...")
else:
    print(f"   ❌ CSV NOT found: {csv_path}")
    print(f"   Current directory: {os.getcwd()}")
    print(f"   Files in directory: {os.listdir()}")

# 2. Check database connection
print("\n2. Checking Database...")
conn = get_db_connection()
if conn:
    print("   ✅ Database connected!")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM destinations")
    count = cursor.fetchone()[0]
    print(f"   📊 Destinations in DB: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, country, city, place_name FROM destinations LIMIT 5")
        sample = cursor.fetchall()
        print(f"   📋 Sample destinations:")
        for row in sample:
            print(f"      - {row[1]}, {row[2]}: {row[3]}")
    else:
        print("   ⚠️ No destinations found in database!")
        print("   You need to import the CSV data into MySQL")
    
    cursor.close()
    conn.close()
else:
    print("   ❌ Database connection FAILED!")
    print("   Check: Is MySQL running in XAMPP?")

# 3. Check images folder
print("\n3. Checking Images folder...")
images_path = "./images"
if os.path.exists(images_path):
    folders = [f for f in os.listdir(images_path) if os.path.isdir(os.path.join(images_path, f))]
    print(f"   ✅ Images folder exists")
    print(f"   📁 Countries with images: {len(folders)}")
else:
    print(f"   ⚠️ Images folder not found: {images_path}")

print("\n" + "=" * 60)
print("💡 RECOMMENDATIONS:")
print("=" * 60)

conn = get_db_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM destinations")
    db_count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    if db_count == 0:
        print("\n❌ Your database is EMPTY!")
        print("\nYou need to import destinations into MySQL:")
        print("1. Open phpMyAdmin (http://localhost/phpmyadmin)")
        print("2. Select 'tourism_app' database")
        print("3. Click 'Import' tab")
        print("4. Select your 'destinations_dataset.csv' file")
        print("5. Click 'Go'")
else:
    print("\n❌ Fix database connection first!")
    print("1. Open XAMPP Control Panel")
    print("2. Click 'Start' next to MySQL")
    print("3. Make sure it shows green highlight")