"""
JouneyBloom - Complete Tourism Recommendation Web App
"""
import re
import ollama
from pathlib import Path
import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import mysql.connector
import bcrypt
import json
import os
import requests
from datetime import datetime, timedelta
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import folium_static
import random
import time

# Import custom modules
from db_config import (
    get_db_connection, 
    init_database, 
    register_user, 
    login_user,
    save_user_rating,
    get_user_ratings,
    add_to_wishlist,
    get_user_wishlist,
    get_destinations,
    get_reviews,
    save_itinerary,
    add_expense,
    get_user_expenses
)
import ollama

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="Tourism Recommendation ",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"  # No sidebar!
)

# ========== CUSTOM CSS FOR PROFESSIONAL UI ==========
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .stApp header {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 0;
    }
    
    /* Navbar styling */
    .navbar {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    
    /* Card styling */
    .destination-card {
        background: white;
        border-radius: 15px;
        padding: 15px;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    .destination-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Rating stars */
    .star-rating {
        color: #ffc107;
        font-size: 20px;
    }
    
    /* Welcome text */
    .welcome-text {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    /* Chat interface */
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 80%;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        float: right;
    }
    
    .assistant-message {
        background: #f0f2f6;
        color: #333;
        float: left;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE INITIALIZATION ==========
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'show_all_destinations' not in st.session_state:
    st.session_state.show_all_destinations = False




# ========== DATABASE FUNCTIONS ==========
def check_login(username, password):
    """Verify user credentials"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, username))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return user
    return None

def register_user(username, email, password, full_name=None):
    """Register a new user - SQLite version"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    cursor = conn.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            return False, "Username or email already exists"
        
        # Hash password and insert
        hashed_pw = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (username, email, hashed_pw, full_name)
        )
        conn.commit()
        return True, "Registration successful! Please login."
    except Exception as e:
        return False, f"Database error: {e}"
    finally:
        cursor.close()
        conn.close()
    return False

def get_destinations(limit=None, country=None):
    """Fetch destinations from database"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM destinations WHERE 1=1"
        params = []
        if country:
            query += " AND country = %s"
            params.append(country)
        query += " ORDER BY avg_user_rating DESC"
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    return []

def get_user_wishlist(user_id):
    """Get user's wishlist items with proper IDs"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT w.id as wishlist_id, d.*, w.status, w.priority, w.personal_notes 
            FROM wishlist w 
            JOIN destinations d ON w.destination_id = d.id 
            WHERE w.user_id = %s
            ORDER BY w.created_at DESC
        """, (user_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    return []

def add_to_wishlist(user_id, destination_id, notes=""):
    """Add destination to wishlist"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO wishlist (user_id, destination_id, personal_notes) VALUES (%s, %s, %s)",
                (user_id, destination_id, notes)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except:
            return False
    return False

def add_review(user_id, destination_id, rating, review_text):
    """Add or update a review"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Check if review exists
            cursor.execute(
                "SELECT id FROM reviews WHERE user_id = %s AND destination_id = %s",
                (user_id, destination_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    "UPDATE reviews SET rating = %s, review_text = %s, updated_at = NOW() WHERE user_id = %s AND destination_id = %s",
                    (rating, review_text, user_id, destination_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO reviews (user_id, destination_id, rating, review_text) VALUES (%s, %s, %s, %s)",
                    (user_id, destination_id, rating, review_text)
                )
            
            # Update destination average rating
            cursor.execute(
                "UPDATE destinations SET avg_user_rating = (SELECT AVG(rating) FROM reviews WHERE destination_id = %s), total_reviews = (SELECT COUNT(*) FROM reviews WHERE destination_id = %s) WHERE id = %s",
                (destination_id, destination_id, destination_id)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(e)
            return False
    return False

def get_reviews(destination_id):
    """Get all reviews for a destination"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, u.username, u.profile_pic 
            FROM reviews r 
            JOIN users u ON r.user_id = u.id 
            WHERE r.destination_id = %s 
            ORDER BY r.created_at DESC
        """, (destination_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    return []

def save_itinerary(user_id, name, itinerary_text, destinations, budget):
    """Save generated itinerary"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO saved_itineraries (user_id, itinerary_name, destination_ids, itinerary_text, total_budget) VALUES (%s, %s, %s, %s, %s)",
            (user_id, name, json.dumps(destinations), itinerary_text, budget)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    return False

def add_expense(user_id, category, amount, description, destination_id=None):
    """Add travel expense"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expense_tracker (user_id, category, amount, description, destination_id, expense_date) VALUES (%s, %s, %s, %s, %s, CURDATE())",
            (user_id, category, amount, description, destination_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    return False

def get_user_expenses(user_id):
    """Get user's expenses"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM expense_tracker WHERE user_id = %s ORDER BY expense_date DESC",
            (user_id,)
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    return []

def send_notification(user_id, title, message, notification_type="info"):
    """Send notification to user"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notifications (user_id, type, title, message) VALUES (%s, %s, %s, %s)",
            (user_id, notification_type, title, message)
        )
        conn.commit()
        cursor.close()
        conn.close()

def get_notifications(user_id):
    """Get user notifications"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM notifications WHERE user_id = %s AND is_read = FALSE ORDER BY created_at DESC",
            (user_id,)
        )
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    return []

def mark_notification_read(notification_id):
    """Mark notification as read"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = TRUE WHERE id = %s", (notification_id,))
        conn.commit()
        cursor.close()
        conn.close()

# Use your Colab tunnel URL
OLLAMA_HOST = "https://acquisition-convicted-steve-proposals.trycloudflare.com"



def generate_tour_plan(prompt):
    """Generate tour plan using Llama 3.2 3B on Colab"""
    try:
        # Connect to the remote Ollama server
        client = ollama.Client(host=OLLAMA_HOST)
        
        response = client.chat(
            model='llama3.2:3b',
            messages=[
                {
                    'role': 'system',
                    'content': """You are an expert travel planner AI. Generate detailed, practical tour plans.
                    Format your response with:
                    - Daily itinerary with specific times
                    - Budget breakdown (accommodation, food, activities, transport)
                    - Recommended places with names
                    - Local foods to try
                    - Tips for the traveler
                    Be specific and helpful."""
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            stream=False
        )
        return response['message']['content']
    except Exception as e:
        return f"⚠️ Error connecting to AI: {e}"
    
    
# ========== WEATHER API (Free - OpenWeatherMap) ==========
def get_weather(city, country):
    """Get real-time weather for destination"""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    if not api_key:
        return "🌤️ Weather data available with API key. Get free key from openweathermap.org"
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            condition = data['weather'][0]['description']
            return f"🌡️ {temp}°C, {condition}"
        return "Weather data unavailable"
    except:
        return "Weather service unavailable"

# ========== CURRENCY CONVERTER (Free API) ==========
def convert_currency(amount, from_currency="USD", to_currency="EUR"):
    """Convert currency using free Frankfurter API"""
    try:
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['rates'][to_currency]
        return amount
    except:
        return amount

# ========== NAVIGATION BAR ==========
def render_navbar():
    """Render navbar using Streamlit buttons - 100% reliable"""
    
    # Custom CSS for navbar styling
    st.markdown("""
    <style>
    /* Navbar container */
    .stNavbar {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 12px 20px;
        border-radius: 0 0 20px 20px;
        margin-bottom: 25px;
    }
    
    /* Style all buttons in the navbar */
    .stNavbar button {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 8px 18px !important;
        margin: 0 5px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stNavbar button:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        transform: translateY(-2px);
    }
    
    /* Active page styling */
    .stNavbar button.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Logout button hover */
    .stNavbar button:last-child:hover {
        background: #dc2626 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create navbar container
    with st.container():
        st.markdown('<div class="stNavbar">', unsafe_allow_html=True)
        
        # Create columns for each nav item
        cols = st.columns([1.5, 0.9, 1, 0.9, 0.9, 1, 1, 0.8, 0.8])
        
        # Logo
        with cols[0]:
            st.markdown("**🌍 JouneyBloom**")
        
        # Home
        with cols[1]:
            if st.button("🏠 Home", key="nav_home", use_container_width=True):
                st.session_state.current_page = "Home"
                st.rerun()
        
        # chatbot
        with cols[2]:
            if st.button("🤖 chatbot", key="nav_ai", use_container_width=True):
                st.session_state.current_page = "chatbot"
                st.rerun()
        
        # My Trips
        with cols[3]:
            if st.button("📋 My Trips", key="nav_trips", use_container_width=True):
                st.session_state.current_page = "My Trips"
                st.rerun()
        
        # Wishlist
        with cols[4]:
            if st.button("❤️ Wishlist", key="nav_wishlist", use_container_width=True):
                st.session_state.current_page = "Wishlist"
                st.rerun()
        
        # Expenses
        with cols[5]:
            if st.button("💰 Expenses", key="nav_expenses", use_container_width=True):
                st.session_state.current_page = "Expenses"
                st.rerun()
        
        # All Destinations
        with cols[6]:
            if st.button("🌍 All Destinations", key="nav_all", use_container_width=True):
                st.session_state.current_page = "All Destinations"
                st.rerun()
        
        # Notifications
        with cols[7]:
            if st.session_state.logged_in:
                notifs = get_notifications(st.session_state.user_id)
                count = len(notifs)
                btn_text = f"🔔 {count}" if count > 0 else "🔔"
                if st.button(btn_text, key="nav_notif", use_container_width=True):
                    st.session_state.current_page = "Notifications"
                    st.rerun()
        
        # Logout
        with cols[8]:
            if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.user_id = None
                st.session_state.current_page = "Home"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ========== HOMEPAGE ==========
def render_homepage():
    """Beautiful homepage with relevant images after login"""
    
    # Welcome banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 40px; margin: 20px 0; text-align: center;">
        <h1 style="color: white; font-size: 3rem;">✈️ Welcome back, {st.session_state.username}! 🌍</h1>
        <p style="color: white; font-size: 1.2rem;">Where shall we take you today? Your next adventure awaits!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick chatbot input
    st.markdown("### ✨ Plan Your Next Trip Instantly")
    col1, col2 = st.columns([4, 1])
    with col1:
        quick_prompt = st.text_input("", placeholder="Example: 'Plan a 5-day romantic honeymoon to Bali with $1500 budget'", label_visibility="collapsed")
    with col2:
        if st.button("✨ Generate Plan", use_container_width=True):
            if quick_prompt:
                st.session_state.current_page = "chatbot"
                st.session_state.quick_prompt = quick_prompt
                st.rerun()
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    wishlist_count = len(get_user_wishlist(st.session_state.user_id))
    
    with col1:
        st.metric("❤️ Places Wishlisted", wishlist_count)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM saved_itineraries WHERE user_id = %s", (st.session_state.user_id,))
        trips_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE user_id = %s", (st.session_state.user_id,))
        reviews_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    else:
        trips_count = 0
        reviews_count = 0
    
    with col2:
        st.metric("📋 Planned Trips", trips_count)
    with col3:
        st.metric("⭐ Reviews Written", reviews_count)
    with col4:
        if st.button("🌏 195+ Countries", use_container_width=True):
            st.session_state.current_page = "All Destinations"
            st.rerun()
    
    # Trending Destinations Section
    st.markdown("---")
    st.markdown("### 🔥 Trending Destinations This Week")
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM destinations 
            WHERE image_paths IS NOT NULL AND image_paths != '' 
            ORDER BY avg_user_rating DESC 
            LIMIT 6
        """)
        trending_dests = cursor.fetchall()
        cursor.close()
        conn.close()
    else:
        trending_dests = []
    
    if trending_dests:
        # Display as a grid using columns
        for i in range(0, len(trending_dests), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(trending_dests):
                    dest = trending_dests[idx]
                    with cols[j]:
                        # Show image
                        image_path = dest.get('image_paths', '')
                        if image_path:
                            first_image = image_path.split(',')[0].strip()
                            try:
                                st.image(first_image, use_container_width=True)
                            except:
                                st.image("https://via.placeholder.com/300x200?text=Travel", use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/300x200?text=Travel", use_container_width=True)
                        
                        st.subheader(dest['place_name'])
                        st.write(f"📍 {dest['city']}, {dest['country']}")
                        st.write(f"⭐ {dest['avg_user_rating'] or 'New'} | 💵 ${dest['budget_per_day_usd']}/day")
                        
                        # Updated button with unique key and navigation
                        button_key = f"trending_btn_{dest['id']}_{i}_{j}"
                        if st.button("🔍 View Destination", key=button_key, use_container_width=True):
                            st.session_state.selected_destination = dest
                            st.session_state.current_page = "Destination"
                            st.query_params["page"] = "destination"
                            st.query_params["id"] = str(dest['id'])
                            st.rerun()
    else:
        st.info("No destinations with images yet. Images are being downloaded...")
    
    # Quick Action Buttons
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✈️ Plan New Trip", use_container_width=True):
            st.session_state.current_page = "chatbot"
            st.rerun()
    with col2:
        if st.button("❤️ View Wishlist", use_container_width=True):
            st.session_state.current_page = "Wishlist"
            st.rerun()
    with col3:
        if st.button("⭐ Write a Review", use_container_width=True):
            st.info("Select a destination from Trending Destinations to write a review!")

def render_all_destinations():
    """Show all destinations from all countries with images"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: white;">🌍 All Destinations</h1>
        <p style="color: white;">Explore every destination from all 195 countries with beautiful images</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search/filter bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search destinations", placeholder="Search by country, city, or place name...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Rating (High to Low)", "Budget (Low to High)", "Budget (High to Low)", "Name A-Z"])
    
    # Fetch all destinations with images
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM destinations WHERE image_paths IS NOT NULL AND image_paths != ''"
        params = []
        
        if search_term:
            query += " AND (country LIKE %s OR city LIKE %s OR place_name LIKE %s)"
            search_pattern = f"%{search_term}%"
            params = [search_pattern, search_pattern, search_pattern]
        
        if sort_by == "Rating (High to Low)":
            query += " ORDER BY avg_user_rating DESC"
        elif sort_by == "Budget (Low to High)":
            query += " ORDER BY budget_per_day_usd ASC"
        elif sort_by == "Budget (High to Low)":
            query += " ORDER BY budget_per_day_usd DESC"
        elif sort_by == "Name A-Z":
            query += " ORDER BY place_name ASC"
        
        cursor.execute(query, params)
        all_destinations = cursor.fetchall()
        cursor.close()
        conn.close()
    else:
        all_destinations = []
    
    st.markdown(f"### 📊 Found {len(all_destinations)} destinations with images")
    
    # Display destinations in grid (3 per row)
    if all_destinations:
        for i in range(0, len(all_destinations), 3):
            cols = st.columns(3)
            for j in range(3):
                idx = i + j
                if idx < len(all_destinations):
                    dest = all_destinations[idx]
                    with cols[j]:
                        # Display image
                        image_path = dest.get('image_paths', '')
                        if image_path:
                            first_image = image_path.split(',')[0].strip()
                            try:
                                st.image(first_image, use_container_width=True)
                            except:
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 150px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                                    <span style="font-size: 50px;">📍</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 150px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                                <span style="font-size: 50px;">📍</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown(f"**{dest['place_name']}**")
                        st.write(f"📍 {dest['city']}, {dest['country']}")
                        st.write(f"⭐ {dest['avg_user_rating'] or 'New'} ({dest['total_reviews'] or 0} reviews)")
                        st.write(f"💰 ${dest['budget_per_day_usd']}/day")
                        
                        # Updated button with new navigation
                        if st.button(f"🔍 View Details", key=f"all_dest_btn_{dest['id']}_{idx}", use_container_width=True):
                            st.session_state.selected_destination = dest
                            st.session_state.current_page = "Destination"
                            st.query_params["page"] = "destination"
                            st.query_params["id"] = str(dest['id'])
                            st.rerun()
                        st.markdown("---")
    else:
        st.info("No destinations with images found yet. Images are still downloading...")

# ========== chatbot PAGE ==========
def render_ai_assistant():
    """Chat interface with Llama 3.2 with image support"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: white;">🤖 JouneyBloom</h1>
        <p style="color: white;">Your personal travel planner. Ask me anything about your next adventure!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick prompt buttons
    st.markdown("### Quick Prompts")
    quick_prompts = [
        "3-day beach trip to Thailand for a couple",
        "Budget family vacation to Japan",
        "Romantic weekend in Paris under $1000",
        "Backpacking Europe for 2 weeks",
        "Best time to visit Bali"
    ]
    
    cols = st.columns(5)
    for idx, prompt in enumerate(quick_prompts):
        with cols[idx]:
            if st.button(f"📌 {prompt[:20]}...", key=f"quick_{idx}"):
                st.session_state.quick_prompt = prompt
                st.rerun()
    
    # Chat interface
    st.markdown("---")
    st.markdown("### 💬 Chat with AI Travel Planner")
    
    # Check for quick prompt
    if hasattr(st.session_state, 'quick_prompt') and st.session_state.quick_prompt:
        user_input = st.session_state.quick_prompt
        st.session_state.quick_prompt = None
    else:
        user_input = st.chat_input("Ask me to plan your trip...")
    
    # Display chat history with images
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(message["content"])
                
                # Show images if available in message
                if "images" in message and message["images"]:
                    cols = st.columns(min(len(message["images"]), 3))
                    for idx, img_path in enumerate(message["images"][:3]):
                        with cols[idx % 3]:
                            if img_path and img_path != "📍":
                                try:
                                    if img_path.startswith("http"):
                                        st.image(img_path, use_container_width=True)
                                    else:
                                        st.image(img_path, use_container_width=True)
                                except:
                                    st.markdown(f"<div style='text-align: center; font-size: 40px;'>{img_path}</div>", unsafe_allow_html=True)
    
    # Process new input
    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("✈️ Planning your dream trip... (fetching images too!)"):
                response = generate_tour_plan(user_input)
                st.write(response)
                
                # Extract destinations and fetch images
                images_found = []
                
                # Common destinations list
                destinations_dict = {
                    "tokyo": "Tokyo, Japan",
                    "paris": "Paris, France", 
                    "bali": "Bali, Indonesia",
                    "phuket": "Phuket, Thailand",
                    "bangkok": "Bangkok, Thailand",
                    "goa": "Goa, India",
                    "maldives": "Maldives",
                    "singapore": "Singapore",
                    "dubai": "Dubai, UAE",
                    "new york": "New York, USA",
                    "london": "London, UK",
                    "rome": "Rome, Italy",
                    "venice": "Venice, Italy",
                    "barcelona": "Barcelona, Spain",
                    "sydney": "Sydney, Australia",
                    "kyoto": "Kyoto, Japan",
                    "osaka": "Osaka, Japan",
                    "seoul": "Seoul, South Korea",
                    "beach": "Beach Destination",
                    "mountain": "Mountain Destination"
                }
                
                # Check for destinations in user input or response
                response_lower = (user_input + " " + response).lower()
                
                for dest_key, dest_name in destinations_dict.items():
                    if dest_key in response_lower:
                        # Try to get image from database
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor(dictionary=True)
                            cursor.execute(
                                "SELECT image_paths, place_name, country FROM destinations WHERE LOWER(place_name) LIKE %s OR LOWER(city) LIKE %s LIMIT 3",
                                (f"%{dest_key}%", f"%{dest_key}%")
                            )
                            results = cursor.fetchall()
                            cursor.close()
                            conn.close()
                            
                            for result in results:
                                if result.get('image_paths'):
                                    paths = result['image_paths'].split(',')
                                    for path in paths[:2]:  # Max 2 images per destination
                                        if path and path.strip():
                                            images_found.append(path.strip())
                            
                            if images_found:
                                break
                
                # If no images found in DB, try Unsplash directly
                if not images_found:
                    # Try to get image from Unsplash API
                    unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
                    if unsplash_key and 'dest_key' in locals():
                        try:
                            import requests
                            url = f"https://api.unsplash.com/search/photos?query={dest_key}+travel&per_page=2&client_id={unsplash_key}"
                            response_img = requests.get(url)
                            if response_img.status_code == 200:
                                data = response_img.json()
                                for photo in data.get('results', []):
                                    images_found.append(photo.get('urls', {}).get('small'))
                        except:
                            pass
                
                # Show emoji placeholders if no real images
                if not images_found:
                    # Show relevant emoji based on destination type
                    if any(word in response_lower for word in ['beach', 'island', 'sea']):
                        images_found = ["🏖️", "🌊"]
                    elif any(word in response_lower for word in ['mountain', 'hike', 'hill']):
                        images_found = ["🏔️", "⛰️"]
                    elif any(word in response_lower for word in ['temple', 'shrine', 'history']):
                        images_found = ["🕌", "🏯"]
                    elif any(word in response_lower for word in ['city', 'urban', 'downtown']):
                        images_found = ["🌆", "🏙️"]
                    else:
                        images_found = ["✈️", "🌍"]
                
                # Display images
                if images_found:
                    st.markdown("### 📸 Destination Images")
                    cols = st.columns(min(len(images_found), 3))
                    for idx, img in enumerate(images_found[:3]):
                        with cols[idx]:
                            if img.startswith("http") or img.endswith(".jpg") or img.endswith(".png"):
                                try:
                                    st.image(img, use_container_width=True)
                                except:
                                    st.markdown(f"<div style='text-align: center; font-size: 60px;'>{img}</div>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<div style='text-align: center; font-size: 60px;'>{img}</div>", unsafe_allow_html=True)
                
                # Add option to save itinerary
                if st.button("💾 Save This Itinerary", key="save_itinerary_ai"):
                    save_itinerary(
                        st.session_state.user_id,
                        f"Trip to {user_input[:50]}",
                        response,
                        [],
                        500
                    )
                    st.success("✅ Itinerary saved to 'My Trips'!")
                    send_notification(st.session_state.user_id, "Itinerary Saved", "Your trip plan has been saved successfully!")
        
        # Store message with images in history
        st.session_state.chat_history.append({
            "role": "assistant", 
            "content": response,
            "images": images_found if 'images_found' in locals() else []
        })
        st.rerun()

# ========== MY TRIPS PAGE ==========
def render_my_trips():
    """Display saved itineraries"""
    st.markdown("### 📋 My Saved Trips")
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM saved_itineraries WHERE user_id = %s ORDER BY created_at DESC", (st.session_state.user_id,))
        trips = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if trips:
            for trip in trips:
                with st.expander(f"✈️ {trip['itinerary_name']} - {trip['created_at'].strftime('%B %d, %Y')}"):
                    st.write(trip['itinerary_text'])
                    if trip['total_budget']:
                        st.info(f"💰 Estimated Budget: ${trip['total_budget']}")
                    if st.button(f"🗑️ Delete", key=f"delete_{trip['id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM saved_itineraries WHERE id = %s", (trip['id'],))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success("Trip deleted!")
                        st.rerun()
        else:
            st.info("No saved trips yet. Go to chatbot to plan your first trip!")

# ========== WISHLIST PAGE ==========
def render_wishlist():
    """Display user's wishlist with working remove button"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: white;">❤️ My Wishlist</h1>
        <p style="color: white;">Your saved destinations - plan your dream trips!</p>
    </div>
    """, unsafe_allow_html=True)
    
    wishlist_items = get_user_wishlist(st.session_state.user_id)
    
    if wishlist_items:
        st.write(f"📊 You have **{len(wishlist_items)}** destinations in your wishlist")
        st.markdown("---")
        
        for idx, item in enumerate(wishlist_items):
            # Create a container for each wishlist item
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    # Show image if available
                    image_path = item.get('image_paths', '')
                    if image_path:
                        first_image = image_path.split(',')[0].strip()
                        try:
                            st.image(first_image, use_container_width=True)
                        except:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 80px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                                <span style="font-size: 40px;">📍</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 80px; border-radius: 10px; display: flex; align-items: center; justify-content: center;">
                            <span style="font-size: 40px;">📍</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{item['place_name']}**")
                    st.write(f"📍 {item['city']}, {item['country']}")
                    st.write(f"⭐ Rating: {item.get('avg_user_rating', 'Not rated yet')}")
                    st.write(f"💰 Budget: ${item.get('budget_per_day_usd', 'N/A')}/day")
                    
                    # Show status and priority if available
                    if item.get('status'):
                        status_color = {
                            'planned': '🟢',
                            'completed': '✅', 
                            'wishlist': '🔵'
                        }.get(item['status'], '🔵')
                        st.write(f"{status_color} Status: {item['status'].capitalize()}")
                    
                    if item.get('personal_notes'):
                        st.caption(f"📝 Notes: {item['personal_notes']}")
                
                with col3:
                    # View button
                    if st.button("🔍 View", key=f"wishlist_view_{item.get('wishlist_id', item.get('id'))}_{idx}"):
                        st.session_state.selected_destination = item
                        st.session_state.current_page = "Destination"
                        st.rerun()
                    
                    # Remove button with proper deletion
                    remove_key = f"wishlist_remove_{item.get('wishlist_id', item.get('id'))}_{idx}"
                    if st.button("🗑️ Remove", key=remove_key):
                        try:
                            conn = get_db_connection()
                            if conn:
                                cursor = conn.cursor()
                                # Delete from wishlist using either wishlist_id or id
                                wishlist_id = item.get('wishlist_id', item.get('id'))
                                cursor.execute(
                                    "DELETE FROM wishlist WHERE id = %s AND user_id = %s",
                                    (wishlist_id, st.session_state.user_id)
                                )
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success(f"✅ Removed {item['place_name']} from wishlist!")
                                st.rerun()
                            else:
                                st.error("Database connection failed")
                        except Exception as e:
                            st.error(f"Error removing item: {e}")
                
                st.markdown("---")
    else:
        st.info("💡 Your wishlist is empty. Browse destinations and click '❤️ Add to Wishlist' to save your favorites!")
        
        # Show some recommendations
        st.markdown("### 🔥 Recommended Destinations")
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM destinations 
                WHERE image_paths IS NOT NULL AND image_paths != '' 
                ORDER BY avg_user_rating DESC 
                LIMIT 3
            """)
            recommendations = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if recommendations:
                cols = st.columns(3)
                for idx, dest in enumerate(recommendations):
                    with cols[idx]:
                        st.markdown(f"**{dest['place_name']}**")
                        st.write(f"{dest['city']}, {dest['country']}")
                        if st.button(f"View {dest['place_name']}", key=f"rec_{dest['id']}"):
                            st.session_state.selected_destination = dest
                            st.session_state.current_page = "Destination"
                            st.rerun()

# ========== GROUPS PAGE ==========
def render_groups():
    """Group trip planning interface"""
    st.markdown("### 👥 Group Trip Planning")
    
    tab1, tab2 = st.tabs(["My Groups", "Create New Group"])
    
    with tab1:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT g.*, d.place_name 
                FROM groups g 
                LEFT JOIN destinations d ON g.destination_id = d.id
                JOIN group_members gm ON g.id = gm.group_id 
                WHERE gm.user_id = %s
            """, (st.session_state.user_id,))
            groups = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if groups:
                for group in groups:
                    with st.expander(f"👥 {group['group_name']}"):
                        st.write(f"📍 Destination: {group['place_name'] or 'TBD'}")
                        st.write(f"📅 Dates: {group['start_date']} to {group['end_date']}")
                        st.write(f"💰 Budget: ${group['total_budget'] or 'Not set'}")
                        if st.button("View Group", key=f"group_{group['id']}"):
                            st.session_state.selected_group = group
                            st.info("Group details view coming soon!")
            else:
                st.info("You're not in any groups yet. Create one or accept an invite!")
    
    with tab2:
        with st.form("create_group"):
            group_name = st.text_input("Group Name")
            destination = st.selectbox("Destination (optional)", ["Not selected"] + [d['place_name'] for d in get_destinations(limit=50)])
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            budget = st.number_input("Total Budget ($)", min_value=0)
            
            if st.form_submit_button("Create Group"):
                if group_name:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO groups (group_name, created_by, start_date, end_date, total_budget) VALUES (%s, %s, %s, %s, %s)",
                        (group_name, st.session_state.user_id, start_date, end_date, budget)
                    )
                    group_id = cursor.lastrowid
                    cursor.execute(
                        "INSERT INTO group_members (group_id, user_id, role) VALUES (%s, %s, 'admin')",
                        (group_id, st.session_state.user_id)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success(f"✅ Group '{group_name}' created successfully!")
                    st.rerun()

# ========== CHAT PAGE ==========
def render_chat():
    """User chat interface"""
    st.markdown("### 💬 Messages")
    
    # Simple chat interface - can be expanded for production
    st.info("💡 Chat with fellow travelers! This feature is ready for expansion.")
    
    # Get list of users to chat with
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username FROM users WHERE id != %s LIMIT 20", (st.session_state.user_id,))
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if users:
            selected_user = st.selectbox("Select user to chat with", users, format_func=lambda x: x['username'])
            
            if selected_user:
                st.markdown(f"#### 💬 Chat with {selected_user['username']}")
                
                # Message input
                message = st.text_area("Type your message")
                if st.button("Send Message") and message:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO chat_messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)",
                        (st.session_state.user_id, selected_user['id'], message)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    send_notification(selected_user['id'], "New Message", f"{st.session_state.username} sent you a message", "chat")
                    st.success("Message sent!")
                    st.rerun()

# ========== EXPENSES PAGE ==========
def render_expenses():
    """Travel expense tracker"""
    st.markdown("### 💰 Travel Expense Tracker")
    
    tab1, tab2 = st.tabs(["Add Expense", "View Expenses"])
    
    with tab1:
        with st.form("add_expense"):
            category = st.selectbox("Category", ["Accommodation", "Food", "Transport", "Activities", "Shopping", "Other"])
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
            description = st.text_input("Description")
            destination = st.selectbox("Destination (optional)", ["Not specified"] + [d['place_name'] for d in get_destinations(limit=50)])
            
            if st.form_submit_button("Add Expense"):
                dest_id = None
                if destination != "Not specified":
                    dest = next((d for d in get_destinations() if d['place_name'] == destination), None)
                    dest_id = dest['id'] if dest else None
                
                add_expense(st.session_state.user_id, category, amount, description, dest_id)
                st.success("✅ Expense added!")
                send_notification(st.session_state.user_id, "Expense Added", f"Added ${amount} for {category}")
                st.rerun()
    
    with tab2:
        expenses = get_user_expenses(st.session_state.user_id)
        
        if expenses:
            # Summary chart
            expense_df = pd.DataFrame(expenses)
            category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
            
            fig = px.pie(category_totals, values='amount', names='category', title='Spending by Category')
            st.plotly_chart(fig, use_container_width=True)
            
            # Expense list
            st.markdown("#### Recent Expenses")
            for exp in expenses[:20]:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{exp['description'] or exp['category']}**")
                with col2:
                    st.write(f"${exp['amount']}")
                with col3:
                    st.write(exp['category'])
                with col4:
                    st.write(exp['expense_date'].strftime('%Y-%m-%d') if exp['expense_date'] else '')
            st.caption(f"Total: ${expense_df['amount'].sum():.2f}")
        else:
            st.info("No expenses recorded yet. Start tracking your travel spending!")

# ========== PROFILE PAGE ==========
def render_profile():
    """User profile and settings"""
    st.markdown("### 👤 My Profile")
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (st.session_state.user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%; width: 150px; height: 150px; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                    <span style="font-size: 60px;">👤</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"## {user['username']}")
                st.write(f"📧 {user['email']}")
                st.write(f"📅 Joined: {user['created_at'].strftime('%B %d, %Y')}")
                st.write(f"🕐 Last seen: {user['last_seen'].strftime('%Y-%m-%d %H:%M') if user['last_seen'] else 'Just now'}")
            
            st.markdown("---")
            st.markdown("### 📊 My Activity")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Destinations Visited", "0", "Start exploring!")
            with col2:
                st.metric("Reviews Written", f"{get_reviews(st.session_state.user_id) if False else '0'}")
            with col3:
                st.metric("Trips Planned", "0")

# ========== DESTINATION PAGE ==========
def render_destination(destination):
    """Single destination view with reviews"""
    
    # Clear any query params that might interfere
    if destination is None:
        st.error("Destination not found")
        st.session_state.current_page = "Home"
        st.rerun()
        return
    
    st.markdown(f"## {destination['place_name']}")
    st.markdown(f"### 📍 {destination['city']}, {destination['country']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; padding: 20px;">
            <h3 style="color: white;">💰 Budget</h3>
            <p style="color: white; font-size: 24px;">${destination['budget_per_day_usd']}/day</p>
            <h3 style="color: white;">⭐ Rating</h3>
            <p style="color: white; font-size: 24px;">{destination['avg_user_rating'] or 'No ratings yet'}</p>
            <h3 style="color: white;">🌤️ Best Season</h3>
            <p style="color: white;">{destination['best_season']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Weather widget
        weather = get_weather(destination['city'], destination['country'])
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); border-radius: 20px; padding: 20px;">
            <h3 style="color: white;">🌤️ Current Weather</h3>
            <p style="color: white; font-size: 18px;">{weather}</p>
            <h3 style="color: white;">🎯 Top Attractions</h3>
            <p style="color: white;">{destination['top_attractions']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Write a review section
    st.markdown("---")
    st.markdown("### ✍️ Write a Review")
    
    with st.form("review_form"):
        rating = st.slider("Your Rating", 1, 5, 5)
        review_text = st.text_area("Your Review")
        
        if st.form_submit_button("Submit Review"):
            add_review(st.session_state.user_id, destination['id'], rating, review_text)
            st.success("✅ Review submitted!")
            st.rerun()
    
    # Display reviews
    st.markdown("### 📝 User Reviews")
    reviews = get_reviews(destination['id'])
    
    if reviews:
        for review in reviews:
            st.markdown(f"""
            <div style="background: #f0f2f6; border-radius: 10px; padding: 15px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <strong>👤 {review['username']}</strong>
                    <span>⭐ {review['rating']}/5</span>
                </div>
                <p>{review['review_text']}</p>
                <small>📅 {review['created_at'].strftime('%B %d, %Y')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No reviews yet. Be the first to review this destination!")
    
    # Add to wishlist button
    if st.button("❤️ Add to Wishlist", key="add_wishlist"):
        add_to_wishlist(st.session_state.user_id, destination['id'])
        st.success("Added to wishlist!")

# ========== NOTIFICATIONS PAGE ==========
def render_notifications():
    """Display user notifications"""
    st.markdown("### 🔔 Notifications")
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC", (st.session_state.user_id,))
        notifs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if notifs:
            for notif in notifs:
                with st.container():
                    st.markdown(f"""
                    <div style="background: {'#e3f2fd' if not notif['is_read'] else '#f5f5f5'}; border-radius: 10px; padding: 15px; margin: 5px 0;">
                        <strong>{notif['title']}</strong>
                        <p>{notif['message']}</p>
                        <small>{notif['created_at'].strftime('%B %d, %Y %H:%M')}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if not notif['is_read']:
                        if st.button("Mark as Read", key=f"mark_{notif['id']}"):
                            mark_notification_read(notif['id'])
                            st.rerun()
        else:
            st.info("No notifications")

# ========== MAIN APP ==========
def main():
    """Main application entry point"""
    
    # Initialize session state variables
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'selected_destination' not in st.session_state:
        st.session_state.selected_destination = None
    if 'quick_prompt' not in st.session_state:
        st.session_state.quick_prompt = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Handle query parameters for navigation
    query_params = st.query_params
    
    # Check for page navigation
    if "page" in query_params:
        page = query_params["page"]
        if page in ["Home", "chatbot", "My Trips", "Wishlist", "Expenses", "All Destinations", "Notifications", "Destination"]:
            st.session_state.current_page = page
            
            # Handle destination page with ID
            if page == "Destination" and "id" in query_params:
                try:
                    dest_id = int(query_params["id"])
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute("SELECT * FROM destinations WHERE id = %s", (dest_id,))
                        dest = cursor.fetchone()
                        cursor.close()
                        conn.close()
                        if dest:
                            st.session_state.selected_destination = dest
                except:
                    pass
            
            # Clear query params after processing
            st.query_params.clear()
            st.rerun()
    
    # Handle logout
    if "logout" in query_params:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.session_state.selected_destination = None
        st.session_state.current_page = "Home"
        st.query_params.clear()
        st.rerun()
    
    # Initialize database
    init_database()
    
    # Login/Registration screen
    if not st.session_state.logged_in:
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="font-size: 4rem;">✈️ JourneyBloom </h1>
            
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username or Email")
                password = st.text_input("Password", type="password")
                
                if st.form_submit_button("Login"):
                    user = check_login(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user['username']
                        st.session_state.user_id = user['id']
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Register"):
                    if new_password != confirm_password:
                        st.error("Passwords don't match")
                    elif register_user(new_username, new_email, new_password):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username or email already exists")
    
    else:
        # Render navbar for logged-in users
        render_navbar()
        
        # Page routing
        if st.session_state.current_page == "Home":
            render_homepage()
        elif st.session_state.current_page == "chatbot":
            render_ai_assistant()
        elif st.session_state.current_page == "My Trips":
            render_my_trips()
        elif st.session_state.current_page == "Wishlist":
            render_wishlist()
        elif st.session_state.current_page == "Expenses":
            render_expenses()
        elif st.session_state.current_page == "All Destinations":
            render_all_destinations()
        elif st.session_state.current_page == "Destination" and st.session_state.selected_destination is not None:
            render_destination(st.session_state.selected_destination)
        elif st.session_state.current_page == "Notifications":
            render_notifications()
        else:
            render_homepage()

if __name__ == "__main__":
    main()