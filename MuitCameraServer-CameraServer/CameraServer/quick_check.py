#!/usr/bin/env python3
"""
Quick sanity check - tests basic functionality without GUI
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from database_manager.models import AuditoryNote, CameraCabJournalNote
from settings import SettingsFile
from datetime import datetime, timedelta


def quick_check():
    """Quick functionality check"""
    print("\n" + "="*60)
    print("CAMERA SERVER - QUICK FUNCTIONALITY CHECK")
    print("="*60)
    
    try:
        # 1. Test settings loading
        print("\n[1/4] Loading settings...")
        settings = SettingsFile()
        settings.read_config_file()
        print("    ✓ Settings loaded")
        print(f"      - Database: {settings.database_settings.db_path}")
        
        # 2. Test database connection
        print("\n[2/4] Connecting to database...")
        if os.path.exists("quick_check.db"):
            os.remove("quick_check.db")
        
        settings.database_settings.db_path = "quick_check.db"
        settings.db_path = "quick_check.db"
        
        db = DatabaseManager(settings)
        db.open_connection()
        print("    ✓ Database connected")
        
        # 3. Test data insertion
        print("\n[3/4] Testing data operations...")
        session = db.Session()
        
        # Create test auditory
        test_aud = AuditoryNote(
            name="Test Room",
            number=999,
            corpus="TEST",
            category="test"
        )
        session.add(test_aud)
        session.commit()
        
        # Verify insertion
        count = session.query(AuditoryNote).count()
        print(f"    ✓ Inserted test data ({count} record(s))")
        
        # Create test camera
        test_cam = CameraCabJournalNote(
            camera_ip="127.0.0.1",
            id_cab=999,
            login_camera="test",
            password_camera="test",
            port_camera=":554",
            is_busy=0
        )
        session.add(test_cam)
        session.commit()
        print(f"    ✓ Camera data added")
        
        # 4. Test queries
        print("\n[4/4] Testing queries...")
        auditories = session.query(AuditoryNote).all()
        cameras = session.query(CameraCabJournalNote).all()
        print(f"    ✓ Auditories: {len(auditories)}")
        print(f"    ✓ Cameras: {len(cameras)}")
        
        session.close()
        db.close_connection()
        
        # Cleanup
        if os.path.exists("quick_check.db"):
            os.remove("quick_check.db")
        
        print("\n" + "="*60)
        print("✓ ALL CHECKS PASSED - PROJECT IS WORKING!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Run full tests: python run_tests.py")
        print("  2. Check GUI: python Server/main.py")
        print("  3. Read docs: TESTING_GUIDE.md")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*60)
        print("QUICK CHECK FAILED")
        print("="*60)
        return False


if __name__ == "__main__":
    success = quick_check()
    sys.exit(0 if success else 1)
