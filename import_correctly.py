import pandas as pd
import mysql.connector

# Read CSV
df = pd.read_csv("destinations_dataset.csv")
print(f"Read {len(df)} rows from CSV")

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='tourism_app'
)
cursor = conn.cursor()

# Insert each row
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO destinations (
            country, country_code, city, place_name, description,
            latitude, longitude, budget_per_day_usd, best_season,
            top_attractions, local_foods, activities, safety_rating, avg_user_rating
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['country'], row.get('country_code', ''), row['city'], row['place_name'],
        row.get('description', ''), row.get('latitude', 0), row.get('longitude', 0),
        row.get('budget_per_day_usd', 100), row.get('best_season', 'Year-round'),
        row.get('top_attractions', ''), row.get('local_foods', ''),
        row.get('activities', ''), row.get('safety_rating', 4.0), row.get('avg_user_rating', 0)
    ))

conn.commit()
cursor.execute("SELECT COUNT(*) FROM destinations")
count = cursor.fetchone()[0]
print(f"✅ Imported {count} destinations successfully!")

cursor.close()
conn.close()