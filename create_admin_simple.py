#!/usr/bin/env python3
"""
Simple admin user creation script that works with existing database structure
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_admin_user():
    """Create an admin user directly in the database"""
    db_path = 'local.sqlite'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please run the app first to create the database.")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if users table has role column
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        has_role_column = 'role' in columns
        
        if not has_role_column:
            # Add role column if it doesn't exist
            print("📝 Adding role column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_role ON users (role)")
            conn.commit()
            print("✅ Role column added successfully!")
        
        # Check if admin user already exists
        cursor.execute("SELECT id, username, email, role FROM users WHERE email = ?", ('darthusian@gmail.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id, username, email, role = existing_user
            if role != 'admin':
                # Update existing user to admin
                cursor.execute("UPDATE users SET role = 'admin' WHERE email = ?", ('darthusian@gmail.com',))
                conn.commit()
                print(f"✅ Updated existing user '{username}' to admin role!")
            else:
                print(f"ℹ️  User '{username}' is already an admin!")
            return
        
        # Create new admin user
        password_hash = generate_password_hash('pepperrrr')
        now = datetime.now()
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('pepper', 'darthusian@gmail.com', password_hash, 'admin', now, now))
        
        conn.commit()
        
        print("✅ Admin user created successfully!")
        print(f"   Email: darthusian@gmail.com")
        print(f"   Username: pepper")
        print(f"   Password: pepperrrr")
        print(f"   Role: admin")
        print("\n⚠️  IMPORTANT: Change the password after first login!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    create_admin_user()