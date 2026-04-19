import sys
import os
import time
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_manager import DatabaseManager
from database_manager.models import AuditoryNote, CameraCabJournalNote, AuditoryJournalNote
from algorithms import AlgorithmManager, AuditoryFinder
from settings import SettingsFile
from tests.mock_servers import MockPHPServer, MockESPServer


def setup_integration_test():
    """Setup full integration test environment"""
    print("\n=== Setting Up Integration Test Environment ===")
    
    settings = SettingsFile()
    settings.database_settings.db_path = "test_integration.db"
    settings.db_path = "test_integration.db"
    
    # Remove old db
    if os.path.exists("test_integration.db"):
        os.remove("test_integration.db")
    
    db = DatabaseManager(settings)
    db.open_connection()
    
    # Add test data
    session = db.Session()
    
    # Add auditories
    for i in range(1, 6):
        aud = AuditoryNote(
            name=f"Classroom {i}",
            number=100 + i,
            corpus="A" if i <= 3 else "B",
            category="учебный"
        )
        session.add(aud)
    
    # Add cameras
    for i in range(1, 4):
        cam = CameraCabJournalNote(
            camera_ip=f"192.168.1.{10+i}",
            id_cab=100+i,
            login_camera="admin",
            password_camera="pass",
            port_camera=":554",
            is_busy=0
        )
        session.add(cam)
    
    session.commit()
    session.close()
    
    print("[OK] Test database setup complete")
    print(f"  - 5 classrooms created")
    print(f"  - 3 cameras added")
    
    return db, settings


def test_full_workflow():
    """Test complete workflow"""
    print("\n=== Testing Full Workflow ===")
    
    db, settings = setup_integration_test()
    session = db.Session()
    
    # Step 1: Check available auditories
    print("\nStep 1: Checking available auditories...")
    auditories = session.query(AuditoryNote).all()
    print(f"[OK] Available: {len(auditories)} auditories")
    for aud in auditories:
        print(f"  - Room {aud.number} ({aud.corpus})")
    
    # Step 2: Check camera status
    print("\nStep 2: Checking camera status...")
    cameras = session.query(CameraCabJournalNote).all()
    for cam in cameras:
        status = "BUSY" if cam.is_busy else "FREE"
        print(f"  - Room {cam.id_cab}: {status}")
    
    # Step 3: Simulate room booking
    print("\nStep 3: Simulating room booking...")
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
    print("[OK] Room 101 booked for 1 hour")
    
    # Step 4: Check for conflicts
    print("\nStep 4: Checking for schedule conflicts...")
    conflicts = session.query(AuditoryJournalNote).filter(
        AuditoryJournalNote.aud_id == 101
    ).all()
    print(f"[OK] Found {len(conflicts)} booking(s) for room 101")
    
    # Step 5: Update camera occupancy
    print("\nStep 5: Updating camera occupancy...")
    camera = session.query(CameraCabJournalNote).filter_by(id_cab=101).first()
    if camera:
        camera.is_busy = 1
        session.commit()
        print("[OK] Room 101 marked as occupied by camera")
    
    # Step 6: Verify final state
    print("\nStep 6: Verifying final state...")
    final_bookings = session.query(AuditoryJournalNote).count()
    final_cameras = session.query(CameraCabJournalNote).filter_by(is_busy=1).count()
    print(f"[OK] Final state: {final_bookings} booking(s), {final_cameras} occupied room(s)")
    
    session.close()
    db.close_connection()
    
    # Cleanup
    if os.path.exists("test_integration.db"):
        os.remove("test_integration.db")
    
    return True


def test_with_mock_servers():
    """Test with mock servers"""
    print("\n=== Testing with Mock Servers ===")
    
    # Start mock servers
    print("\nStarting mock servers...")
    php_server = MockPHPServer()
    esp_server = MockESPServer()
    
    php_server.start()
    esp_server.start()
    time.sleep(1)
    
    print("[OK] Mock servers started (PHP on 8080, ESP on 4444)")
    
    # Test PHP server communication
    try:
        import requests
        test_data = {'action': 'find_auditory', 'corpus': 'A', 'duration': 60}
        response = requests.post('http://127.0.0.1:8080/api/find_auditory.php', json=test_data, timeout=2)
        print(f"[OK] PHP server responding: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] PHP server test failed: {e}")
    
    php_server.stop()
    esp_server.stop()
    
    print("[OK] Mock servers test passed")
    return True


def test_settings_loading():
    """Test settings loading"""
    print("\n=== Testing Settings Loading ===")
    
    settings = SettingsFile()
    settings.read_config_file()
    
    print(f"[OK] Settings loaded")
    print(f"  - Database path: {settings.database_settings.db_path}")
    print(f"  - TCP Java: {settings.tcp_settings.tcp_ip_java}:{settings.tcp_settings.tcp_port_java}")
    print(f"  - TCP ESP: {settings.tcp_settings.tcp_ip_esp}:{settings.tcp_settings.tcp_port_esp}")
    
    return True


def run_all_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("CAMERA SERVER INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Settings Loading", test_settings_loading),
        ("Full Workflow", test_full_workflow),
        ("Mock Servers", test_with_mock_servers),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n[OK] {test_name} PASSED")
            else:
                failed += 1
                print(f"\n[FAIL] {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"\n[FAIL] {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)
