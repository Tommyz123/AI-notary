"""
Database Backup and Maintenance Utilities
Provides tools for backing up, restoring, and maintaining the database
"""

import sqlite3
import os
import shutil
import json
from datetime import datetime, timedelta
import gzip

DB_PATH = "notary_training.db"
BACKUP_DIR = "database_backups"

class DatabaseMaintenance:
    """Database backup and maintenance utilities."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.backup_dir = BACKUP_DIR
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, compress=True):
        """Create a backup of the database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"notary_training_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_name)

        try:
            # Create backup using SQLite backup API
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)

            source_conn.backup(backup_conn)

            backup_conn.close()
            source_conn.close()

            if compress:
                # Compress the backup
                compressed_path = backup_path + ".gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(backup_path)
                backup_path = compressed_path

            file_size = os.path.getsize(backup_path) / 1024  # KB
            print(f"✅ Backup created: {os.path.basename(backup_path)}")
            print(f"   Size: {file_size:.2f} KB")
            print(f"   Location: {backup_path}")

            return backup_path

        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None

    def restore_backup(self, backup_path):
        """Restore database from a backup file."""
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False

        try:
            # Create a safety backup of current database
            current_backup = self.create_backup(compress=False)
            print(f"   Created safety backup: {current_backup}")

            # Handle compressed backups
            restore_path = backup_path
            if backup_path.endswith('.gz'):
                temp_path = backup_path[:-3]
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                restore_path = temp_path

            # Restore the backup
            shutil.copy2(restore_path, self.db_path)

            # Clean up temp file if needed
            if restore_path != backup_path:
                os.remove(restore_path)

            print(f"✅ Database restored from: {os.path.basename(backup_path)}")
            return True

        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False

    def list_backups(self):
        """List all available backups."""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.startswith("notary_training_backup_"):
                file_path = os.path.join(self.backup_dir, file)
                size = os.path.getsize(file_path) / 1024  # KB
                mtime = os.path.getmtime(file_path)
                backups.append({
                    'name': file,
                    'path': file_path,
                    'size_kb': size,
                    'created': datetime.fromtimestamp(mtime)
                })

        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups

    def cleanup_old_backups(self, keep_days=30, keep_min=5):
        """Remove backups older than specified days, keeping minimum number."""
        backups = self.list_backups()

        if len(backups) <= keep_min:
            print(f"ℹ️  Keeping all {len(backups)} backups (minimum: {keep_min})")
            return

        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed = 0

        # Sort by date and keep newest ones
        for backup in backups[keep_min:]:
            if backup['created'] < cutoff_date:
                try:
                    os.remove(backup['path'])
                    removed += 1
                    print(f"   Removed old backup: {backup['name']}")
                except Exception as e:
                    print(f"   Warning: Could not remove {backup['name']}: {e}")

        print(f"✅ Cleaned up {removed} old backup(s)")
        print(f"   Kept {len(backups) - removed} backup(s)")

    def export_to_json(self, output_dir="data_exports"):
        """Export database tables to JSON format."""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        tables = [
            'users', 'lessons', 'user_progress', 'quiz_attempts',
            'final_test_attempts', 'qa_history', 'achievements',
            'user_achievements', 'user_preferences'
        ]

        export_summary = {}

        for table in tables:
            try:
                rows = conn.execute(f"SELECT * FROM {table}").fetchall()
                data = [dict(row) for row in rows]

                filename = f"{table}_{timestamp}.json"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)

                export_summary[table] = {
                    'records': len(data),
                    'file': filename
                }

                print(f"✅ Exported {table}: {len(data)} records")

            except sqlite3.Error as e:
                print(f"⚠️  Could not export {table}: {e}")

        conn.close()

        # Save export summary
        summary_file = os.path.join(output_dir, f"export_summary_{timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(export_summary, f, indent=2)

        print(f"\n✅ Export completed to: {output_dir}")
        return export_summary

    def vacuum_database(self):
        """Vacuum the database to reclaim space and defragment."""
        conn = sqlite3.connect(self.db_path)

        # Get size before vacuum
        size_before = os.path.getsize(self.db_path) / 1024  # KB

        conn.execute("VACUUM")
        conn.close()

        # Get size after vacuum
        size_after = os.path.getsize(self.db_path) / 1024  # KB
        saved = size_before - size_after

        print(f"✅ Database vacuumed")
        print(f"   Size before: {size_before:.2f} KB")
        print(f"   Size after: {size_after:.2f} KB")
        print(f"   Space saved: {saved:.2f} KB ({saved/size_before*100:.1f}%)")

    def analyze_database(self):
        """Analyze database for query optimizer."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("ANALYZE")
        conn.close()
        print("✅ Database analyzed (query optimizer updated)")

    def check_integrity(self):
        """Check database integrity."""
        conn = sqlite3.connect(self.db_path)
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()

        if result == "ok":
            print("✅ Database integrity check: PASSED")
            return True
        else:
            print(f"❌ Database integrity check: FAILED")
            print(f"   Error: {result}")
            return False

    def get_database_stats(self):
        """Get comprehensive database statistics."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        stats = {}

        # Database file size
        stats['file_size_kb'] = os.path.getsize(self.db_path) / 1024

        # Table counts
        tables = conn.execute("""
            SELECT name FROM sqlite_master WHERE type='table'
            AND name NOT LIKE 'sqlite_%'
        """).fetchall()

        table_stats = {}
        total_rows = 0

        for table in tables:
            table_name = table['name']
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                table_stats[table_name] = count
                total_rows += count
            except sqlite3.Error:
                table_stats[table_name] = 'N/A'

        stats['tables'] = table_stats
        stats['total_rows'] = total_rows

        # Index count
        index_count = conn.execute("""
            SELECT COUNT(*) FROM sqlite_master WHERE type='index'
            AND name NOT LIKE 'sqlite_%'
        """).fetchone()[0]
        stats['indexes'] = index_count

        # View count
        view_count = conn.execute("""
            SELECT COUNT(*) FROM sqlite_master WHERE type='view'
        """).fetchone()[0]
        stats['views'] = view_count

        # Trigger count
        trigger_count = conn.execute("""
            SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'
        """).fetchone()[0]
        stats['triggers'] = trigger_count

        conn.close()
        return stats

    def print_database_stats(self):
        """Print database statistics in a formatted way."""
        stats = self.get_database_stats()

        print("\n" + "=" * 60)
        print("DATABASE STATISTICS")
        print("=" * 60)
        print(f"Database File: {self.db_path}")
        print(f"File Size: {stats['file_size_kb']:.2f} KB")
        print(f"Total Rows: {stats['total_rows']:,}")
        print(f"Indexes: {stats['indexes']}")
        print(f"Views: {stats['views']}")
        print(f"Triggers: {stats['triggers']}")
        print("\nTable Row Counts:")
        print("-" * 60)

        for table, count in sorted(stats['tables'].items()):
            print(f"  {table:30s} {str(count):>10s}")

        print("=" * 60)

    def optimize_all(self):
        """Run all optimization procedures."""
        print("\n🔧 Running comprehensive database optimization...")
        print("=" * 60)

        self.check_integrity()
        self.analyze_database()
        self.vacuum_database()

        print("=" * 60)
        print("✅ All optimization procedures completed")


def main():
    """Main maintenance menu."""
    maintenance = DatabaseMaintenance()

    print("\n" + "=" * 60)
    print("DATABASE BACKUP & MAINTENANCE UTILITY")
    print("=" * 60)

    # Show current stats
    maintenance.print_database_stats()

    # Create automatic backup
    print("\n📦 Creating automatic backup...")
    maintenance.create_backup(compress=True)

    # List existing backups
    print("\n📋 Existing backups:")
    backups = maintenance.list_backups()
    if backups:
        for i, backup in enumerate(backups[:5], 1):
            print(f"  {i}. {backup['name']}")
            print(f"     Size: {backup['size_kb']:.2f} KB")
            print(f"     Created: {backup['created']}")
    else:
        print("  No backups found")

    # Cleanup old backups
    print("\n🧹 Cleaning up old backups...")
    maintenance.cleanup_old_backups(keep_days=30, keep_min=5)

    # Run optimization
    maintenance.optimize_all()

    print("\n" + "=" * 60)
    print("🎉 Maintenance completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
