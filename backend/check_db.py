#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('chatbot.db')
cursor = conn.cursor()

# Check tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

# Check users
try:
    cursor.execute('SELECT COUNT(*) FROM users')
    users = cursor.fetchone()[0]
    print(f'Users count: {users}')

    if users > 0:
        cursor.execute('SELECT id, email, username FROM users LIMIT 5')
        user_data = cursor.fetchall()
        print('Users:', user_data)
except Exception as e:
    print(f'No users table or error: {e}')

# Check invoices
try:
    cursor.execute('SELECT COUNT(*) FROM invoices')
    invoices = cursor.fetchone()[0]
    print(f'Invoices count: {invoices}')
except Exception as e:
    print(f'No invoices table or error: {e}')

conn.close()