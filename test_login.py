"""
Test login functionality without streamlit
"""

import sqlite3
import hashlib

def test_authentication():
    print("Testing authentication...")
    
    # Direct database test
    conn = sqlite3.connect("notary_training.db")
    conn.row_factory = sqlite3.Row  # This is important!
    
    username = "admin"
    password = "admin123"
    
    # Hash password the same way as in the code
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    print(f"Testing login for: {username}")
    print(f"Password: {password}")
    print(f"Password hash: {password_hash}")
    
    # Test query
    user = conn.execute("""
        SELECT id, username, email, full_name, role, is_active
        FROM users 
        WHERE username = ? AND password_hash = ? AND is_active = 1
    """, (username, password_hash)).fetchone()
    
    if user:
        print("✅ Authentication successful!")
        print(f"User ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Role: {user['role']}")
        print(f"Active: {user['is_active']}")
        
        # Test the database module
        print("\nTesting database module...")
        try:
            from database import db
            user_dict = db.authenticate_user(username, password)
            if user_dict:
                print("✅ Database module authentication successful!")
                print(f"Returned data: {user_dict}")
            else:
                print("❌ Database module authentication failed!")
        except Exception as e:
            print(f"❌ Database module error: {e}")
            
    else:
        print("❌ Authentication failed!")
        
        # Check if user exists
        existing_user = conn.execute("""
            SELECT username, password_hash, is_active FROM users WHERE username = ?
        """, (username,)).fetchone()
        
        if existing_user:
            print(f"User exists: {existing_user['username']}")
            print(f"Stored hash: {existing_user['password_hash']}")
            print(f"Expected hash: {password_hash}")
            print(f"Hash match: {existing_user['password_hash'] == password_hash}")
            print(f"Is active: {existing_user['is_active']}")
        else:
            print("User does not exist in database")
    
    conn.close()

if __name__ == "__main__":
    test_authentication()