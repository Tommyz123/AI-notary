"""
Extended Database Manager
Adds support for new database features including:
- Audit logging
- Achievements system
- User preferences
- Bookmarks and notes
- Statistics and analytics
"""

from database import DatabaseManager, DB_PATH
import json
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExtendedDatabaseManager(DatabaseManager):
    """Extended database manager with additional features."""

    # ===== AUDIT LOGGING =====

    def log_audit(self, user_id: Optional[int], action_type: str, table_name: str,
                  record_id: Optional[int] = None, old_values: Dict = None,
                  new_values: Dict = None, ip_address: str = None, user_agent: str = None):
        """Log an audit entry."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO audit_log
                (user_id, action_type, table_name, record_id, old_values, new_values, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, action_type, table_name, record_id,
                  json.dumps(old_values) if old_values else None,
                  json.dumps(new_values) if new_values else None,
                  ip_address, user_agent))
            conn.commit()

    def get_audit_log(self, user_id: Optional[int] = None, table_name: Optional[str] = None,
                     limit: int = 100) -> List[Dict]:
        """Retrieve audit log entries."""
        with self.get_connection() as conn:
            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            if table_name:
                query += " AND table_name = ?"
                params.append(table_name)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            results = conn.execute(query, params).fetchall()
            return [dict(row) for row in results]

    # ===== USER PREFERENCES =====

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """Get user preferences."""
        with self.get_connection() as conn:
            result = conn.execute("""
                SELECT * FROM user_preferences WHERE user_id = ?
            """, (user_id,)).fetchone()

            if result:
                return dict(result)
            else:
                # Create default preferences
                self.set_user_preferences(user_id, {})
                return self.get_user_preferences(user_id)

    def set_user_preferences(self, user_id: int, preferences: Dict[str, Any]):
        """Set or update user preferences."""
        with self.get_connection() as conn:
            # Get current preferences or defaults
            current = conn.execute("""
                SELECT * FROM user_preferences WHERE user_id = ?
            """, (user_id,)).fetchone()

            if current:
                # Update existing preferences
                update_fields = []
                values = []
                for key, value in preferences.items():
                    update_fields.append(f"{key} = ?")
                    values.append(value)

                if update_fields:
                    values.append(user_id)
                    conn.execute(f"""
                        UPDATE user_preferences
                        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, values)
            else:
                # Insert new preferences with defaults
                conn.execute("""
                    INSERT INTO user_preferences (user_id) VALUES (?)
                """, (user_id,))

                if preferences:
                    self.set_user_preferences(user_id, preferences)

            conn.commit()

    # ===== BOOKMARKS & NOTES =====

    def add_bookmark(self, user_id: int, lesson_no: str, content_index: int = 0, note: str = None):
        """Add a bookmark for a lesson."""
        with self.get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO user_bookmarks (user_id, lesson_no, content_index, note)
                    VALUES (?, ?, ?, ?)
                """, (user_id, lesson_no, content_index, note))
                conn.commit()
                return True
            except:
                return False

    def remove_bookmark(self, user_id: int, lesson_no: str, content_index: int = 0):
        """Remove a bookmark."""
        with self.get_connection() as conn:
            conn.execute("""
                DELETE FROM user_bookmarks
                WHERE user_id = ? AND lesson_no = ? AND content_index = ?
            """, (user_id, lesson_no, content_index))
            conn.commit()

    def get_user_bookmarks(self, user_id: int) -> List[Dict]:
        """Get all bookmarks for a user."""
        with self.get_connection() as conn:
            results = conn.execute("""
                SELECT b.*, l.title as lesson_title
                FROM user_bookmarks b
                JOIN lessons l ON b.lesson_no = l.lesson_no
                WHERE b.user_id = ?
                ORDER BY b.created_at DESC
            """, (user_id,)).fetchall()
            return [dict(row) for row in results]

    def add_note(self, user_id: int, lesson_no: str, note_text: str, is_private: bool = True):
        """Add a note for a lesson."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO user_notes (user_id, lesson_no, note_text, is_private)
                VALUES (?, ?, ?, ?)
            """, (user_id, lesson_no, note_text, is_private))
            conn.commit()

    def update_note(self, note_id: int, note_text: str):
        """Update a note."""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE user_notes
                SET note_text = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (note_text, note_id))
            conn.commit()

    def delete_note(self, note_id: int, user_id: int):
        """Delete a note (only if owned by user)."""
        with self.get_connection() as conn:
            conn.execute("""
                DELETE FROM user_notes WHERE id = ? AND user_id = ?
            """, (note_id, user_id))
            conn.commit()

    def get_user_notes(self, user_id: int, lesson_no: Optional[str] = None) -> List[Dict]:
        """Get notes for a user, optionally filtered by lesson."""
        with self.get_connection() as conn:
            if lesson_no:
                results = conn.execute("""
                    SELECT n.*, l.title as lesson_title
                    FROM user_notes n
                    JOIN lessons l ON n.lesson_no = l.lesson_no
                    WHERE n.user_id = ? AND n.lesson_no = ?
                    ORDER BY n.created_at DESC
                """, (user_id, lesson_no)).fetchall()
            else:
                results = conn.execute("""
                    SELECT n.*, l.title as lesson_title
                    FROM user_notes n
                    JOIN lessons l ON n.lesson_no = l.lesson_no
                    WHERE n.user_id = ?
                    ORDER BY n.created_at DESC
                """, (user_id,)).fetchall()

            return [dict(row) for row in results]

    # ===== ACHIEVEMENTS SYSTEM =====

    def award_achievement(self, user_id: int, achievement_id: int):
        """Award an achievement to a user."""
        with self.get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO user_achievements (user_id, achievement_id)
                    VALUES (?, ?)
                """, (user_id, achievement_id))

                # Update leaderboard
                points = conn.execute("""
                    SELECT points FROM achievements WHERE id = ?
                """, (achievement_id,)).fetchone()[0]

                conn.execute("""
                    INSERT INTO leaderboard (user_id, total_points, total_achievements)
                    VALUES (?, ?, 1)
                    ON CONFLICT(user_id) DO UPDATE SET
                        total_points = total_points + ?,
                        total_achievements = total_achievements + 1,
                        updated_at = CURRENT_TIMESTAMP
                """, (user_id, points, points))

                conn.commit()

                # Log audit
                self.log_audit(user_id, 'achievement_awarded', 'user_achievements',
                             achievement_id, None, {'achievement_id': achievement_id})

                return True
            except:
                return False

    def get_user_achievements(self, user_id: int) -> List[Dict]:
        """Get all achievements earned by a user."""
        with self.get_connection() as conn:
            results = conn.execute("""
                SELECT a.*, ua.earned_at
                FROM achievements a
                JOIN user_achievements ua ON a.id = ua.achievement_id
                WHERE ua.user_id = ?
                ORDER BY ua.earned_at DESC
            """, (user_id,)).fetchall()
            return [dict(row) for row in results]

    def get_available_achievements(self, user_id: int) -> List[Dict]:
        """Get achievements not yet earned by user."""
        with self.get_connection() as conn:
            results = conn.execute("""
                SELECT * FROM achievements
                WHERE is_active = 1
                AND id NOT IN (
                    SELECT achievement_id FROM user_achievements WHERE user_id = ?
                )
                ORDER BY category, points
            """, (user_id,)).fetchall()
            return [dict(row) for row in results]

    def check_and_award_achievements(self, user_id: int):
        """Check user progress and award any earned achievements."""
        achievements_awarded = []

        # Get user stats
        stats = self.get_user_analytics(user_id)
        progress_stats = stats.get('progress', {})
        quiz_stats = stats.get('quiz_performance', {})
        final_test = stats.get('final_test')

        # Get available achievements
        available = self.get_available_achievements(user_id)

        with self.get_connection() as conn:
            for achievement in available:
                earned = False
                req_type = achievement['requirement_type']
                req_value = achievement['requirement_value']

                if req_type == 'lessons_completed':
                    if req_value == 'all':
                        total_lessons = conn.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
                        if progress_stats.get('completed_lessons', 0) >= total_lessons:
                            earned = True
                    else:
                        if progress_stats.get('completed_lessons', 0) >= int(req_value):
                            earned = True

                elif req_type == 'perfect_quiz':
                    if quiz_stats.get('best_score', 0) >= 100:
                        earned = True

                elif req_type == 'questions_asked':
                    total_questions = conn.execute("""
                        SELECT COUNT(*) FROM qa_history WHERE user_id = ?
                    """, (user_id,)).fetchone()[0]
                    if total_questions >= int(req_value):
                        earned = True

                elif req_type == 'final_test_passed':
                    if final_test and final_test.get('passed'):
                        earned = True

                elif req_type == 'final_test_score':
                    if final_test:
                        score_pct = (final_test['score'] / final_test['total_questions']) * 100
                        if score_pct >= float(req_value):
                            earned = True

                if earned:
                    if self.award_achievement(user_id, achievement['id']):
                        achievements_awarded.append(achievement)

        return achievements_awarded

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users on leaderboard."""
        with self.get_connection() as conn:
            results = conn.execute("""
                SELECT
                    l.user_id,
                    u.username,
                    u.full_name,
                    l.total_points,
                    l.total_achievements,
                    ROW_NUMBER() OVER (ORDER BY l.total_points DESC) as rank
                FROM leaderboard l
                JOIN users u ON l.user_id = u.id
                WHERE u.is_active = 1
                ORDER BY l.total_points DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in results]

    # ===== STATISTICS & ANALYTICS =====

    def update_daily_statistics(self):
        """Update daily statistics (should be run once per day)."""
        with self.get_connection() as conn:
            today = datetime.now().date()

            # Count stats for today
            stats = {
                'total_users': conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1").fetchone()[0],
                'active_users': conn.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM user_progress
                    WHERE DATE(updated_at) = DATE('now')
                """).fetchone()[0],
                'new_registrations': conn.execute("""
                    SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')
                """).fetchone()[0],
                'lessons_completed': conn.execute("""
                    SELECT COUNT(*) FROM user_progress
                    WHERE DATE(completion_date) = DATE('now')
                """).fetchone()[0],
                'quizzes_taken': conn.execute("""
                    SELECT COUNT(*) FROM quiz_attempts WHERE DATE(created_at) = DATE('now')
                """).fetchone()[0],
                'final_tests_taken': conn.execute("""
                    SELECT COUNT(*) FROM final_test_attempts WHERE DATE(created_at) = DATE('now')
                """).fetchone()[0],
                'final_tests_passed': conn.execute("""
                    SELECT COUNT(*) FROM final_test_attempts
                    WHERE DATE(created_at) = DATE('now') AND passed = 1
                """).fetchone()[0],
                'total_questions_asked': conn.execute("""
                    SELECT COUNT(*) FROM qa_history WHERE DATE(created_at) = DATE('now')
                """).fetchone()[0],
            }

            # Calculate average quiz score for today
            avg_score = conn.execute("""
                SELECT AVG(CAST(score AS FLOAT) / total_questions * 100)
                FROM quiz_attempts WHERE DATE(created_at) = DATE('now')
            """).fetchone()[0] or 0

            stats['avg_quiz_score'] = avg_score

            # Insert or update daily stats
            conn.execute("""
                INSERT OR REPLACE INTO daily_statistics
                (stat_date, total_users, active_users, new_registrations, lessons_completed,
                 quizzes_taken, avg_quiz_score, final_tests_taken, final_tests_passed,
                 total_questions_asked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (today, stats['total_users'], stats['active_users'], stats['new_registrations'],
                  stats['lessons_completed'], stats['quizzes_taken'], stats['avg_quiz_score'],
                  stats['final_tests_taken'], stats['final_tests_passed'],
                  stats['total_questions_asked']))

            conn.commit()
            return stats

    def get_lesson_analytics(self, lesson_no: str) -> Dict[str, Any]:
        """Get analytics for a specific lesson."""
        with self.get_connection() as conn:
            analytics = conn.execute("""
                SELECT * FROM lesson_analytics WHERE lesson_no = ?
            """, (lesson_no,)).fetchone()

            if analytics:
                return dict(analytics)

            # Return empty analytics if not found
            return {
                'lesson_no': lesson_no,
                'total_views': 0,
                'total_completions': 0,
                'avg_completion_time': 0,
                'avg_quiz_score': 0,
                'total_questions_asked': 0,
                'difficulty_rating': 0
            }

    def get_system_analytics(self) -> Dict[str, Any]:
        """Get overall system analytics."""
        with self.get_connection() as conn:
            analytics = {
                'total_users': conn.execute("""
                    SELECT COUNT(*) FROM users WHERE is_active = 1
                """).fetchone()[0],

                'total_lessons': conn.execute("""
                    SELECT COUNT(*) FROM lessons
                """).fetchone()[0],

                'total_completions': conn.execute("""
                    SELECT COUNT(*) FROM user_progress WHERE is_completed = 1
                """).fetchone()[0],

                'total_quizzes_taken': conn.execute("""
                    SELECT COUNT(*) FROM quiz_attempts
                """).fetchone()[0],

                'avg_quiz_score': conn.execute("""
                    SELECT AVG(CAST(score AS FLOAT) / total_questions * 100)
                    FROM quiz_attempts
                """).fetchone()[0] or 0,

                'total_final_tests': conn.execute("""
                    SELECT COUNT(*) FROM final_test_attempts
                """).fetchone()[0],

                'final_test_pass_rate': 0,

                'total_questions_asked': conn.execute("""
                    SELECT COUNT(*) FROM qa_history
                """).fetchone()[0],

                'active_users_7_days': conn.execute("""
                    SELECT COUNT(DISTINCT user_id) FROM user_progress
                    WHERE updated_at >= datetime('now', '-7 days')
                """).fetchone()[0],
            }

            # Calculate pass rate
            total_tests = analytics['total_final_tests']
            if total_tests > 0:
                passed = conn.execute("""
                    SELECT COUNT(*) FROM final_test_attempts WHERE passed = 1
                """).fetchone()[0]
                analytics['final_test_pass_rate'] = (passed / total_tests) * 100

            return analytics

    # ===== LESSON DEPENDENCIES =====

    def add_lesson_dependency(self, lesson_no: str, prerequisite_lesson_no: str, is_required: bool = True):
        """Add a prerequisite for a lesson."""
        with self.get_connection() as conn:
            try:
                conn.execute("""
                    INSERT INTO lesson_dependencies (lesson_no, prerequisite_lesson_no, is_required)
                    VALUES (?, ?, ?)
                """, (lesson_no, prerequisite_lesson_no, is_required))
                conn.commit()
                return True
            except:
                return False

    def get_lesson_prerequisites(self, lesson_no: str) -> List[str]:
        """Get all prerequisites for a lesson."""
        with self.get_connection() as conn:
            results = conn.execute("""
                SELECT prerequisite_lesson_no
                FROM lesson_dependencies
                WHERE lesson_no = ? AND is_required = 1
            """, (lesson_no,)).fetchall()
            return [row[0] for row in results]

    def can_access_lesson(self, user_id: int, lesson_no: str) -> bool:
        """Check if user has completed all prerequisites for a lesson."""
        prerequisites = self.get_lesson_prerequisites(lesson_no)
        if not prerequisites:
            return True

        completed = self.get_completed_lessons(user_id)
        return all(prereq in completed for prereq in prerequisites)


# Create extended database instance
db_extended = ExtendedDatabaseManager()


if __name__ == "__main__":
    # Test extended features
    print("✅ Extended Database Manager loaded successfully")
    print("\nAvailable extended features:")
    print("  - Audit logging")
    print("  - User preferences")
    print("  - Bookmarks and notes")
    print("  - Achievements system")
    print("  - Leaderboard")
    print("  - Statistics and analytics")
    print("  - Lesson dependencies")
