"""
Check database contents
"""

import sqlite3
import hashlib

def check_database():
    conn = sqlite3.connect("notary_training.db")
    
    # Check users table
    print("=== USERS TABLE ===")
    users = conn.execute("SELECT * FROM users").fetchall()
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[5]}, Active: {user[8]}")
    
    # Check lessons count
    print("\n=== LESSONS TABLE ===")
    lesson_count = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    print(f"Total lessons: {lesson_count}")
    
    # Test password hash
    print("\n=== PASSWORD VERIFICATION ===")
    test_password = "admin123"
    test_hash = hashlib.sha256(test_password.encode()).hexdigest()
    
    stored_hash = conn.execute("SELECT password_hash FROM users WHERE username = 'admin'").fetchone()
    if stored_hash:
        print(f"Test password: {test_password}")
        print(f"Test hash: {test_hash}")
        print(f"Stored hash: {stored_hash[0]}")
        print(f"Match: {test_hash == stored_hash[0]}")
    
    conn.close()

if __name__ == "__main__":
    check_database()