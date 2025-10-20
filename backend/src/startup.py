#!/usr/bin/env python3
"""
Startup script for the Climaborough backend.
Handles database initialization and optional minimal KPI creation.
"""
import os
import sys
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def wait_for_database():
    """Wait for database to be ready."""
    from app.core.database import engine
    from sqlalchemy import text
    
    max_retries = 30
    retry_interval = 2
    
    print("Waiting for database connection...")
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✓ Database connection established!")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Attempt {attempt + 1}/{max_retries} failed. Retrying in {retry_interval}s...")
                time.sleep(retry_interval)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts")
                raise

def initialize_database():
    """Initialize database schema."""
    print("\nInitializing database schema...")
    try:
        from init_db import main as init_db_main
        init_db_main()
        print("✓ Database schema initialized!")
        return True
    except Exception as e:
        print(f"⚠️  Database initialization: {e}")
        # Don't fail if tables already exist
        return True

def create_minimal_kpis():
    """Create minimal KPIs if AUTO_CREATE_KPIS is enabled."""
    auto_create = os.getenv("AUTO_CREATE_KPIS", "false").lower() == "true"
    
    if not auto_create:
        print("\nℹ️  Skipping KPI auto-creation (AUTO_CREATE_KPIS not set)")
        return
    
    print("\nAuto-creating minimal KPIs...")
    try:
        from create_minimal_kpis import main as create_kpis_main
        create_kpis_main()
    except Exception as e:
        print(f"⚠️  KPI creation: {e}")
        # Don't fail startup if KPI creation fails

def start_server():
    """Start the FastAPI server."""
    import uvicorn
    
    print("\n" + "=" * 60)
    print("Starting Climaborough Backend Server")
    print("=" * 60)
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

def main():
    """Main startup sequence."""
    print("=" * 60)
    print("Climaborough Backend - Startup Sequence")
    print("=" * 60)
    
    try:
        # Step 1: Wait for database
        wait_for_database()
        
        # Step 2: Initialize database schema
        initialize_database()
        
        # Step 3: Create minimal KPIs (if enabled)
        create_minimal_kpis()
        
        # Step 4: Start the server
        start_server()
        
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
