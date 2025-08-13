"""
Admin panel for Notary Training System
Provides administrative functions for user management and system configuration.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from database import db
from auth import AuthManager
from analytics import show_admin_analytics


def show_admin_panel():
    """Display the admin panel."""
    user = AuthManager.get_current_user()
    if not user or user['role'] != 'admin':
        st.error("🚫 Admin access required.")
        return
    
    st.title("🛠️ Admin Panel")
    st.markdown(f"Welcome, **{user['full_name'] or user['username']}**")
    
    # Admin tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users", "📊 Analytics", "📚 Content", "⚙️ Settings"])
    
    with tab1:
        show_user_management()
    
    with tab2:
        show_admin_analytics()
    
    with tab3:
        show_content_management()
    
    with tab4:
        show_system_settings()


def show_user_management():
    """User management interface."""
    st.subheader("👥 User Management")
    
    # User statistics
    with db.get_connection() as conn:
        user_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users,
                SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admin_users,
                SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as student_users
            FROM users
        """).fetchone()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", user_stats['total_users'])
    with col2:
        st.metric("Active Users", user_stats['active_users'])
    with col3:
        st.metric("Administrators", user_stats['admin_users'])
    with col4:
        st.metric("Students", user_stats['student_users'])
    
    # Create new user
    st.subheader("➕ Create New User")
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Username")
            new_email = st.text_input("Email (optional)")
        with col2:
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["student", "admin"])
        
        new_full_name = st.text_input("Full Name (optional)")
        
        if st.form_submit_button("Create User"):
            if new_username and new_password:
                user_id = db.create_user(new_username, new_password, new_email, new_full_name)
                if user_id:
                    # Set role
                    with db.get_connection() as conn:
                        conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
                        conn.commit()
                    st.success(f"✅ User '{new_username}' created successfully!")
                else:
                    st.error("❌ Failed to create user. Username may already exist.")
            else:
                st.error("❌ Username and password are required.")
    
    # User list and management
    st.subheader("👥 User List")
    
    with db.get_connection() as conn:
        users = conn.execute("""
            SELECT id, username, email, full_name, role, is_active, 
                   created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """).fetchall()
    
    if users:
        users_df = pd.DataFrame([dict(user) for user in users])
        
        # User filter
        filter_role = st.selectbox("Filter by Role", ["All", "admin", "student"])
        filter_status = st.selectbox("Filter by Status", ["All", "Active", "Inactive"])
        
        filtered_df = users_df.copy()
        if filter_role != "All":
            filtered_df = filtered_df[filtered_df['role'] == filter_role]
        if filter_status == "Active":
            filtered_df = filtered_df[filtered_df['is_active'] == 1]
        elif filter_status == "Inactive":
            filtered_df = filtered_df[filtered_df['is_active'] == 0]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # User actions
        st.subheader("🔧 User Actions")
        selected_username = st.selectbox("Select User", filtered_df['username'].tolist())
        
        if selected_username:
            selected_user = filtered_df[filtered_df['username'] == selected_username].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Reset Password"):
                    new_pass = f"temp{selected_user['id']}123"
                    # Hash and update password
                    import hashlib
                    password_hash = hashlib.sha256(new_pass.encode()).hexdigest()
                    
                    with db.get_connection() as conn:
                        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", 
                                   (password_hash, selected_user['id']))
                        conn.commit()
                    
                    st.success(f"Password reset to: {new_pass}")
            
            with col2:
                current_status = "Active" if selected_user['is_active'] else "Inactive"
                new_status = "Inactive" if selected_user['is_active'] else "Active"
                
                if st.button(f"Toggle to {new_status}"):
                    new_is_active = 0 if selected_user['is_active'] else 1
                    
                    with db.get_connection() as conn:
                        conn.execute("UPDATE users SET is_active = ? WHERE id = ?", 
                                   (new_is_active, selected_user['id']))
                        conn.commit()
                    
                    st.success(f"User status changed to {new_status}")
                    st.rerun()
            
            with col3:
                new_role = "admin" if selected_user['role'] == "student" else "student"
                if st.button(f"Change to {new_role}"):
                    with db.get_connection() as conn:
                        conn.execute("UPDATE users SET role = ? WHERE id = ?", 
                                   (new_role, selected_user['id']))
                        conn.commit()
                    
                    st.success(f"User role changed to {new_role}")
                    st.rerun()


def show_content_management():
    """Content management interface."""
    st.subheader("📚 Content Management")
    
    # Lesson statistics
    with db.get_connection() as conn:
        lesson_count = conn.execute("SELECT COUNT(*) as count FROM lessons").fetchone()
        
        recent_activity = conn.execute("""
            SELECT COUNT(*) as recent_quizzes
            FROM quiz_attempts
            WHERE created_at >= datetime('now', '-7 days')
        """).fetchone()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Lessons", lesson_count['count'])
    with col2:
        st.metric("Quiz Attempts (7d)", recent_activity['recent_quizzes'])
    
    # Lesson management
    st.subheader("📝 Lessons")
    
    with db.get_connection() as conn:
        lessons = conn.execute("""
            SELECT lesson_no, title, 
                   LENGTH(content) as content_length,
                   created_at, updated_at
            FROM lessons
            ORDER BY CAST(lesson_no AS INTEGER)
        """).fetchall()
    
    if lessons:
        lessons_df = pd.DataFrame([dict(lesson) for lesson in lessons])
        st.dataframe(lessons_df, use_container_width=True)
        
        # Add new lesson
        st.subheader("➕ Add New Lesson")
        with st.form("add_lesson_form"):
            col1, col2 = st.columns(2)
            with col1:
                lesson_no = st.text_input("Lesson Number (e.g., 001)")
            with col2:
                lesson_title = st.text_input("Lesson Title")
            
            lesson_content = st.text_area("Lesson Content", height=200)
            
            if st.form_submit_button("Add Lesson"):
                if lesson_no and lesson_title and lesson_content:
                    try:
                        with db.get_connection() as conn:
                            conn.execute("""
                                INSERT INTO lessons (lesson_no, title, content)
                                VALUES (?, ?, ?)
                            """, (lesson_no, lesson_title, lesson_content))
                            conn.commit()
                        st.success("✅ Lesson added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding lesson: {e}")
                else:
                    st.error("❌ All fields are required.")
    
    # Data migration tools
    st.subheader("🔄 Data Migration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Import from CSV"):
            success = db.migrate_lessons_from_csv("lessons.csv")
            if success:
                st.success("✅ Lessons imported from CSV successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to import lessons from CSV.")
    
    with col2:
        if st.button("🗑️ Clear All Lessons"):
            if st.checkbox("I understand this will delete all lesson data"):
                with db.get_connection() as conn:
                    conn.execute("DELETE FROM lessons")
                    conn.commit()
                st.success("✅ All lessons cleared.")
                st.rerun()


def show_system_settings():
    """System settings interface."""
    st.subheader("⚙️ System Settings")
    
    # Current settings
    with db.get_connection() as conn:
        settings = conn.execute("""
            SELECT key, value, description, updated_at
            FROM system_settings
            ORDER BY key
        """).fetchall()
    
    if settings:
        st.subheader("Current Settings")
        settings_df = pd.DataFrame([dict(setting) for setting in settings])
        st.dataframe(settings_df, use_container_width=True)
    
    # Update settings
    st.subheader("Update Settings")
    
    with st.form("settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            setting_key = st.text_input("Setting Key")
            setting_value = st.text_input("Setting Value")
        
        with col2:
            setting_description = st.text_area("Description", height=100)
        
        if st.form_submit_button("Update Setting"):
            if setting_key and setting_value:
                db.set_system_setting(setting_key, setting_value, setting_description)
                st.success(f"✅ Setting '{setting_key}' updated successfully!")
                st.rerun()
            else:
                st.error("❌ Key and value are required.")
    
    # System information
    st.subheader("📊 System Information")
    
    with db.get_connection() as conn:
        # Database size and statistics
        db_stats = conn.execute("""
            SELECT 
                (SELECT COUNT(*) FROM users) as total_users,
                (SELECT COUNT(*) FROM lessons) as total_lessons,
                (SELECT COUNT(*) FROM quiz_attempts) as total_quiz_attempts,
                (SELECT COUNT(*) FROM qa_history) as total_qa_interactions,
                (SELECT COUNT(*) FROM sessions) as active_sessions
        """).fetchone()
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.metric("Database Users", db_stats['total_users'])
        st.metric("Total Lessons", db_stats['total_lessons'])
        st.metric("Quiz Attempts", db_stats['total_quiz_attempts'])
    
    with info_col2:
        st.metric("Q&A Interactions", db_stats['total_qa_interactions'])
        st.metric("Active Sessions", db_stats['active_sessions'])
    
    # Database maintenance
    st.subheader("🔧 Database Maintenance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Cleanup Expired Sessions"):
            db.cleanup_expired_sessions()
            st.success("✅ Expired sessions cleaned up!")
    
    with col2:
        if st.button("📈 Rebuild Indexes"):
            with db.get_connection() as conn:
                conn.execute("ANALYZE")
                conn.commit()
            st.success("✅ Database indexes rebuilt!")
    
    with col3:
        if st.button("💾 Backup Database"):
            import shutil
            import os
            backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db.db_path, backup_path)
            st.success(f"✅ Database backed up to {backup_path}")


if __name__ == "__main__":
    show_admin_panel()