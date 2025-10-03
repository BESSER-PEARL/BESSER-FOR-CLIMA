#!/usr/bin/env python3
"""
Database Migration Script for Dashboard Sections
================================================

This script migrates existing dashboard data to the new section-based structure.
It creates the necessary database tables and migrates existing visualizations
to use the new section system.

Usage:
    python migrate_sections.py

Requirements:
    - PostgreSQL database configured in .env
    - Backend dependencies installed
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.database import engine, Base
from app.models import Dashboard, DashboardSection, Visualization
from app.core.config import settings

def create_tables():
    """Create all database tables"""
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def migrate_existing_data():
    """Migrate existing dashboard data to use sections"""
    print("🔄 Migrating existing data to section-based structure...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Get all dashboards
        dashboards = session.query(Dashboard).all()
        print(f"📊 Found {len(dashboards)} dashboards to migrate")
        
        for dashboard in dashboards:
            print(f"   Processing dashboard: {dashboard.name}")
            
            # Check if this dashboard already has sections
            existing_sections = session.query(DashboardSection).filter(
                DashboardSection.dashboard_id == dashboard.id
            ).all()
            
            if existing_sections:
                print(f"   ⏭️  Dashboard {dashboard.name} already has sections, skipping...")
                continue
            
            # Get visualizations for this dashboard
            visualizations = session.query(Visualization).filter(
                Visualization.dashboard_id == dashboard.id
            ).all()
            
            if not visualizations:
                print(f"   📄 No visualizations found, creating default section")
                # Create default section even if no visualizations
                default_section = DashboardSection(
                    name="Main",
                    description="Default section for dashboard visualizations",
                    order=0,
                    dashboard_id=dashboard.id,
                    is_active=True
                )
                session.add(default_section)
                session.flush()  # Get the ID
                continue
            
            # Group visualizations by their current section (if any)
            sections_map = {}
            for viz in visualizations:
                # Check if visualization has a section_name or similar field
                section_name = getattr(viz, 'section_name', None) or getattr(viz, 'section', None) or "Main"
                
                if section_name not in sections_map:
                    sections_map[section_name] = []
                sections_map[section_name].append(viz)
            
            print(f"   📂 Creating {len(sections_map)} sections")
            
            # Create sections and update visualizations
            for order, (section_name, section_visualizations) in enumerate(sections_map.items()):
                # Create section
                section = DashboardSection(
                    name=section_name,
                    description=f"Section containing {len(section_visualizations)} visualizations",
                    order=order,
                    dashboard_id=dashboard.id,
                    is_active=True
                )
                session.add(section)
                session.flush()  # Get the ID
                
                print(f"      ✅ Created section '{section_name}' with {len(section_visualizations)} visualizations")
                
                # Update visualizations to reference this section
                for viz in section_visualizations:
                    viz.section_id = section.id
        
        # Commit all changes
        session.commit()
        print("✅ Data migration completed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        session.close()

def verify_migration():
    """Verify the migration was successful"""
    print("🔍 Verifying migration...")
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Count dashboards, sections, and visualizations
        dashboard_count = session.query(Dashboard).count()
        section_count = session.query(DashboardSection).count()
        visualization_count = session.query(Visualization).count()
        
        # Count visualizations with section references
        visualizations_with_sections = session.query(Visualization).filter(
            Visualization.section_id.isnot(None)
        ).count()
        
        print(f"📊 Migration Results:")
        print(f"   • Dashboards: {dashboard_count}")
        print(f"   • Sections: {section_count}")
        print(f"   • Visualizations: {visualization_count}")
        print(f"   • Visualizations with sections: {visualizations_with_sections}")
        
        if visualization_count > 0 and visualizations_with_sections == visualization_count:
            print("✅ All visualizations are properly linked to sections")
        elif visualization_count == 0:
            print("ℹ️  No visualizations found in database")
        else:
            print(f"⚠️  {visualization_count - visualizations_with_sections} visualizations are not linked to sections")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        session.close()

def main():
    """Main migration function"""
    print("🚀 Starting Dashboard Sections Migration")
    print("=" * 50)
    
    try:
        # Check database connection
        print("🔌 Testing database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Create tables
        create_tables()
        
        # Migrate data
        migrate_existing_data()
        
        # Verify migration
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Start the backend server: python run.py")
            print("2. Start the frontend: npm run dev")
            print("3. Test the enhanced sections functionality")
        else:
            print("\n⚠️  Migration completed with warnings. Please check the logs above.")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nPlease check your database configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()