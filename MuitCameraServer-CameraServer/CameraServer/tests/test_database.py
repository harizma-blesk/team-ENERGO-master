import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager
from database_manager.models import Base, AuditoryNote, AuditoryJournalNote, CameraCabJournalNote
from settings import SettingsFile


def setup_test_database():
    """Create test database with sample data"""
    settings = SettingsFile()
    settings.database_settings.db_path = "test_camera_server.db"
    settings.db_path = "test_camera_server.db"
    
    # Remove old test db if exists
    if os.path.exists("test_camera_server.db"):
        os.remove("test_camera_server.db")
    
    db = DatabaseManager(settings)
    db.open_connection()
    
    # Insert test data
    session = db.Session()
    
    # Add test auditories
    auditories = [
        AuditoryNote(name="Класс 101", number=101, corpus="A", category="учебный"),
        AuditoryNote(name="Класс 102", number=102, corpus="A", category="учебный"),
        AuditoryNote(name="Класс 201", number=201, corpus="B", category="учебный"),
        AuditoryNote(name="Лаборатория 301", number=301, corpus="B", category="лаборатория"),
    ]
    
    for aud in auditories:
        session.add(aud)
    session.commit()
    
    # Add test cameras
    cameras = [
        CameraCabJournalNote(camera_ip="192.168.1.10", id_cab=101, login_camera="admin", 
                            password_camera="pass123", port_camera=":554", is_busy=0),
        CameraCabJournalNote(camera_ip="192.168.1.11", id_cab=102, login_camera="admin", 
                            password_camera="pass123", port_camera=":554", is_busy=0),
        CameraCabJournalNote(camera_ip="192.168.1.12", id_cab=201, login_camera="admin", 
                            password_camera="pass123", port_camera=":554", is_busy=0),
    ]
    
    for cam in cameras:
        session.add(cam)
    session.commit()
    
    # Add some bookings
    now = datetime.now()
    booking = AuditoryJournalNote(
        aud_id=101,
        startTime=now,
        endTime=now + timedelta(hours=1),
        duration=60,
        dayOfWeek=now.weekday(),
        timeStatus=1
    )
    session.add(booking)
    session.commit()
    
    session.close()
    return db


def test_database_connection():
    """Test database connection"""
    print("\n=== Testing Database Connection ===")
    db = setup_test_database()
    print("[OK] Database created and connected successfully")
    print(f"  Database file: test_camera_server.db")
    return db


def test_database_queries(db):
    """Test database queries"""
    print("\n=== Testing Database Queries ===")
    session = db.Session()
    
    # Test reading auditories
    auditories = session.query(AuditoryNote).all()
    print(f"[OK] Found {len(auditories)} auditories")
    for aud in auditories:
        print(f"  - {aud.name} (#{aud.number}) in corpus {aud.corpus}")
    
    # Test reading cameras
    cameras = session.query(CameraCabJournalNote).all()
    print(f"[OK] Found {len(cameras)} cameras")
    for cam in cameras:
        print(f"  - Camera at {cam.camera_ip} for room #{cam.id_cab}")
    
    # Test reading bookings
    bookings = session.query(AuditoryJournalNote).all()
    print(f"[OK] Found {len(bookings)} bookings")
    
    session.close()


def test_insert_operation(db):
    """Test insert operation"""
    print("\n=== Testing Insert Operation ===")
    session = db.Session()
    
    new_booking = AuditoryJournalNote(
        aud_id=102,
        startTime=datetime.now(),
        endTime=datetime.now() + timedelta(hours=2),
        duration=120,
        dayOfWeek=datetime.now().weekday(),
        timeStatus=2  # temporary
    )
    session.add(new_booking)
    session.commit()
    
    # Verify
    count = session.query(AuditoryJournalNote).count()
    print(f"[OK] Booking inserted successfully. Total bookings: {count}")
    
    session.close()


def test_update_operation(db):
    """Test update operation"""
    print("\n=== Testing Update Operation ===")
    session = db.Session()
    
    # Update camera status
    camera = session.query(CameraCabJournalNote).first()
    if camera:
        camera.is_busy = 1
        session.commit()
        print(f"[OK] Updated camera #{camera.id_cab} status to busy")
    
    session.close()


def test_delete_operation(db):
    """Test delete operation"""
    print("\n=== Testing Delete Operation ===")
    session = db.Session()
    
    # Delete temporary bookings
    deleted = session.query(AuditoryJournalNote).filter_by(timeStatus=2).delete()
    session.commit()
    print(f"[OK] Deleted {deleted} temporary bookings")
    
    session.close()


def run_all_tests():
    """Run all database tests"""
    print("=" * 50)
    print("CAMERA SERVER DATABASE TESTS")
    print("=" * 50)
    
    try:
        db = test_database_connection()
        test_database_queries(db)
        test_insert_operation(db)
        test_update_operation(db)
        test_delete_operation(db)
        
        print("\n" + "=" * 50)
        print("[OK] ALL TESTS PASSED")
        print("=" * 50)
        
        # Cleanup
        db.close_connection()
        if os.path.exists("test_camera_server.db"):
            os.remove("test_camera_server.db")
        print("\nTest database cleaned up")
        
        return True
    
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
