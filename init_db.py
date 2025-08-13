"""
Simple database initialization script without external dependencies
"""

import sqlite3
import hashlib
import os

DB_PATH = "notary_training.db"

def init_database():
    """Initialize database with basic tables."""
    conn = sqlite3.connect(DB_PATH)
    
    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            full_name TEXT,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # Sessions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Lessons table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY,
            lesson_no TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # User progress
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_no TEXT NOT NULL,
            current_index INTEGER DEFAULT 0,
            is_completed BOOLEAN DEFAULT 0,
            completion_date TIMESTAMP,
            time_spent INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no),
            UNIQUE(user_id, lesson_no)
        )
    """)
    
    # Quiz attempts
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_no TEXT NOT NULL,
            attempt_number INTEGER DEFAULT 1,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            time_taken INTEGER,
            answers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no)
        )
    """)
    
    # Final test attempts
    conn.execute("""
        CREATE TABLE IF NOT EXISTS final_test_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            time_taken INTEGER,
            passed BOOLEAN DEFAULT 0,
            answers TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Q&A history
    conn.execute("""
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_no TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            detail_level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no)
        )
    """)
    
    # System settings
    conn.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions (expires_at)",
        "CREATE INDEX IF NOT EXISTS idx_progress_user_lesson ON user_progress (user_id, lesson_no)",
        "CREATE INDEX IF NOT EXISTS idx_quiz_user_lesson ON quiz_attempts (user_id, lesson_no)",
        "CREATE INDEX IF NOT EXISTS idx_qa_user_lesson ON qa_history (user_id, lesson_no)",
        "CREATE INDEX IF NOT EXISTS idx_final_test_user ON final_test_attempts (user_id)",
    ]
    
    for index_sql in indexes:
        conn.execute(index_sql)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def create_admin_user():
    """Create default admin user."""
    conn = sqlite3.connect(DB_PATH)
    
    username = "admin"
    password = "admin123"
    email = "admin@notary-training.com"
    full_name = "System Administrator"
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor = conn.execute("""
            INSERT INTO users (username, password_hash, email, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password_hash, email, full_name, "admin"))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   User ID: {user_id}")
        
    except sqlite3.IntegrityError:
        print("⚠️ Admin user already exists")
    
    conn.close()

def migrate_lessons_from_csv():
    """Import lessons from CSV if it exists."""
    if not os.path.exists("lessons.csv"):
        print("⚠️ lessons.csv not found")
        return
    
    try:
        import csv
        conn = sqlite3.connect(DB_PATH)
        
        with open("lessons.csv", "r", encoding="ISO-8859-1") as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO lessons (lesson_no, title, content)
                        VALUES (?, ?, ?)
                    """, (str(row['No']), row['Title'], row['Content']))
                    count += 1
                except Exception as e:
                    print(f"Error importing lesson {row.get('No', 'unknown')}: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ Imported {count} lessons from CSV")
        
    except Exception as e:
        print(f"❌ Error importing lessons: {e}")

def main():
    print("🚀 Initializing Notary Training System Database...")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Create admin user
    create_admin_user()
    
    # Import lessons
    migrate_lessons_from_csv()
    
    print("=" * 50)
    print("🎉 Setup completed!")
    print()
    print("You can now:")
    print("1. Run: streamlit run app.py")
    print("2. Login with username 'admin' and password 'admin123'")

if __name__ == "__main__":
    main()