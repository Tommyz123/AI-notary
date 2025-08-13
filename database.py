"""
Database module for Notary Training System
Provides SQLite database operations for user management, progress tracking, and analytics.
"""

import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import json
import os

DB_PATH = "notary_training.db"

class DatabaseManager:
    """Manages all database operations for the Notary Training System."""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with all required tables."""
        with self.get_connection() as conn:
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
            
            # Sessions table for authentication
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
            
            # Lessons table (migrated from CSV)
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
            
            # User progress tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    lesson_no TEXT NOT NULL,
                    current_index INTEGER DEFAULT 0,
                    is_completed BOOLEAN DEFAULT 0,
                    completion_date TIMESTAMP,
                    time_spent INTEGER DEFAULT 0,  -- in seconds
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no),
                    UNIQUE(user_id, lesson_no)
                )
            """)
            
            # Quiz attempts and results
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    lesson_no TEXT NOT NULL,
                    attempt_number INTEGER DEFAULT 1,
                    score INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    time_taken INTEGER,  -- in seconds
                    answers TEXT,  -- JSON string of user answers
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no)
                )
            """)
            
            # Final test results
            conn.execute("""
                CREATE TABLE IF NOT EXISTS final_test_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    time_taken INTEGER,
                    passed BOOLEAN DEFAULT 0,
                    answers TEXT,  -- JSON string of user answers
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # User questions and AI responses
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
            
            # System settings and configuration
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for better performance."""
        with self.get_connection() as conn:
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
    
    # User Management Methods
    def create_user(self, username: str, password: str, email: str = None, full_name: str = None) -> Optional[int]:
        """Create a new user account."""
        password_hash = self._hash_password(password)
        
        with self.get_connection() as conn:
            try:
                cursor = conn.execute("""
                    INSERT INTO users (username, password_hash, email, full_name)
                    VALUES (?, ?, ?, ?)
                """, (username, password_hash, email, full_name))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None  # User already exists
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info if successful."""
        password_hash = self._hash_password(password)
        
        with self.get_connection() as conn:
            user = conn.execute("""
                SELECT id, username, email, full_name, role, is_active
                FROM users 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            """, (username, password_hash)).fetchone()
            
            if user:
                # Update last login
                conn.execute("""
                    UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                """, (user['id'],))
                conn.commit()
                
                return dict(user)
        return None
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None) -> str:
        """Create a new user session."""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=24)  # 24 hour sessions
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO sessions (id, user_id, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, expires_at, ip_address, user_agent))
            conn.commit()
        
        return session_id
    
    def get_user_by_session(self, session_id: str) -> Optional[Dict]:
        """Get user info from session ID."""
        with self.get_connection() as conn:
            result = conn.execute("""
                SELECT u.id, u.username, u.email, u.full_name, u.role
                FROM users u
                JOIN sessions s ON u.id = s.user_id
                WHERE s.id = ? AND s.expires_at > CURRENT_TIMESTAMP AND u.is_active = 1
            """, (session_id,)).fetchone()
            
            return dict(result) if result else None
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from database."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP")
            conn.commit()
    
    # Progress Tracking Methods
    def update_user_progress(self, user_id: int, lesson_no: str, current_index: int = 0, 
                           is_completed: bool = False, time_spent: int = 0):
        """Update user progress for a lesson."""
        with self.get_connection() as conn:
            completion_date = datetime.now().isoformat() if is_completed else None
            
            conn.execute("""
                INSERT OR REPLACE INTO user_progress 
                (user_id, lesson_no, current_index, is_completed, completion_date, time_spent, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, lesson_no, current_index, is_completed, completion_date, time_spent))
            conn.commit()
    
    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """Get all progress data for a user."""
        with self.get_connection() as conn:
            progress = conn.execute("""
                SELECT lesson_no, current_index, is_completed, completion_date, time_spent
                FROM user_progress 
                WHERE user_id = ?
            """, (user_id,)).fetchall()
            
            return {row['lesson_no']: dict(row) for row in progress}
    
    def get_completed_lessons(self, user_id: int) -> List[str]:
        """Get list of completed lesson numbers for a user."""
        with self.get_connection() as conn:
            results = conn.execute("""
                SELECT lesson_no FROM user_progress 
                WHERE user_id = ? AND is_completed = 1
            """, (user_id,)).fetchall()
            
            return [row['lesson_no'] for row in results]
    
    # Quiz and Assessment Methods
    def save_quiz_attempt(self, user_id: int, lesson_no: str, score: int, 
                         total_questions: int, time_taken: int, answers: Dict):
        """Save a quiz attempt."""
        with self.get_connection() as conn:
            # Get attempt number
            attempt_num = conn.execute("""
                SELECT COALESCE(MAX(attempt_number), 0) + 1 
                FROM quiz_attempts 
                WHERE user_id = ? AND lesson_no = ?
            """, (user_id, lesson_no)).fetchone()[0]
            
            conn.execute("""
                INSERT INTO quiz_attempts 
                (user_id, lesson_no, attempt_number, score, total_questions, time_taken, answers)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, lesson_no, attempt_num, score, total_questions, time_taken, json.dumps(answers)))
            conn.commit()
    
    def save_final_test_attempt(self, user_id: int, score: int, total_questions: int, 
                               time_taken: int, answers: Dict):
        """Save a final test attempt."""
        passed = score >= (total_questions * 0.8)  # 80% pass rate
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO final_test_attempts 
                (user_id, score, total_questions, time_taken, passed, answers)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, score, total_questions, time_taken, passed, json.dumps(answers)))
            conn.commit()
    
    def save_qa_interaction(self, user_id: int, lesson_no: str, question: str, 
                           answer: str, detail_level: str):
        """Save a Q&A interaction."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO qa_history (user_id, lesson_no, question, answer, detail_level)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, lesson_no, question, answer, detail_level))
            conn.commit()
    
    # Analytics Methods
    def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a user."""
        with self.get_connection() as conn:
            # Basic progress stats
            progress_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_lessons_attempted,
                    SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_lessons,
                    SUM(time_spent) as total_time_spent
                FROM user_progress 
                WHERE user_id = ?
            """, (user_id,)).fetchone()
            
            # Quiz performance
            quiz_stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_quizzes_taken,
                    AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_score,
                    MAX(CAST(score AS FLOAT) / total_questions * 100) as best_score
                FROM quiz_attempts 
                WHERE user_id = ?
            """, (user_id,)).fetchone()
            
            # Final test results
            final_test = conn.execute("""
                SELECT score, total_questions, passed, created_at
                FROM final_test_attempts 
                WHERE user_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,)).fetchone()
            
            return {
                'progress': dict(progress_stats) if progress_stats else {},
                'quiz_performance': dict(quiz_stats) if quiz_stats else {},
                'final_test': dict(final_test) if final_test else None
            }
    
    # Data Migration Methods
    def migrate_lessons_from_csv(self, csv_file_path: str):
        """Migrate lesson data from CSV to database."""
        import pandas as pd
        
        if not os.path.exists(csv_file_path):
            return False
        
        try:
            df = pd.read_csv(csv_file_path, encoding="ISO-8859-1")
            
            with self.get_connection() as conn:
                for _, row in df.iterrows():
                    conn.execute("""
                        INSERT OR REPLACE INTO lessons (lesson_no, title, content)
                        VALUES (?, ?, ?)
                    """, (str(row['No']), row['Title'], row['Content']))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error migrating lessons: {e}")
            return False
    
    def migrate_json_progress(self, user_id: int, progress_file: str, completed_file: str):
        """Migrate existing JSON progress data to database."""
        try:
            # Migrate progress.json
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    progress_data = json.load(f)
                    current_index = progress_data.get('current_index', 0)
                    # This would need lesson number mapping
            
            # Migrate completed.json
            if os.path.exists(completed_file):
                with open(completed_file, 'r') as f:
                    completed_lessons = json.load(f)
                    for lesson_no in completed_lessons:
                        self.update_user_progress(user_id, lesson_no, is_completed=True)
            
            return True
        except Exception as e:
            print(f"Error migrating JSON data: {e}")
            return False
    
    # Utility Methods
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_system_setting(self, key: str, default_value: str = None) -> str:
        """Get a system setting value."""
        with self.get_connection() as conn:
            result = conn.execute("""
                SELECT value FROM system_settings WHERE key = ?
            """, (key,)).fetchone()
            
            return result['value'] if result else default_value
    
    def set_system_setting(self, key: str, value: str, description: str = None):
        """Set a system setting value."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO system_settings (key, value, description, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, description))
            conn.commit()

# Global database instance
db = DatabaseManager()