# Database configuration for XAMPP MySQL
import mysql.connector
from mysql.connector import Error
import streamlit as st

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # XAMPP default is empty
    'database': 'tourism_app'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database with tables if not exists"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS tourism_app")
        cursor.execute("USE tourism_app")
        
        # Execute SQL setup file
        with open('setup_db.sql', 'r') as f:
            sql_commands = f.read().split(';')
            for command in sql_commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                    except:
                        pass
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    return False