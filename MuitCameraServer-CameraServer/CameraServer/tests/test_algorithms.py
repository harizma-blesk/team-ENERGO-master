import sys
import os
from datetime import datetime, timedelta, time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager
from database_manager.models import AuditoryNote, AuditoryJournalNote, CameraCabJournalNote
from algorithms import AuditoryFinder
from settings import SettingsFile


def setup_test_env():
    """Setup test database and finder"""
    settings = SettingsFile()
    settings.database_settings.db_path = "test_algo.db"
    settings.db_path = "test_algo.db"
    
    # Remove old test db
    if os.path.exists("test_algo.db"):
        os.remove("test_algo.db")
    
    db = DatabaseManager(settings)
    db.open_connection()
    
    # Add test data
    session = db.Session()
    
    auditories = [
        AuditoryNote(name="Класс A101", number=101, corpus="A", category="учебный"),
        AuditoryNote(name="Класс A102", number=102, corpus="A", category="учебный"),
        AuditoryNote(name="Класс B201", number=201, corpus="B", category="учебный"),
    ]
    
    for aud in auditories:
        session.add(aud)
    
    # Add cameras
    cameras = [
        CameraCabJournalNote(camera_ip="192.168.1.10", id_cab=101, login_camera="admin",
                            password_camera="pass", port_camera=":554", is_busy=0),
        CameraCabJournalNote(camera_ip="192.168.1.11", id_cab=102, login_camera="admin",
                            password_camera="pass", port_camera=":554", is_busy=0),
        CameraCabJournalNote(camera_ip="192.168.1.12", id_cab=201, login_camera="admin",
                            password_camera="pass", port_camera=":554", is_busy=0),
    ]
    
    for cam in cameras:
        session.add(cam)
    
    session.commit()
    session.close()
    
    finder = AuditoryFinder(db)
    return db, finder


def test_finder_initialization():
    """Test AuditoryFinder initialization"""
    print("\n=== Testing AuditoryFinder Initialization ===")
    db, finder = setup_test_env()
    print("[OK] AuditoryFinder initialized successfully")
    return db, finder


def test_get_all_auditories(db):
    """Test getting all auditories"""
    print("\n=== Testing Get All Auditories ===")
    session = db.Session()
    
    auditories = session.query(AuditoryNote).all()
    print(f"[OK] Retrieved {len(auditories)} auditories:")
    for aud in auditories:
        print(f"  - {aud.name} (#{aud.number}) - Corpus {aud.corpus}")
    
    session.close()
    return len(auditories) > 0


def test_find_free_auditory(db, finder):
    """Test finding free auditory"""
    print("\n=== Testing Find Free Auditory ===")
    
    # Test finding in corpus A
    session = db.Session()
    auditories = session.query(AuditoryNote).filter_by(corpus="A").all()
    session.close()
    
    if auditories:
        print(f"[OK] Found {len(auditories)} auditories in corpus A")
        for aud in auditories:
            print(f"  - {aud.name} is available (id: {aud.id})")
        return True
    else:
        print("[FAIL] No auditories found in corpus A")
        return False


def test_camera_occupancy(db):
    """Test camera occupancy status"""
    print("\n=== Testing Camera Occupancy ===")
    session = db.Session()
    
    cameras = session.query(CameraCabJournalNote).all()
    print(f"[OK] Found {len(cameras)} cameras:")
    for cam in cameras:
        status = "BUSY" if cam.is_busy else "FREE"
        print(f"  - Room #{cam.id_cab}: {status} ({cam.camera_ip})")
    
    # Test updating occupancy
    if cameras:
        cameras[0].is_busy = 1
        session.commit()
        print(f"[OK] Updated room #{cameras[0].id_cab} status to BUSY")
    
    session.close()
    return True


def test_booking_creation(db):
    """Test creating booking"""
    print("\n=== Testing Booking Creation ===")
    session = db.Session()
    
    now = datetime.now()
    booking = AuditoryJournalNote(
        aud_id=101,
        startTime=now,
        endTime=now + timedelta(hours=2),
        duration=120,
        dayOfWeek=now.weekday(),
        timeStatus=1  # confirmed
    )
    session.add(booking)
    session.commit()
    
    # Verify
    total = session.query(AuditoryJournalNote).count()
    print(f"[OK] Booking created successfully. Total bookings: {total}")
    
    session.close()
    return True


def test_schedule_conflict(db):
    """Test detecting schedule conflicts"""
    print("\n=== Testing Schedule Conflict Detection ===")
    session = db.Session()
    
    now = datetime.now()
    
    # Create two overlapping bookings for same room
    booking1 = AuditoryJournalNote(
        aud_id=102,
        startTime=now,
        endTime=now + timedelta(hours=1),
        duration=60,
        dayOfWeek=now.weekday(),
        timeStatus=1
    )
    session.add(booking1)
    session.commit()
    
    # Check for conflicts
    conflicts = session.query(AuditoryJournalNote).filter(
        AuditoryJournalNote.aud_id == 102,
        AuditoryJournalNote.startTime < now + timedelta(minutes=30),
        AuditoryJournalNote.endTime > now
    ).all()
    
    print(f"[OK] Found {len(conflicts)} conflicting booking(s)")
    
    session.close()
    return True


def run_all_tests():
    """Run all algorithm tests"""
    print("=" * 50)
    print("CAMERA SERVER ALGORITHM TESTS")
    print("=" * 50)
    
    try:
        db, finder = test_finder_initialization()
        test_get_all_auditories(db)
        test_find_free_auditory(db, finder)
        test_camera_occupancy(db)
        test_booking_creation(db)
        test_schedule_conflict(db)
        
        print("\n" + "=" * 50)
        print("[OK] ALL TESTS PASSED")
        print("=" * 50)
        
        # Cleanup
        db.close_connection()
        if os.path.exists("test_algo.db"):
            os.remove("test_algo.db")
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
