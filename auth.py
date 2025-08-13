"""
Authentication module for Notary Training System
Handles user login, registration, session management, and access control.
"""

import streamlit as st
from typing import Optional, Dict, Any
from database import db
import re


class AuthManager:
    """Manages user authentication and session handling."""
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Validate username format."""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        # Allow alphanumeric characters, underscores, and hyphens
        return re.match(r'^[a-zA-Z0-9_-]+$', username) is not None
    
    @staticmethod
    def is_valid_password(password: str) -> bool:
        """Validate password strength."""
        if not password or len(password) < 6:
            return False
        # Require at least one letter and one number
        has_letter = re.search(r'[a-zA-Z]', password)
        has_number = re.search(r'[0-9]', password)
        return has_letter and has_number
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return True  # Email is optional
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def login_user(username: str, password: str) -> bool:
        """Authenticate user and create session."""
        if not username or not password:
            return False
        
        user = db.authenticate_user(username, password)
        if user:
            # Create session
            session_id = db.create_session(user['id'])
            
            # Store in Streamlit session
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = user['id']
            st.session_state['username'] = user['username']
            st.session_state['user_role'] = user['role']
            st.session_state['session_id'] = session_id
            st.session_state['full_name'] = user.get('full_name', username)
            
            return True
        return False
    
    @staticmethod
    def register_user(username: str, password: str, email: str = None, full_name: str = None) -> tuple[bool, str]:
        """Register a new user."""
        # Validate inputs
        if not AuthManager.is_valid_username(username):
            return False, "Username must be 3-50 characters long and contain only letters, numbers, underscores, and hyphens."
        
        if not AuthManager.is_valid_password(password):
            return False, "Password must be at least 6 characters long and contain at least one letter and one number."
        
        if email and not AuthManager.is_valid_email(email):
            return False, "Please enter a valid email address."
        
        # Create user
        user_id = db.create_user(username, password, email, full_name)
        if user_id:
            return True, "Account created successfully! Please log in."
        else:
            return False, "Username already exists. Please choose a different username."
    
    @staticmethod
    def logout_user():
        """Log out current user and clear session."""
        # Clear Streamlit session
        for key in ['authenticated', 'user_id', 'username', 'user_role', 'session_id', 'full_name']:
            if key in st.session_state:
                del st.session_state[key]
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is currently authenticated."""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get current authenticated user info."""
        if not AuthManager.is_authenticated():
            return None
        
        return {
            'id': st.session_state.get('user_id'),
            'username': st.session_state.get('username'),
            'role': st.session_state.get('user_role'),
            'full_name': st.session_state.get('full_name'),
            'session_id': st.session_state.get('session_id')
        }
    
    @staticmethod
    def require_auth():
        """Decorator/function to require authentication."""
        if not AuthManager.is_authenticated():
            AuthManager.show_login_page()
            st.stop()
    
    @staticmethod
    def show_login_page():
        """Display the login/registration page."""
        st.title("🔐 Notary Training System")
        st.markdown("Please log in to access your personalized learning experience.")
        
        # Login/Register tabs
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            AuthManager._show_login_form()
        
        with tab2:
            AuthManager._show_register_form()
    
    @staticmethod
    def _show_login_form():
        """Show the login form."""
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("Username", max_chars=50)
            password = st.text_input("Password", type="password", max_chars=100)
            
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                elif AuthManager.login_user(username, password):
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
    
    @staticmethod
    def _show_register_form():
        """Show the registration form."""
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            username = st.text_input("Username*", max_chars=50, 
                                    help="3-50 characters, letters, numbers, underscores, and hyphens only")
            password = st.text_input("Password*", type="password", max_chars=100,
                                   help="Minimum 6 characters with at least one letter and one number")
            password_confirm = st.text_input("Confirm Password*", type="password", max_chars=100)
            email = st.text_input("Email (optional)", max_chars=100)
            full_name = st.text_input("Full Name (optional)", max_chars=100)
            
            submitted = st.form_submit_button("Create Account")
            
            if submitted:
                if not username or not password:
                    st.error("Username and password are required.")
                elif password != password_confirm:
                    st.error("Passwords do not match.")
                else:
                    success, message = AuthManager.register_user(username, password, email, full_name)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    @staticmethod
    def show_user_info():
        """Display current user information in sidebar."""
        if AuthManager.is_authenticated():
            user = AuthManager.get_current_user()
            with st.sidebar:
                st.markdown("---")
                st.markdown(f"👤 **{user['full_name'] or user['username']}**")
                st.markdown(f"📊 Role: {user['role'].title()}")
                
                if st.button("🚪 Logout"):
                    AuthManager.logout_user()
                    st.rerun()


# Utility functions for backward compatibility
def require_auth():
    """Convenience function to require authentication."""
    AuthManager.require_auth()

def get_current_user_id() -> Optional[int]:
    """Get current user ID or None if not authenticated."""
    user = AuthManager.get_current_user()
    return user['id'] if user else None

def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return AuthManager.is_authenticated()