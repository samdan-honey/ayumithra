import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'health_data.db')
print(f'DB Path: {db_path}')
print(f'File exists: {os.path.exists(db_path)}')
print(f'File size: {os.path.getsize(db_path)} bytes')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f'Tables: {[t[0] for t in tables]}')

if tables:
    cursor.execute('SELECT name FROM diseases')
    diseases = cursor.fetchall()
    print(f'Diseases: {[d[0] for d in diseases]}')
else:
    print('No tables found - database is empty!')

conn.close()
