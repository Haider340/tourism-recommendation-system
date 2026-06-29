"""
retrain_models.py - Train ML models on 10,000 rows dataset
"""

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder

print("="*60)
print("RETRAINING MODELS ON 10,000 ROWS DATASET")
print("="*60)

# Create models directory
os.makedirs('models', exist_ok=True)

# Load data
print("\n[1/5] Loading 10,000 row dataset...")
destinations = pd.read_csv('data/raw/destinations.csv')
users = pd.read_csv('data/raw/users.csv')
ratings = pd.read_csv('data/raw/ratings.csv')

print(f"   Destinations: {len(destinations)}")
print(f"   Users: {len(users)}")
print(f"   Ratings: {len(ratings)}")
print(f"   Total rows: {len(destinations) + len(users) + len(ratings)}")

# Preprocess
print("\n[2/5] Preprocessing data...")
destinations['combined_text'] = destinations['place_name'] + ' ' + \
                                destinations['category'] + ' ' + \
                                destinations['tags'].fillna('') + ' ' + \
                                destinations['description'].fillna('')

le = LabelEncoder()
destinations['category_encoded'] = le.fit_transform(destinations['category'])

# Content-Based Model
print("\n[3/5] Training content-based model...")
tfidf = TfidfVectorizer(max_features=500, stop_words='english')
destination_features = tfidf.fit_transform(destinations['combined_text'])
similarity_matrix = cosine_similarity(destination_features)
print(f"   Similarity matrix shape: {similarity_matrix.shape}")

# Collaborative Filtering
print("\n[4/5] Training collaborative filtering model...")
user_item_matrix = ratings.pivot(
    index='user_id', 
    columns='destination_id', 
    values='rating'
).fillna(0)

user_similarity = cosine_similarity(user_item_matrix)
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_item_matrix.index,
    columns=user_item_matrix.index
)
print(f"   User-Item matrix shape: {user_item_matrix.shape}")

# Save models
print("\n[5/5] Saving models...")
joblib.dump(tfidf, 'models/tfidf_vectorizer.pkl')
joblib.dump(destination_features, 'models/destination_features.pkl')
joblib.dump(similarity_matrix, 'models/similarity_matrix.pkl')
joblib.dump(user_item_matrix, 'models/user_item_matrix.pkl')
joblib.dump(user_similarity_df, 'models/user_similarity_df.pkl')
joblib.dump(destinations, 'models/destinations.pkl')
joblib.dump(users, 'models/users.pkl')
joblib.dump(ratings, 'models/ratings.pkl')

print("   ✓ Models saved to models/")

# Verify
print("\nVerifying saved models...")
test_users = joblib.load('models/users.pkl')
test_dest = joblib.load('models/destinations.pkl')
print(f"   Users: {len(test_users)}")
print(f"   Destinations: {len(test_dest)}")

print("\n" + "="*60)
print("✅ MODEL RETRAINING COMPLETE!")
print("="*60)
print("\nNow run: streamlit run app.py")