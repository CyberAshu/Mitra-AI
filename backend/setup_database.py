#!/usr/bin/env python3
"""
Database setup script for Mitra AI Backend
"""

import asyncio
import sys
import os
from sqlalchemy import text

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_engine, create_tables, drop_tables
from app.core.config import get_settings, create_directories
from app.models.user import User
from app.api.routes.auth import auth_service

async def create_admin_user():
    """Create an admin user"""
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if admin user already exists
            result = await session.execute(
                text("SELECT id FROM users WHERE username = 'admin'")
            )
            if result.first():
                print("Admin user already exists")
                return
            
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@mitraai.local",
                hashed_password=auth_service.hash_password("MitraAI@2024"),
                full_name="System Administrator",
                is_active=True,
                is_superuser=True
            )
            
            session.add(admin_user)
            await session.commit()
            print("Admin user created successfully")
            print("Username: admin")
            print("Password: MitraAI@2024")
            
        except Exception as e:
            print(f"Error creating admin user: {e}")
            await session.rollback()

async def setup_database():
    """Set up the database"""
    try:
        print("Setting up Mitra AI database...")
        
        # Create directories
        create_directories()
        print("✓ Created required directories")
        
        # Create tables
        await create_tables()
        print("✓ Created database tables")
        
        # Create admin user
        await create_admin_user()
        print("✓ Admin user setup complete")
        
        print("\nDatabase setup completed successfully!")
        print("\nYou can now start the backend server with:")
        print("cd backend && python main.py")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

async def reset_database():
    """Reset the database (drop and recreate all tables)"""
    try:
        print("Resetting database...")
        
        # Drop all tables
        await drop_tables()
        print("✓ Dropped all tables")
        
        # Recreate tables
        await create_tables()
        print("✓ Recreated tables")
        
        # Create admin user
        await create_admin_user()
        print("✓ Created admin user")
        
        print("\nDatabase reset completed successfully!")
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Mitra AI Database Setup")
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset the database (drop and recreate all tables)"
    )
    
    args = parser.parse_args()
    
    if args.reset:
        asyncio.run(reset_database())
    else:
        asyncio.run(setup_database())
