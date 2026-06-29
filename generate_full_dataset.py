"""
Synthetic Data Generator - 10,000 Destinations Version
Generates 10,000 unique destinations with images
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta
import json
import requests
from pathlib import Path
import time

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

print("="*60)
print("TOURISM RECOMMENDATION SYSTEM - 10,000 DESTINATIONS")
print("="*60)

# Create directories
print("\n[1/5] Creating directories...")
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('images/destinations', exist_ok=True)
print("  ✓ Directories created")

# ============================================
# CONFIGURATION - 10,000 DESTINATIONS
# ============================================
NUM_DESTINATIONS = 10000   # 10,000 unique destinations
NUM_USERS = 100            # 100 users
RATING_DENSITY = 0.15      # 15% of user-destination pairs have ratings
# Total ratings = 100 × 10,000 × 0.15 = 150,000 ratings

# ============================================
# Define categories and tags
# ============================================

categories = {
    'Landmark': ['Historical Monument', 'Architectural Wonder', 'Iconic Building', 'Castle', 'Palace', 'Fortress', 'Cathedral', 'Bridge', 'Statue', 'Square'],
    'Museum': ['Art Museum', 'History Museum', 'Science Museum', 'Cultural Museum', 'Modern Art', 'Natural History', 'War Museum', 'Children\'s Museum'],
    'Nature': ['Beach', 'Mountain', 'National Park', 'Garden', 'Waterfall', 'Lake', 'Forest', 'Volcano', 'Cave', 'Canyon', 'Desert', 'Rainforest'],
    'Activity': ['Adventure Park', 'Water Sports', 'Hiking Trail', 'Ski Resort', 'Zip Line', 'Biking', 'Scuba Diving', 'Paragliding', 'Rafting'],
    'Cultural': ['Temple', 'Church', 'Mosque', 'Historical Site', 'Ancient Ruins', 'Monastery', 'Shrine', 'Pagoda', 'Synagogue'],
    'Food': ['Restaurant', 'Cafe', 'Food Market', 'Winery', 'Street Food', 'Bakery', 'Brewery', 'Tea House', 'Chocolate Factory'],
    'Shopping': ['Mall', 'Market', 'Boutique', 'Shopping Street', 'Outlet', 'Souvenir Shop', 'Department Store']
}

all_tags = [
    'romantic', 'family_friendly', 'adventure', 'budget', 'luxury',
    'historical', 'modern', 'photography', 'nature', 'cultural',
    'indoor', 'outdoor', 'peaceful', 'famous', 'local', 'hidden_gem',
    'sunset_view', 'nightlife', 'art', 'architecture', 'wildlife',
    'hiking', 'swimming', 'shopping', 'dining', 'spiritual', 'educational',
    'accessible', 'pet_friendly', 'instagrammable', 'sunrise', 'sunset',
    'beachfront', 'mountain_view', 'city_view', 'garden', 'waterfront'
]

# User profiles
user_profiles = {
    'adventure_seeker': {
        'name': 'Adventure Seeker',
        'preferred_categories': ['Nature', 'Activity'],
        'preferred_tags': ['adventure', 'outdoor', 'nature', 'hiking', 'swimming'],
        'budget': ['$', '$$']
    },
    'culture_lover': {
        'name': 'Culture Lover',
        'preferred_categories': ['Museum', 'Cultural', 'Landmark'],
        'preferred_tags': ['historical', 'cultural', 'art', 'architecture', 'educational'],
        'budget': ['$$', '$$$']
    },
    'relaxation_seeker': {
        'name': 'Relaxation Seeker',
        'preferred_categories': ['Nature', 'Food'],
        'preferred_tags': ['peaceful', 'family_friendly', 'romantic', 'scenic'],
        'budget': ['$$']
    },
    'budget_traveler': {
        'name': 'Budget Traveler',
        'preferred_categories': ['Nature', 'Food', 'Shopping'],
        'preferred_tags': ['budget', 'local', 'hidden_gem', 'street_food'],
        'budget': ['$']
    },
    'luxury_traveler': {
        'name': 'Luxury Traveler',
        'preferred_categories': ['Landmark', 'Cultural', 'Food'],
        'preferred_tags': ['luxury', 'famous', 'romantic', 'fine_dining'],
        'budget': ['$$$']
    },
    'foodie': {
        'name': 'Food Enthusiast',
        'preferred_categories': ['Food'],
        'preferred_tags': ['local', 'food', 'cultural', 'dining', 'street_food'],
        'budget': ['$$', '$$$']
    },
    'photographer': {
        'name': 'Photography Enthusiast',
        'preferred_categories': ['Landmark', 'Nature'],
        'preferred_tags': ['photography', 'sunset_view', 'architecture', 'scenic'],
        'budget': ['$$']
    },
    'family_traveler': {
        'name': 'Family Traveler',
        'preferred_categories': ['Nature', 'Activity', 'Museum'],
        'preferred_tags': ['family_friendly', 'educational', 'safe', 'fun'],
        'budget': ['$$']
    }
}

# Expanded cities for 10,000 destinations
cities = [
    # Europe
    ('Paris', 'France', 48.8566, 2.3522, 'Europe'),
    ('Rome', 'Italy', 41.9028, 12.4964, 'Europe'),
    ('Barcelona', 'Spain', 41.3851, 2.1734, 'Europe'),
    ('London', 'UK', 51.5074, -0.1278, 'Europe'),
    ('Amsterdam', 'Netherlands', 52.3676, 4.9041, 'Europe'),
    ('Berlin', 'Germany', 52.5200, 13.4050, 'Europe'),
    ('Lisbon', 'Portugal', 38.7223, -9.1393, 'Europe'),
    ('Prague', 'Czech Republic', 50.0755, 14.4378, 'Europe'),
    ('Vienna', 'Austria', 48.2082, 16.3738, 'Europe'),
    ('Athens', 'Greece', 37.9838, 23.7275, 'Europe'),
    ('Oslo', 'Norway', 59.9139, 10.7522, 'Europe'),
    ('Stockholm', 'Sweden', 59.3293, 18.0686, 'Europe'),
    ('Copenhagen', 'Denmark', 55.6761, 12.5683, 'Europe'),
    ('Helsinki', 'Finland', 60.1699, 24.9384, 'Europe'),
    ('Dublin', 'Ireland', 53.3498, -6.2603, 'Europe'),
    ('Edinburgh', 'UK', 55.9533, -3.1883, 'Europe'),
    ('Venice', 'Italy', 45.4408, 12.3155, 'Europe'),
    ('Florence', 'Italy', 43.7696, 11.2558, 'Europe'),
    ('Seville', 'Spain', 37.3891, -5.9845, 'Europe'),
    ('Munich', 'Germany', 48.1351, 11.5820, 'Europe'),
    ('Warsaw', 'Poland', 52.2297, 21.0122, 'Europe'),
    ('Budapest', 'Hungary', 47.4979, 19.0402, 'Europe'),
    ('Krakow', 'Poland', 50.0647, 19.9450, 'Europe'),
    ('Tallinn', 'Estonia', 59.4370, 24.7536, 'Europe'),
    ('Riga', 'Latvia', 56.9496, 24.1052, 'Europe'),
    ('Belgrade', 'Serbia', 44.7866, 20.4489, 'Europe'),
    ('Sarajevo', 'Bosnia', 43.8563, 18.4131, 'Europe'),
    ('Tbilisi', 'Georgia', 41.7151, 44.8271, 'Europe/Asia'),
    ('Brussels', 'Belgium', 50.8503, 4.3517, 'Europe'),
    ('Zurich', 'Switzerland', 47.3769, 8.5417, 'Europe'),
    ('Geneva', 'Switzerland', 46.2044, 6.1432, 'Europe'),
    ('Milan', 'Italy', 45.4642, 9.1900, 'Europe'),
    ('Naples', 'Italy', 40.8518, 14.2681, 'Europe'),
    
    # Asia
    ('Tokyo', 'Japan', 35.6762, 139.6503, 'Asia'),
    ('Bangkok', 'Thailand', 13.7563, 100.5018, 'Asia'),
    ('Singapore', 'Singapore', 1.3521, 103.8198, 'Asia'),
    ('Kyoto', 'Japan', 35.0116, 135.7680, 'Asia'),
    ('Mumbai', 'India', 19.0760, 72.8777, 'Asia'),
    ('Delhi', 'India', 28.7041, 77.1025, 'Asia'),
    ('Shanghai', 'China', 31.2304, 121.4737, 'Asia'),
    ('Beijing', 'China', 39.9042, 116.4074, 'Asia'),
    ('Seoul', 'South Korea', 37.5665, 126.9780, 'Asia'),
    ('Jakarta', 'Indonesia', -6.2088, 106.8456, 'Asia'),
    ('Kuala Lumpur', 'Malaysia', 3.1390, 101.6869, 'Asia'),
    ('Hong Kong', 'China', 22.3193, 114.1694, 'Asia'),
    ('Taipei', 'Taiwan', 25.0330, 121.5654, 'Asia'),
    ('Manila', 'Philippines', 14.5995, 120.9842, 'Asia'),
    ('Ho Chi Minh', 'Vietnam', 10.8231, 106.6297, 'Asia'),
    ('Hanoi', 'Vietnam', 21.0278, 105.8342, 'Asia'),
    ('Yangon', 'Myanmar', 16.8409, 96.1735, 'Asia'),
    ('Kathmandu', 'Nepal', 27.7172, 85.3240, 'Asia'),
    ('Colombo', 'Sri Lanka', 6.9271, 79.8612, 'Asia'),
    
    # North America
    ('New York', 'USA', 40.7128, -74.0060, 'North America'),
    ('San Francisco', 'USA', 37.7749, -122.4194, 'North America'),
    ('Vancouver', 'Canada', 49.2827, -123.1207, 'North America'),
    ('Mexico City', 'Mexico', 19.4326, -99.1332, 'North America'),
    ('Los Angeles', 'USA', 34.0522, -118.2437, 'North America'),
    ('Chicago', 'USA', 41.8781, -87.6298, 'North America'),
    ('Miami', 'USA', 25.7617, -80.1918, 'North America'),
    ('Toronto', 'Canada', 43.6532, -79.3832, 'North America'),
    ('Montreal', 'Canada', 45.5017, -73.5673, 'North America'),
    ('Las Vegas', 'USA', 36.1699, -115.1398, 'North America'),
    ('Orlando', 'USA', 28.5383, -81.3792, 'North America'),
    ('Washington', 'USA', 38.9072, -77.0369, 'North America'),
    ('Boston', 'USA', 42.3601, -71.0589, 'North America'),
    ('Seattle', 'USA', 47.6062, -122.3321, 'North America'),
    
    # South America
    ('Rio', 'Brazil', -22.9068, -43.1729, 'South America'),
    ('Cusco', 'Peru', -13.5319, -71.9675, 'South America'),
    ('Buenos Aires', 'Argentina', -34.6037, -58.3816, 'South America'),
    ('Santiago', 'Chile', -33.4489, -70.6693, 'South America'),
    ('Lima', 'Peru', -12.0464, -77.0428, 'South America'),
    ('Bogota', 'Colombia', 4.7110, -74.0721, 'South America'),
    ('Medellin', 'Colombia', 6.2442, -75.5812, 'South America'),
    ('Quito', 'Ecuador', -0.1807, -78.4678, 'South America'),
    ('La Paz', 'Bolivia', -16.5000, -68.1500, 'South America'),
    ('Montevideo', 'Uruguay', -34.9011, -56.1645, 'South America'),
    
    # Africa
    ('Cape Town', 'South Africa', -33.9249, 18.4241, 'Africa'),
    ('Marrakech', 'Morocco', 31.6295, -7.9811, 'Africa'),
    ('Cairo', 'Egypt', 30.0444, 31.2357, 'Africa'),
    ('Nairobi', 'Kenya', -1.2921, 36.8219, 'Africa'),
    ('Johannesburg', 'South Africa', -26.2041, 28.0473, 'Africa'),
    ('Durban', 'South Africa', -29.8587, 31.0218, 'Africa'),
    ('Accra', 'Ghana', 5.6037, -0.1870, 'Africa'),
    ('Lagos', 'Nigeria', 6.5244, 3.3792, 'Africa'),
    ('Casablanca', 'Morocco', 33.5731, -7.5898, 'Africa'),
    ('Tunis', 'Tunisia', 36.8065, 10.1815, 'Africa'),
    ('Alexandria', 'Egypt', 31.2001, 29.9187, 'Africa'),
    ('Addis Ababa', 'Ethiopia', 9.0320, 38.7469, 'Africa'),
    
    # Middle East
    ('Dubai', 'UAE', 25.2048, 55.2708, 'Middle East'),
    ('Istanbul', 'Turkey', 41.0082, 28.9784, 'Europe/Asia'),
    ('Abu Dhabi', 'UAE', 24.4539, 54.3773, 'Middle East'),
    ('Doha', 'Qatar', 25.2854, 51.5310, 'Middle East'),
    ('Riyadh', 'Saudi Arabia', 24.7136, 46.6753, 'Middle East'),
    ('Muscat', 'Oman', 23.5880, 58.3829, 'Middle East'),
    ('Tel Aviv', 'Israel', 32.0853, 34.7818, 'Middle East'),
    ('Jerusalem', 'Israel', 31.7683, 35.2137, 'Middle East'),
    ('Amman', 'Jordan', 31.9454, 35.9284, 'Middle East'),
    ('Beirut', 'Lebanon', 33.8938, 35.5018, 'Middle East'),
    
    # Oceania
    ('Sydney', 'Australia', -33.8688, 151.2093, 'Oceania'),
    ('Auckland', 'New Zealand', -36.8485, 174.7633, 'Oceania'),
    ('Melbourne', 'Australia', -37.8136, 144.9631, 'Oceania'),
    ('Brisbane', 'Australia', -27.4698, 153.0251, 'Oceania'),
    ('Perth', 'Australia', -31.9505, 115.8605, 'Oceania'),
    ('Wellington', 'New Zealand', -41.2865, 174.7762, 'Oceania'),
    ('Christchurch', 'New Zealand', -43.5321, 172.6362, 'Oceania'),
    ('Gold Coast', 'Australia', -28.0167, 153.4000, 'Oceania'),
    ('Queenstown', 'New Zealand', -45.0312, 168.6626, 'Oceania'),
    
    # Caribbean
    ('Havana', 'Cuba', 23.1136, -82.3666, 'Caribbean'),
    ('San Juan', 'Puerto Rico', 18.4655, -66.1057, 'Caribbean'),
    ('Kingston', 'Jamaica', 17.9714, -76.7934, 'Caribbean'),
    ('Santo Domingo', 'Dominican Republic', 18.4861, -69.9312, 'Caribbean'),
    ('Nassau', 'Bahamas', 25.0443, -77.3504, 'Caribbean'),
    ('Bridgetown', 'Barbados', 13.0975, -59.6165, 'Caribbean'),
    ('Port of Spain', 'Trinidad', 10.6549, -61.5019, 'Caribbean'),
]

# ============================================
# Generate 10,000 Destinations
# ============================================

print(f"\n[2/5] Generating {NUM_DESTINATIONS} destinations...")

destinations = []
destination_id = 1

# Ensure coverage across 195 countries
countries_used = set()

# Pre-generate all country-city combinations for variety
city_combinations = []
for city_data in cities:
    city_combinations.append(city_data)

for i in range(NUM_DESTINATIONS):
    # Cycle through cities to ensure variety
    city_data = city_combinations[i % len(city_combinations)]
    city, country, lat, lng, region = city_data
    countries_used.add(country)
    
    category = random.choice(list(categories.keys()))
    subcategory = random.choice(categories[category])
    
    # Generate diverse names
    name_prefixes = ['Historic', 'Royal', 'Grand', 'Ancient', 'Modern', 'Traditional', 'Beautiful', 'Sacred', 'Famous', 'Hidden']
    name_suffixes = ['Gardens', 'Palace', 'Temple', 'Museum', 'Square', 'Bridge', 'Tower', 'Cathedral', 'Castle', 'Market']
    
    if random.random() < 0.3:
        name = f"{random.choice(name_prefixes)} {subcategory} of {city}"
    elif random.random() < 0.6:
        name = f"{city} {random.choice(['Grand', 'Royal', 'Historic'])} {subcategory}"
    else:
        name = f"{city} {subcategory}"
    
    # Generate tags (4-8 tags)
    num_tags = random.randint(4, 8)
    dest_tags = random.sample(all_tags, num_tags)
    
    # Add category-specific tags
    if category == 'Nature':
        dest_tags.extend(['nature', 'scenic', 'outdoor', 'fresh_air'])
    elif category == 'Museum':
        dest_tags.extend(['educational', 'indoor', 'art', 'history'])
    elif category == 'Landmark':
        dest_tags.extend(['iconic', 'tourist_favorite', 'photo_spot'])
    elif category == 'Activity':
        dest_tags.extend(['active', 'fun', 'exciting'])
    elif category == 'Food':
        dest_tags.extend(['delicious', 'cuisine', 'local_flavor'])
    
    dest_tags = list(set(dest_tags))[:8]
    
    # Price level
    price_weights = {
        'Landmark': {'$': 0.3, '$$': 0.5, '$$$': 0.2},
        'Museum': {'$': 0.5, '$$': 0.4, '$$$': 0.1},
        'Nature': {'$': 0.6, '$$': 0.3, '$$$': 0.1},
        'Activity': {'$': 0.2, '$$': 0.5, '$$$': 0.3},
        'Cultural': {'$': 0.4, '$$': 0.5, '$$$': 0.1},
        'Food': {'$': 0.3, '$$': 0.5, '$$$': 0.2},
        'Shopping': {'$': 0.3, '$$': 0.5, '$$$': 0.2}
    }
    weights = price_weights.get(category, {'$': 0.33, '$$': 0.34, '$$$': 0.33})
    price_level = random.choices(['$', '$$', '$$$'], weights=[weights['$'], weights['$$'], weights['$$$']])[0]
    
    # Rating
    rating_base = 3.5
    if 'famous' in dest_tags:
        rating_base += 0.5
    if 'luxury' in dest_tags:
        rating_base += 0.3
    rating = np.random.normal(rating_base, 0.4)
    rating = max(1.0, min(5.0, round(rating, 1)))
    
    # Popularity score
    popularity_base = 50
    if 'famous' in dest_tags:
        popularity_base += 30
    if 'iconic' in dest_tags:
        popularity_base += 20
    popularity = np.random.normal(popularity_base, 15)
    popularity = max(0, min(100, int(popularity)))
    
    # Budget per day
    budget_per_day = random.randint(20, 400)
    
    # Description
    descriptions = {
        'Landmark': f"{name} stands as a testament to {city}'s rich history and architectural brilliance. This iconic {subcategory.lower()} attracts millions of visitors annually with its stunning design and cultural significance.",
        'Museum': f"Step into {name} and embark on a journey through time. This {subcategory.lower()} houses an impressive collection of artifacts and artworks that tell the story of {region}'s heritage.",
        'Nature': f"Discover the natural wonders at {name}. This breathtaking {subcategory.lower()} offers visitors a chance to connect with nature through scenic trails, diverse wildlife, and unforgettable vistas.",
        'Activity': f"Get your adrenaline pumping at {name}! This premier {subcategory.lower()} destination offers thrilling experiences for adventurers of all skill levels.",
        'Cultural': f"Experience the spiritual heart of {city} at {name}. This sacred {subcategory.lower()} provides insight into local traditions and centuries-old customs.",
        'Food': f"Savor the flavors of {city} at {name}. This beloved {subcategory.lower()} serves authentic local cuisine that will delight your taste buds.",
        'Shopping': f"Indulge in retail therapy at {name}. This {subcategory.lower()} features a curated selection of local crafts, designer brands, and unique finds."
    }
    
    description = descriptions.get(category, f"{name} is a must-visit destination in {city}.")
    description += f" Perfect for {', '.join(dest_tags[:3])} enthusiasts."
    
    # Best season
    if category == 'Nature':
        best_season = random.choice(['Spring', 'Summer'])
    elif category == 'Activity':
        best_season = random.choice(['Summer', 'Winter'])
    else:
        best_season = random.choice(['Spring', 'Summer', 'Autumn', 'Winter'])
    
    # Top attractions
    top_attractions = ', '.join(random.sample(dest_tags, min(3, len(dest_tags))))
    
    # Image URL (Unsplash direct - will be downloaded later)
    image_url = f"https://source.unsplash.com/featured/800x500?{city},{category.lower()},{random.randint(1, 100)}"
    
    destination = {
        'id': destination_id,
        'place_name': name,
        'city': city,
        'country': country,
        'region': region,
        'latitude': round(lat + random.uniform(-0.5, 0.5), 4),
        'longitude': round(lng + random.uniform(-0.5, 0.5), 4),
        'category': category,
        'subcategory': subcategory,
        'price_level': price_level,
        'budget_per_day_usd': budget_per_day,
        'avg_user_rating': rating,
        'popularity_score': popularity,
        'tags': ','.join(dest_tags),
        'description': description,
        'best_season': best_season,
        'estimated_hours': round(random.uniform(1, 5), 1),
        'top_attractions': top_attractions,
        'image_url': image_url,
        'image_paths': ''  # Will be filled by image downloader
    }
    
    destinations.append(destination)
    destination_id += 1
    
    # Progress indicator
    if i % 1000 == 0:
        print(f"   Generated {i} destinations...")

destinations_df = pd.DataFrame(destinations)
print(f"  ✓ Generated {len(destinations_df)} destinations in {len(countries_used)} countries")

# ============================================
# Generate Users (100 users)
# ============================================

print(f"\n[3/5] Generating {NUM_USERS} users...")

users = []
for i in range(NUM_USERS):
    profile_type = random.choice(list(user_profiles.keys()))
    profile = user_profiles[profile_type]
    
    # Generate preferred categories (2-5 categories)
    num_categories = random.randint(2, 5)
    pref_categories = random.sample(list(categories.keys()), num_categories)
    for cat in profile['preferred_categories']:
        if cat not in pref_categories:
            pref_categories.append(cat)
    pref_categories = list(set(pref_categories))
    
    # Generate preferred tags (4-8 tags)
    num_tags = random.randint(4, 8)
    pref_tags = random.sample(all_tags, num_tags)
    for tag in profile['preferred_tags']:
        if tag not in pref_tags:
            pref_tags.append(tag)
    pref_tags = list(set(pref_tags))[:8]
    
    travel_styles = ['Solo', 'Couple', 'Family', 'Friends']
    travel_style_weights = [0.2, 0.3, 0.3, 0.2]
    
    user = {
        'user_id': i + 1,
        'username': f"traveler_{i+1}",
        'email': f"traveler_{i+1}@example.com",
        'age': random.randint(18, 75),
        'gender': random.choice(['M', 'F']),
        'profile_type': profile_type,
        'profile_name': profile['name'],
        'travel_style': random.choices(travel_styles, weights=travel_style_weights)[0],
        'budget_preference': random.choice(profile['budget']),
        'preferred_categories': ','.join(pref_categories),
        'preferred_tags': ','.join(pref_tags),
        'experience_level': random.choice(['Beginner', 'Intermediate', 'Expert']),
        'created_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
    }
    
    users.append(user)

users_df = pd.DataFrame(users)
print(f"  ✓ Generated {len(users_df)} users")

# ============================================
# Generate Ratings (100 users × 10,000 destinations × 15% density)
# ============================================

print(f"\n[4/5] Generating {NUM_USERS} × {NUM_DESTINATIONS} × {RATING_DENSITY} ratings...")

ratings = []
rating_id = 1
total_ratings = int(NUM_USERS * NUM_DESTINATIONS * RATING_DENSITY)

for user_idx, (_, user) in enumerate(users_df.iterrows()):
    user_id = user['user_id']
    profile_type = user['profile_type']
    profile = user_profiles[profile_type]
    
    user_categories = set(user['preferred_categories'].split(','))
    user_tags = set(user['preferred_tags'].split(','))
    user_budget = user['budget_preference']
    
    # Select random subset of destinations to rate (15%)
    sample_size = int(NUM_DESTINATIONS * RATING_DENSITY)
    selected_destinations = destinations_df.sample(n=sample_size)
    
    for _, dest in selected_destinations.iterrows():
        rating = 3.0
        
        # Category match (0-2 points)
        if dest['category'] in user_categories:
            rating += 1.5
        
        # Tag match (0-2 points)
        dest_tags = set(dest['tags'].split(','))
        tag_overlap = len(user_tags.intersection(dest_tags))
        rating += min(tag_overlap * 0.2, 1.5)
        
        # Budget match (0-1 point)
        if dest['price_level'] == user_budget:
            rating += 0.8
        elif (dest['price_level'] == '$' and user_budget == '$$') or \
             (dest['price_level'] == '$$' and user_budget == '$$$'):
            rating += 0.3
        
        # Profile-specific bonuses (0-1 point)
        if profile_type == 'adventure_seeker' and dest['category'] in ['Nature', 'Activity']:
            rating += 0.8
        elif profile_type == 'culture_lover' and dest['category'] in ['Museum', 'Cultural', 'Landmark']:
            rating += 0.8
        elif profile_type == 'foodie' and dest['category'] == 'Food':
            rating += 1.0
        elif profile_type == 'photographer' and ('photography' in dest_tags or 'sunset_view' in dest_tags):
            rating += 0.7
        elif profile_type == 'family_traveler' and 'family_friendly' in dest_tags:
            rating += 0.8
        
        rating = max(1.0, min(5.0, rating))
        rating += random.gauss(0, 0.2)
        rating = max(0.5, min(5.0, round(rating, 1)))
        
        ratings.append({
            'rating_id': rating_id,
            'user_id': user_id,
            'destination_id': dest['id'],
            'rating': rating,
            'timestamp': (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d %H:%M:%S')
        })
        rating_id += 1
    
    if user_idx % 10 == 0:
        print(f"   Generated ratings for {user_idx+1} users...")

ratings_df = pd.DataFrame(ratings)
print(f"  ✓ Generated {len(ratings_df)} ratings")

# ============================================
# Save all data
# ============================================

print("\n[5/5] Saving data...")

# Save to CSV
destinations_df.to_csv('data/raw/destinations.csv', index=False)
users_df.to_csv('data/raw/users.csv', index=False)
ratings_df.to_csv('data/raw/ratings.csv', index=False)

# Save metadata
metadata = {
    'num_destinations': len(destinations_df),
    'num_users': len(users_df),
    'num_ratings': len(ratings_df),
    'num_countries': len(countries_used),
    'rating_density': len(ratings_df) / (len(destinations_df) * len(users_df)),
    'generated_date': datetime.now().isoformat(),
    'categories': list(categories.keys()),
    'user_profiles': list(user_profiles.keys())
}

with open('data/raw/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("  ✓ Data saved to data/raw/")

# ============================================
# Summary
# ============================================

print("\n" + "="*60)
print("DATA GENERATION COMPLETE!")
print("="*60)

print(f"\n📊 Data Summary:")
print(f"  • Destinations: {len(destinations_df)} ✅")
print(f"  • Users: {len(users_df)}")
print(f"  • Ratings: {len(ratings_df)}")
print(f"  • Countries: {len(countries_used)}")
print(f"  • Rating density: {len(ratings_df)/(len(destinations_df)*len(users_df)):.2%}")
print(f"  • Total rows: {len(destinations_df) + len(users_df) + len(ratings_df):,}")

print(f"\n📁 Files created:")
print(f"  • data/raw/destinations.csv ({len(destinations_df):,} rows)")
print(f"  • data/raw/users.csv ({len(users_df)} rows)")
print(f"  • data/raw/ratings.csv ({len(ratings_df):,} rows)")
print(f"  • data/raw/metadata.json")

print(f"\n📈 Sample Statistics:")
print(f"  • Avg rating: {ratings_df['rating'].mean():.2f}")
print(f"  • Most popular category: {destinations_df['category'].mode()[0]}")
print(f"  • Most common user type: {users_df['profile_type'].mode()[0]}")

print("\n" + "="*60)
print("✅ Data generation successful!")
print("="*60)
print("\nNext steps:")
print("  1. Run: python download_images.py (to download images for destinations)")
print("  2. Run: python retrain_models.py (to train models)")
print("  3. Run: streamlit run app.py (to launch the app)")