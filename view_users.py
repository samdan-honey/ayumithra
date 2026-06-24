import sqlite3
import os

def display_users():
    db_path = 'database/health_app.db'
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return

    print("=" * 60)
    print(f"{'ID':<6} | {'USERNAME':<35} | {'PASSWORD HASH (SHA-256)':<15}")
    print("=" * 60)

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, password FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
        
        for row in rows:
            # Truncate hash for clean display
            truncated_hash = row['password'][:12] + "..."
            print(f"{row['id']:<6} | {row['username']:<35} | {truncated_hash:<15}")
            
        print("=" * 60)
        print(f"Total registered users: {len(rows)}")
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Database Error: {e}")
        print("Tip: Make sure the app has been started at least once to create the tables.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    display_users()
