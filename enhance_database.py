"""
Database Enhancement Script
Adds advanced features to the notary training database including:
- Audit logging
- Enhanced indexes
- Data validation triggers
- Statistics tables
"""

import sqlite3
from datetime import datetime

DB_PATH = "notary_training.db"

def add_audit_logging():
    """Add comprehensive audit logging table."""
    conn = sqlite3.connect(DB_PATH)

    # Audit log table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action_type TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id INTEGER,
            old_values TEXT,
            new_values TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Create index for audit log queries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_user_action
        ON audit_log (user_id, action_type, created_at DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_table_record
        ON audit_log (table_name, record_id, created_at DESC)
    """)

    conn.commit()
    conn.close()
    print("✅ Audit logging table created")

def add_enhanced_indexes():
    """Add additional indexes for performance optimization."""
    conn = sqlite3.connect(DB_PATH)

    indexes = [
        # User-related indexes
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email) WHERE email IS NOT NULL",
        "CREATE INDEX IF NOT EXISTS idx_users_role_active ON users (role, is_active)",
        "CREATE INDEX IF NOT EXISTS idx_users_created ON users (created_at DESC)",

        # Progress tracking indexes
        "CREATE INDEX IF NOT EXISTS idx_progress_completed ON user_progress (is_completed, completion_date)",
        "CREATE INDEX IF NOT EXISTS idx_progress_time_spent ON user_progress (time_spent DESC)",

        # Quiz performance indexes
        "CREATE INDEX IF NOT EXISTS idx_quiz_score ON quiz_attempts (score, total_questions)",
        "CREATE INDEX IF NOT EXISTS idx_quiz_date ON quiz_attempts (created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_quiz_user_date ON quiz_attempts (user_id, created_at DESC)",

        # Final test indexes
        "CREATE INDEX IF NOT EXISTS idx_final_test_passed ON final_test_attempts (passed, created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_final_test_score ON final_test_attempts (score DESC)",

        # Q&A history indexes
        "CREATE INDEX IF NOT EXISTS idx_qa_date ON qa_history (created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_qa_detail_level ON qa_history (detail_level, created_at DESC)",

        # Lesson indexes
        "CREATE INDEX IF NOT EXISTS idx_lessons_updated ON lessons (updated_at DESC)",
    ]

    for index_sql in indexes:
        try:
            conn.execute(index_sql)
        except sqlite3.Error as e:
            print(f"Warning: {e}")

    conn.commit()
    conn.close()
    print("✅ Enhanced indexes created")

def add_statistics_tables():
    """Add tables for caching statistics and analytics."""
    conn = sqlite3.connect(DB_PATH)

    # Daily statistics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date DATE UNIQUE NOT NULL,
            total_users INTEGER DEFAULT 0,
            active_users INTEGER DEFAULT 0,
            new_registrations INTEGER DEFAULT 0,
            lessons_completed INTEGER DEFAULT 0,
            quizzes_taken INTEGER DEFAULT 0,
            avg_quiz_score REAL DEFAULT 0,
            final_tests_taken INTEGER DEFAULT 0,
            final_tests_passed INTEGER DEFAULT 0,
            total_questions_asked INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User performance summary
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_performance_summary (
            user_id INTEGER PRIMARY KEY,
            total_lessons_completed INTEGER DEFAULT 0,
            total_time_spent INTEGER DEFAULT 0,
            total_quizzes_taken INTEGER DEFAULT 0,
            avg_quiz_score REAL DEFAULT 0,
            best_quiz_score REAL DEFAULT 0,
            total_questions_asked INTEGER DEFAULT 0,
            final_test_passed BOOLEAN DEFAULT 0,
            final_test_score INTEGER DEFAULT 0,
            last_activity_date TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Lesson analytics
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lesson_analytics (
            lesson_no TEXT PRIMARY KEY,
            total_views INTEGER DEFAULT 0,
            total_completions INTEGER DEFAULT 0,
            avg_completion_time INTEGER DEFAULT 0,
            avg_quiz_score REAL DEFAULT 0,
            total_questions_asked INTEGER DEFAULT 0,
            difficulty_rating REAL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Statistics tables created")

def add_validation_triggers():
    """Add triggers for data validation and automatic updates."""
    conn = sqlite3.connect(DB_PATH)

    # Trigger to update user_performance_summary when progress is updated
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS update_performance_on_progress
        AFTER INSERT ON user_progress
        BEGIN
            INSERT OR REPLACE INTO user_performance_summary
            (user_id, total_lessons_completed, total_time_spent, last_activity_date, updated_at)
            SELECT
                NEW.user_id,
                (SELECT COUNT(*) FROM user_progress WHERE user_id = NEW.user_id AND is_completed = 1),
                (SELECT SUM(time_spent) FROM user_progress WHERE user_id = NEW.user_id),
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP;
        END;
    """)

    # Trigger to update lesson analytics when lesson is completed
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS update_lesson_analytics_on_completion
        AFTER UPDATE ON user_progress
        WHEN NEW.is_completed = 1 AND OLD.is_completed = 0
        BEGIN
            INSERT OR IGNORE INTO lesson_analytics (lesson_no) VALUES (NEW.lesson_no);
            UPDATE lesson_analytics
            SET
                total_completions = total_completions + 1,
                avg_completion_time = (
                    SELECT AVG(time_spent)
                    FROM user_progress
                    WHERE lesson_no = NEW.lesson_no AND is_completed = 1
                ),
                updated_at = CURRENT_TIMESTAMP
            WHERE lesson_no = NEW.lesson_no;
        END;
    """)

    # Trigger to update performance summary when quiz is taken
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS update_performance_on_quiz
        AFTER INSERT ON quiz_attempts
        BEGIN
            INSERT OR IGNORE INTO user_performance_summary (user_id) VALUES (NEW.user_id);
            UPDATE user_performance_summary
            SET
                total_quizzes_taken = (
                    SELECT COUNT(*) FROM quiz_attempts WHERE user_id = NEW.user_id
                ),
                avg_quiz_score = (
                    SELECT AVG(CAST(score AS FLOAT) / total_questions * 100)
                    FROM quiz_attempts WHERE user_id = NEW.user_id
                ),
                best_quiz_score = (
                    SELECT MAX(CAST(score AS FLOAT) / total_questions * 100)
                    FROM quiz_attempts WHERE user_id = NEW.user_id
                ),
                last_activity_date = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = NEW.user_id;

            -- Update lesson analytics
            INSERT OR IGNORE INTO lesson_analytics (lesson_no) VALUES (NEW.lesson_no);
            UPDATE lesson_analytics
            SET
                avg_quiz_score = (
                    SELECT AVG(CAST(score AS FLOAT) / total_questions * 100)
                    FROM quiz_attempts WHERE lesson_no = NEW.lesson_no
                ),
                updated_at = CURRENT_TIMESTAMP
            WHERE lesson_no = NEW.lesson_no;
        END;
    """)

    # Trigger to clean up expired sessions automatically
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS cleanup_expired_sessions
        AFTER INSERT ON sessions
        BEGIN
            DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP;
        END;
    """)

    conn.commit()
    conn.close()
    print("✅ Validation triggers created")

def add_user_preferences_table():
    """Add table for user preferences and settings."""
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INTEGER PRIMARY KEY,
            theme TEXT DEFAULT 'light',
            language TEXT DEFAULT 'en',
            notifications_enabled BOOLEAN DEFAULT 1,
            email_notifications BOOLEAN DEFAULT 1,
            quiz_difficulty_preference TEXT DEFAULT 'medium',
            detail_level_preference TEXT DEFAULT 'medium',
            lessons_per_page INTEGER DEFAULT 10,
            auto_save_progress BOOLEAN DEFAULT 1,
            show_hints BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ User preferences table created")

def add_bookmarks_and_notes():
    """Add tables for user bookmarks and notes."""
    conn = sqlite3.connect(DB_PATH)

    # Bookmarks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_no TEXT NOT NULL,
            content_index INTEGER DEFAULT 0,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no),
            UNIQUE(user_id, lesson_no, content_index)
        )
    """)

    # Notes table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_no TEXT NOT NULL,
            note_text TEXT NOT NULL,
            is_private BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no)
        )
    """)

    # Indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_bookmarks_user_lesson
        ON user_bookmarks (user_id, lesson_no)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_user_lesson
        ON user_notes (user_id, lesson_no, created_at DESC)
    """)

    conn.commit()
    conn.close()
    print("✅ Bookmarks and notes tables created")

def add_achievements_system():
    """Add gamification with achievements and badges."""
    conn = sqlite3.connect(DB_PATH)

    # Achievements definitions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            icon TEXT,
            category TEXT NOT NULL,
            points INTEGER DEFAULT 0,
            requirement_type TEXT NOT NULL,
            requirement_value TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User achievements
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id INTEGER NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (achievement_id) REFERENCES achievements (id),
            UNIQUE(user_id, achievement_id)
        )
    """)

    # Leaderboard
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            user_id INTEGER PRIMARY KEY,
            total_points INTEGER DEFAULT 0,
            total_achievements INTEGER DEFAULT 0,
            rank INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Achievements system created")

def initialize_achievements():
    """Initialize default achievements."""
    conn = sqlite3.connect(DB_PATH)

    achievements = [
        ("First Steps", "Complete your first lesson", "🎯", "progress", 10, "lessons_completed", "1"),
        ("Scholar", "Complete 10 lessons", "📚", "progress", 50, "lessons_completed", "10"),
        ("Expert", "Complete all lessons", "🏆", "progress", 200, "lessons_completed", "all"),
        ("Quiz Master", "Score 100% on a quiz", "⭐", "performance", 30, "perfect_quiz", "1"),
        ("Consistent Learner", "Complete lessons 7 days in a row", "📅", "engagement", 75, "streak_days", "7"),
        ("Quick Learner", "Complete a lesson in under 5 minutes", "⚡", "speed", 20, "lesson_time", "300"),
        ("Curious Mind", "Ask 50 questions", "❓", "engagement", 40, "questions_asked", "50"),
        ("Test Taker", "Pass the final test", "🎓", "achievement", 100, "final_test_passed", "1"),
        ("Perfect Score", "Score 100% on final test", "💯", "achievement", 150, "final_test_score", "100"),
    ]

    for achievement in achievements:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO achievements
                (name, description, icon, category, points, requirement_type, requirement_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, achievement)
        except sqlite3.Error as e:
            print(f"Warning: {e}")

    conn.commit()
    conn.close()
    print("✅ Default achievements initialized")

def add_lesson_dependencies():
    """Add table to track lesson prerequisites and dependencies."""
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS lesson_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_no TEXT NOT NULL,
            prerequisite_lesson_no TEXT NOT NULL,
            is_required BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_no) REFERENCES lessons (lesson_no),
            FOREIGN KEY (prerequisite_lesson_no) REFERENCES lessons (lesson_no),
            UNIQUE(lesson_no, prerequisite_lesson_no)
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_lesson_deps
        ON lesson_dependencies (lesson_no, prerequisite_lesson_no)
    """)

    conn.commit()
    conn.close()
    print("✅ Lesson dependencies table created")

def optimize_database():
    """Run database optimization commands."""
    conn = sqlite3.connect(DB_PATH)

    # Analyze tables for query optimizer
    conn.execute("ANALYZE")

    # Vacuum to reclaim unused space and defragment
    conn.execute("VACUUM")

    # Enable Write-Ahead Logging for better concurrent access
    conn.execute("PRAGMA journal_mode=WAL")

    # Set synchronous to NORMAL for better performance
    conn.execute("PRAGMA synchronous=NORMAL")

    # Increase cache size
    conn.execute("PRAGMA cache_size=-64000")  # 64MB cache

    conn.commit()
    conn.close()
    print("✅ Database optimized")

def create_views():
    """Create useful database views for common queries."""
    conn = sqlite3.connect(DB_PATH)

    # User progress overview
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_user_progress_overview AS
        SELECT
            u.id,
            u.username,
            u.full_name,
            COUNT(DISTINCT up.lesson_no) as lessons_started,
            SUM(CASE WHEN up.is_completed = 1 THEN 1 ELSE 0 END) as lessons_completed,
            SUM(up.time_spent) as total_time_spent,
            COUNT(DISTINCT qa.lesson_no) as lessons_attempted,
            (SELECT COUNT(*) FROM lessons) as total_lessons,
            CAST(SUM(CASE WHEN up.is_completed = 1 THEN 1 ELSE 0 END) AS FLOAT) /
                (SELECT COUNT(*) FROM lessons) * 100 as completion_percentage
        FROM users u
        LEFT JOIN user_progress up ON u.id = up.user_id
        LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
        WHERE u.is_active = 1
        GROUP BY u.id, u.username, u.full_name
    """)

    # Quiz performance view
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_quiz_performance AS
        SELECT
            u.id as user_id,
            u.username,
            qa.lesson_no,
            l.title as lesson_title,
            COUNT(*) as attempts,
            AVG(CAST(qa.score AS FLOAT) / qa.total_questions * 100) as avg_score,
            MAX(CAST(qa.score AS FLOAT) / qa.total_questions * 100) as best_score,
            MIN(qa.created_at) as first_attempt,
            MAX(qa.created_at) as last_attempt
        FROM users u
        JOIN quiz_attempts qa ON u.id = qa.user_id
        JOIN lessons l ON qa.lesson_no = l.lesson_no
        GROUP BY u.id, u.username, qa.lesson_no, l.title
    """)

    # Active users view (users who have activity in last 7 days)
    conn.execute("""
        CREATE VIEW IF NOT EXISTS v_active_users AS
        SELECT DISTINCT
            u.id,
            u.username,
            u.email,
            u.last_login,
            MAX(COALESCE(up.updated_at, qa.created_at, qah.created_at)) as last_activity
        FROM users u
        LEFT JOIN user_progress up ON u.id = up.user_id
        LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
        LEFT JOIN qa_history qah ON u.id = qah.user_id
        WHERE u.is_active = 1
        AND (
            up.updated_at >= datetime('now', '-7 days')
            OR qa.created_at >= datetime('now', '-7 days')
            OR qah.created_at >= datetime('now', '-7 days')
        )
        GROUP BY u.id, u.username, u.email, u.last_login
    """)

    conn.commit()
    conn.close()
    print("✅ Database views created")

def main():
    print("🚀 Enhancing Notary Training Database...")
    print("=" * 60)

    try:
        add_audit_logging()
        add_enhanced_indexes()
        add_statistics_tables()
        add_validation_triggers()
        add_user_preferences_table()
        add_bookmarks_and_notes()
        add_achievements_system()
        initialize_achievements()
        add_lesson_dependencies()
        create_views()
        optimize_database()

        print("=" * 60)
        print("🎉 Database enhancement completed successfully!")
        print()
        print("New features added:")
        print("  ✓ Audit logging for security and compliance")
        print("  ✓ Enhanced indexes for better performance")
        print("  ✓ Statistics and analytics tables")
        print("  ✓ Automatic data validation triggers")
        print("  ✓ User preferences system")
        print("  ✓ Bookmarks and notes functionality")
        print("  ✓ Achievements and gamification")
        print("  ✓ Lesson dependencies tracking")
        print("  ✓ Useful database views")
        print("  ✓ Database optimization (WAL mode, vacuum, analyze)")

    except Exception as e:
        print(f"❌ Error during enhancement: {e}")
        raise

if __name__ == "__main__":
    main()
