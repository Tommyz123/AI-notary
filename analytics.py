"""
Analytics module for Notary Training System
Provides user progress visualization and learning analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import db
from auth import get_current_user_id, AuthManager


def show_analytics_page():
    """Display the analytics dashboard for the current user."""
    st.title("📊 Learning Analytics")
    
    user_id = 1  # Fixed user ID for single-user mode
    
    # Get user analytics data
    analytics_data = db.get_user_analytics(user_id)
    
    # Overview metrics
    st.subheader("📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    progress_data = analytics_data.get('progress', {})
    quiz_data = analytics_data.get('quiz_performance', {})
    
    with col1:
        st.metric(
            "Lessons Attempted", 
            progress_data.get('total_lessons_attempted', 0)
        )
    
    with col2:
        st.metric(
            "Lessons Completed", 
            progress_data.get('completed_lessons', 0)
        )
    
    with col3:
        avg_score = quiz_data.get('avg_score', 0)
        st.metric(
            "Average Quiz Score", 
            f"{avg_score:.1f}%" if avg_score else "N/A"
        )
    
    with col4:
        total_time = progress_data.get('total_time_spent', 0)
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        st.metric(
            "Study Time", 
            f"{hours}h {minutes}m"
        )
    
    # Progress visualization
    st.subheader("📚 Lesson Progress")
    
    with db.get_connection() as conn:
        # Get detailed progress data
        lesson_progress = conn.execute("""
            SELECT l.lesson_no, l.title, 
                   COALESCE(up.is_completed, 0) as completed,
                   COALESCE(up.time_spent, 0) as time_spent,
                   up.completion_date
            FROM lessons l
            LEFT JOIN user_progress up ON l.lesson_no = up.lesson_no AND up.user_id = ?
            ORDER BY CAST(l.lesson_no AS INTEGER)
        """, (user_id,)).fetchall()
        
        if lesson_progress:
            progress_df = pd.DataFrame([dict(row) for row in lesson_progress])
            
            # Progress bar chart
            fig = px.bar(
                progress_df, 
                x='lesson_no', 
                y='time_spent', 
                color='completed',
                title="Time Spent per Lesson",
                labels={'time_spent': 'Time (seconds)', 'lesson_no': 'Lesson'},
                color_discrete_map={0: '#ff6b6b', 1: '#51cf66'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Completion status
            completed_count = progress_df['completed'].sum()
            total_lessons = len(progress_df)
            completion_rate = (completed_count / total_lessons) * 100 if total_lessons > 0 else 0
            
            st.progress(completion_rate / 100)
            st.write(f"Overall Completion: {completed_count}/{total_lessons} lessons ({completion_rate:.1f}%)")
    
    # Quiz performance
    st.subheader("🧪 Quiz Performance")
    
    with db.get_connection() as conn:
        quiz_attempts = conn.execute("""
            SELECT qa.lesson_no, l.title, qa.score, qa.total_questions, 
                   qa.created_at, qa.attempt_number
            FROM quiz_attempts qa
            JOIN lessons l ON qa.lesson_no = l.lesson_no
            WHERE qa.user_id = ?
            ORDER BY qa.created_at DESC
        """, (user_id,)).fetchall()
        
        if quiz_attempts:
            quiz_df = pd.DataFrame([dict(row) for row in quiz_attempts])
            quiz_df['score_percentage'] = (quiz_df['score'] / quiz_df['total_questions']) * 100
            quiz_df['created_at'] = pd.to_datetime(quiz_df['created_at'])
            
            # Quiz scores over time
            fig = px.line(
                quiz_df, 
                x='created_at', 
                y='score_percentage',
                title="Quiz Scores Over Time",
                labels={'score_percentage': 'Score (%)', 'created_at': 'Date'}
            )
            fig.add_hline(y=80, line_dash="dash", line_color="green", 
                         annotation_text="Pass Threshold (80%)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Recent quiz attempts
            st.subheader("Recent Quiz Attempts")
            recent_quizzes = quiz_df.head(10)[['title', 'score', 'total_questions', 'score_percentage', 'created_at']]
            recent_quizzes['created_at'] = recent_quizzes['created_at'].dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(recent_quizzes, use_container_width=True)
        else:
            st.info("No quiz attempts yet. Complete some lesson quizzes to see your performance!")
    
    # Final test results
    final_test_data = analytics_data.get('final_test')
    if final_test_data:
        st.subheader("🏁 Final Test Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{final_test_data['score']}/{final_test_data['total_questions']}")
        with col2:
            percentage = (final_test_data['score'] / final_test_data['total_questions']) * 100
            st.metric("Percentage", f"{percentage:.1f}%")
        with col3:
            status = "✅ PASSED" if final_test_data['passed'] else "❌ FAILED"
            st.metric("Status", status)
        
        st.write(f"Completed on: {final_test_data['created_at']}")
    
    # Learning insights
    st.subheader("💡 Learning Insights")
    
    insights = []
    
    if progress_data.get('completed_lessons', 0) > 0:
        avg_time_per_lesson = progress_data.get('total_time_spent', 0) / progress_data['completed_lessons']
        insights.append(f"📖 You spend an average of {avg_time_per_lesson/60:.1f} minutes per lesson.")
    
    if quiz_data.get('avg_score', 0) > 0:
        if quiz_data['avg_score'] >= 90:
            insights.append("🌟 Excellent! Your quiz performance is outstanding.")
        elif quiz_data['avg_score'] >= 80:
            insights.append("👍 Good job! You're performing well on quizzes.")
        elif quiz_data['avg_score'] >= 70:
            insights.append("📚 Consider reviewing lessons more thoroughly before taking quizzes.")
        else:
            insights.append("⚠️ Quiz scores suggest you may need more study time per lesson.")
    
    completion_rate = (progress_data.get('completed_lessons', 0) / 
                      max(progress_data.get('total_lessons_attempted', 1), 1)) * 100
    
    if completion_rate == 100:
        insights.append("🎉 Congratulations! You've completed all attempted lessons.")
    elif completion_rate >= 80:
        insights.append("🚀 You're making great progress! Keep it up.")
    elif completion_rate >= 50:
        insights.append("📈 You're halfway there! Continue with your studies.")
    else:
        insights.append("🎯 Focus on completing the lessons you've started.")
    
    for insight in insights:
        st.info(insight)


def show_admin_analytics():
    """Display admin analytics dashboard."""
    user = AuthManager.get_current_user()
    if not user or user['role'] != 'admin':
        st.error("Admin access required.")
        return
    
    st.title("🛠️ Admin Analytics")
    
    # System overview
    st.subheader("📊 System Overview")
    
    with db.get_connection() as conn:
        # User stats
        user_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users,
                SUM(CASE WHEN last_login > datetime('now', '-7 days') THEN 1 ELSE 0 END) as recent_users
            FROM users
        """).fetchone()
        
        # Lesson stats
        lesson_stats = conn.execute("""
            SELECT COUNT(*) as total_lessons FROM lessons
        """).fetchone()
        
        # Quiz stats
        quiz_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_attempts,
                AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_score
            FROM quiz_attempts
        """).fetchone()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", user_stats['total_users'])
    with col2:
        st.metric("Active Users", user_stats['active_users'])
    with col3:
        st.metric("Recent Users (7d)", user_stats['recent_users'])
    with col4:
        st.metric("Total Lessons", lesson_stats['total_lessons'])
    
    # User activity over time
    st.subheader("📈 User Activity")
    
    with db.get_connection() as conn:
        activity_data = conn.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as registrations
            FROM users
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """).fetchall()
        
        if activity_data:
            activity_df = pd.DataFrame([dict(row) for row in activity_data])
            fig = px.line(activity_df, x='date', y='registrations', 
                         title="Daily User Registrations (Last 30 Days)")
            st.plotly_chart(fig, use_container_width=True)
    
    # Top performing users
    st.subheader("🏆 Top Performers")
    
    with db.get_connection() as conn:
        top_users = conn.execute("""
            SELECT u.username, u.full_name,
                   COUNT(DISTINCT up.lesson_no) as completed_lessons,
                   AVG(CAST(qa.score AS FLOAT) / qa.total_questions * 100) as avg_quiz_score
            FROM users u
            LEFT JOIN user_progress up ON u.id = up.user_id AND up.is_completed = 1
            LEFT JOIN quiz_attempts qa ON u.id = qa.user_id
            WHERE u.role = 'student'
            GROUP BY u.id, u.username, u.full_name
            HAVING completed_lessons > 0
            ORDER BY completed_lessons DESC, avg_quiz_score DESC
            LIMIT 10
        """).fetchall()
        
        if top_users:
            top_df = pd.DataFrame([dict(row) for row in top_users])
            st.dataframe(top_df, use_container_width=True)


if __name__ == "__main__":
    show_analytics_page()