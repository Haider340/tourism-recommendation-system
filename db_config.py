# db_config.py - SQLite Version (Works on Streamlit Cloud)
import sqlite3
import bcrypt
import streamlit as st
from datetime import datetime
import os
import json

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'travelgenie.db')

def get_db_connection():
    """Create and return a SQLite database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize SQLite database tables"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Create all tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            region TEXT,
            latitude REAL,
            longitude REAL,
            category TEXT,
            subcategory TEXT,
            price_level TEXT,
            budget_per_day_usd INTEGER,
            avg_user_rating REAL,
            popularity_score INTEGER,
            tags TEXT,
            description TEXT,
            best_season TEXT,
            image_paths TEXT,
            top_attractions TEXT
        );
        
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5),
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            status TEXT DEFAULT 'wishlist',
            priority TEXT,
            personal_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (destination_id) REFERENCES destinations(id) ON DELETE CASCADE,
            UNIQUE(user_id, destination_id)
        );
        
        CREATE TABLE IF NOT EXISTS saved_itineraries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            itinerary_name TEXT NOT NULL,
            destination_ids TEXT,
            itinerary_text TEXT,
            total_budget REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS expense_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            destination_id INTEGER,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            expense_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT DEFAULT 'info',
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username, email, password, full_name=None):
    """Register a new user"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            return False, "Username or email already exists"
        
        hashed_pw = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (username, email, hashed_pw, full_name)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO notifications (user_id, type, title, message) VALUES (?, ?, ?, ?)",
            (user_id, "info", "Welcome to TravelGenie!", "Start planning your dream trip!")
        )
        conn.commit()
        
        return True, "Registration successful! Please login."
    except Exception as e:
        return False, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    """Authenticate a user"""
    conn = get_db_connection()
    if not conn:
        return None, "Database connection failed"
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
        user = cursor.fetchone()
        
        if not user:
            return None, "Invalid username or email"
        
        if not verify_password(password, user['password_hash']):
            return None, "Invalid password"
        
        cursor.execute("UPDATE users SET last_seen = ? WHERE id = ?", (datetime.now(), user['id']))
        conn.commit()
        
        return dict(user), "Login successful"
    except Exception as e:
        return None, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()

def save_user_rating(user_id, destination_id, rating, destination_name, category, city, country):
    """Save or update a user's rating"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO reviews (user_id, destination_id, rating, review_text) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, destination_id) DO UPDATE SET rating = ?",
            (user_id, destination_id, rating, "", rating)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving rating: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_ratings(user_id):
    """Get all ratings for a specific user"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """SELECT r.destination_id, r.rating, d.place_name, d.category, d.city, d.country
               FROM reviews r
               JOIN destinations d ON r.destination_id = d.id
               WHERE r.user_id = ?""",
            (user_id,)
        )
        results = cursor.fetchall()
        
        ratings = {}
        for row in results:
            ratings[row['place_name']] = {
                'destination_id': row['destination_id'],
                'rating': row['rating'],
                'category': row['category'],
                'city': row['city'],
                'country': row['country']
            }
        return ratings
    except Exception as e:
        return {}
    finally:
        cursor.close()
        conn.close()

def add_to_wishlist(user_id, destination_id, notes=""):
    """Add destination to wishlist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO wishlist (user_id, destination_id, personal_notes) VALUES (?, ?, ?)",
            (user_id, destination_id, notes)
        )
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_wishlist(user_id):
    """Get user's wishlist items"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT w.id as wishlist_id, d.*, w.status, w.priority, w.personal_notes 
            FROM wishlist w 
            JOIN destinations d ON w.destination_id = d.id 
            WHERE w.user_id = ?
            ORDER BY w.created_at DESC
        """, (user_id,))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def get_destinations(limit=None, country=None):
    """Fetch destinations from database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    query = "SELECT * FROM destinations WHERE 1=1"
    params = []
    
    if country:
        query += " AND country = ?"
        params.append(country)
    
    query += " ORDER BY avg_user_rating DESC"
    
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def get_reviews(destination_id):
    """Get all reviews for a destination"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT r.*, u.username 
            FROM reviews r 
            JOIN users u ON r.user_id = u.id 
            WHERE r.destination_id = ? 
            ORDER BY r.created_at DESC
        """, (destination_id,))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()

def save_itinerary(user_id, name, itinerary_text, destinations, budget):
    """Save generated itinerary"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO saved_itineraries (user_id, itinerary_name, destination_ids, itinerary_text, total_budget) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, json.dumps(destinations), itinerary_text, budget)
        )
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        cursor.close()
        conn.close()

def add_expense(user_id, category, amount, description, destination_id=None):
    """Add travel expense"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO expense_tracker (user_id, category, amount, description, destination_id, expense_date) VALUES (?, ?, ?, ?, ?, DATE('now'))",
            (user_id, category, amount, description, destination_id)
        )
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_expenses(user_id):
    """Get user's expenses"""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM expense_tracker WHERE user_id = ? ORDER BY expense_date DESC",
            (user_id,)
        )
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        return []
    finally:
        cursor.close()
        conn.close()