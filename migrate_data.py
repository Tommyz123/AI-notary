"""
Data migration script for Notary Training System
Migrates existing CSV and JSON data to the new SQLite database.
"""

import os
import json
from database import db
from auth import AuthManager


def migrate_lessons():
    """Migrate lessons from CSV to database."""
    print("🔄 Migrating lessons from CSV...")
    
    if os.path.exists("lessons.csv"):
        success = db.migrate_lessons_from_csv("lessons.csv")
        if success:
            print("✅ Lessons migrated successfully!")
        else:
            print("❌ Failed to migrate lessons.")
    else:
        print("⚠️ lessons.csv not found.")


def create_default_user():
    """Create a default admin user for testing."""
    print("🔄 Creating default admin user...")
    
    username = "admin"
    password = "admin123"
    email = "admin@notary-training.com"
    full_name = "System Administrator"
    
    user_id = db.create_user(username, password, email, full_name)
    
    if user_id:
        # Update user role to admin
        with db.get_connection() as conn:
            conn.execute("UPDATE users SET role = 'admin' WHERE id = ?", (user_id,))
            conn.commit()
        print(f"✅ Default admin user created (ID: {user_id})")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        return user_id
    else:
        print("⚠️ Default user already exists or creation failed.")
        # Try to get existing user
        with db.get_connection() as conn:
            result = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            return result['id'] if result else None


def migrate_progress_data(user_id):
    """Migrate existing progress and completed data."""
    print("🔄 Migrating user progress data...")
    
    migrated_items = 0
    
    # Migrate completed.json
    if os.path.exists("completed.json"):
        try:
            with open("completed.json", "r") as f:
                completed_lessons = json.load(f)
                
            for lesson_no in completed_lessons:
                db.update_user_progress(user_id, lesson_no, is_completed=True)
                migrated_items += 1
                
            print(f"✅ Migrated {len(completed_lessons)} completed lessons")
        except Exception as e:
            print(f"❌ Error migrating completed.json: {e}")
    
    # Migrate progress.json
    if os.path.exists("progress.json"):
        try:
            with open("progress.json", "r") as f:
                progress_data = json.load(f)
                
            current_index = progress_data.get("current_index", 0)
            
            # We need to map index to lesson number
            # For now, let's assume lesson numbers are sequential starting from "001"
            if current_index > 0:
                current_lesson = f"{current_index:03d}"
                db.update_user_progress(user_id, current_lesson, current_index=current_index)
                print(f"✅ Set current lesson to {current_lesson} (index {current_index})")
                
        except Exception as e:
            print(f"❌ Error migrating progress.json: {e}")
    
    return migrated_items


def set_system_settings():
    """Set initial system settings."""
    print("🔄 Setting system configuration...")
    
    settings = [
        ("app_version", "2.0.0", "Current application version"),
        ("migration_date", "2024-01-01", "Date of database migration"),
        ("default_detail_level", "Standard", "Default explanation detail level"),
        ("quiz_pass_rate", "0.8", "Required pass rate for final test"),
        ("session_timeout_hours", "24", "User session timeout in hours"),
    ]
    
    for key, value, description in settings:
        db.set_system_setting(key, value, description)
    
    print(f"✅ Set {len(settings)} system settings")


def main():
    """Run the complete migration process."""
    print("🚀 Starting data migration for Notary Training System...")
    print("=" * 60)
    
    # Initialize database
    print("🔄 Initializing database...")
    db.init_database()
    print("✅ Database initialized!")
    
    # Migrate lessons
    migrate_lessons()
    
    # Create default user
    user_id = create_default_user()
    
    # Migrate progress data if we have a user
    if user_id:
        migrate_progress_data(user_id)
    
    # Set system settings
    set_system_settings()
    
    print("=" * 60)
    print("🎉 Migration completed successfully!")
    print()
    print("Next steps:")
    print("1. Run the application: streamlit run app.py")
    print("2. Login with username 'admin' and password 'admin123'")
    print("3. Change the admin password after first login")
    print("4. Create additional user accounts as needed")


if __name__ == "__main__":
    main()