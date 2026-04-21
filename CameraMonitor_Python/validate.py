#!/usr/bin/env python3
"""
Phase 7: Final Validation & Runtime Testing
Camera Monitor Python - Application Startup Validator
"""

import sys
import os
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_environment():
    """Validate Python environment and dependencies"""
    logger.info("=" * 60)
    logger.info("PHASE 7: Final Validation & Runtime Testing")
    logger.info("=" * 60)
    
    # Check Python version
    logger.info(f"Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ required")
        return False
    
    # Check required packages
    required_packages = {
        'cv2': 'opencv-python',
        'PyQt6': 'PyQt6',
        'sqlalchemy': 'SQLAlchemy',
        'ultralytics': 'ultralytics',
        'numpy': 'numpy',
        'PIL': 'Pillow'
    }
    
    logger.info("\nChecking required packages:")
    missing = []
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
            logger.info(f"  ✓ {package_name}")
        except ImportError:
            logger.warning(f"  ✗ {package_name} - NOT INSTALLED")
            missing.append(package_name)
    
    if missing:
        logger.error(f"\nMissing packages: {', '.join(missing)}")
        logger.error("Install with: pip install -r requirements.txt")
        return False
    
    return True


def validate_config():
    """Validate configuration file"""
    logger.info("\n" + "=" * 60)
    logger.info("Configuration Validation")
    logger.info("=" * 60)
    
    try:
        from src.core.config import Config
        
        config_path = project_root / "config" / "settings.ini"
        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            return False
        
        logger.info(f"Loading config: {config_path}")
        config = Config(str(config_path))
        
        logger.info("Configuration loaded successfully")
        logger.info(f"  Database: {config.db_path}")
        logger.info(f"  Camera RTSP: {config.camera_rtsp_url}")
        logger.info(f"  YOLO Model: {config.yolo_weights_path}")
        logger.info(f"  UDP Listen Port: {config.udp_listen_port}")
        logger.info(f"  TCP Server: {config.java_server_ip}:{config.java_server_port}")
        
        return True
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False


def validate_core_modules():
    """Validate all core modules"""
    logger.info("\n" + "=" * 60)
    logger.info("Core Modules Validation")
    logger.info("=" * 60)
    
    modules = [
        ('src.core.config', 'Config'),
        ('src.core.camera', 'CameraManager'),
        ('src.core.detector', 'PersonDetector'),
        ('src.core.database', 'DatabaseManager'),
        ('src.core.network', 'NetworkManager'),
    ]
    
    for module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            logger.info(f"  ✓ {class_name} from {module_path}")
        except Exception as e:
            logger.error(f"  ✗ Failed to import {class_name}: {e}")
            return False
    
    return True


def validate_gui_modules():
    """Validate all GUI modules"""
    logger.info("\n" + "=" * 60)
    logger.info("GUI Modules Validation")
    logger.info("=" * 60)
    
    modules = [
        ('src.gui.main_window', 'MainWindow'),
        ('src.gui.camera_window', 'CameraWindow'),
        ('src.gui.request_window', 'RequestWindow'),
        ('src.gui.settings_window', 'SettingsWindow'),
    ]
    
    for module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            logger.info(f"  ✓ {class_name} from {module_path}")
        except Exception as e:
            logger.error(f"  ✗ Failed to import {class_name}: {e}")
            return False
    
    return True


def validate_database():
    """Validate database initialization"""
    logger.info("\n" + "=" * 60)
    logger.info("Database Validation")
    logger.info("=" * 60)
    
    try:
        from src.core.database import DatabaseManager
        from src.core.config import Config
        
        config_path = project_root / "config" / "settings.ini"
        config = Config(str(config_path))
        
        db_path = project_root / config.db_path
        logger.info(f"Initializing database: {db_path}")
        
        db_manager = DatabaseManager(str(db_path))
        db_manager.initialize_database()
        
        logger.info("  ✓ Database initialized successfully")
        
        # Test basic operations
        cameras = db_manager.get_cameras()
        logger.info(f"  ✓ Retrieved {len(cameras)} cameras from database")
        
        rooms = db_manager.get_all_rooms()
        logger.info(f"  ✓ Retrieved {len(rooms)} rooms from database")
        
        return True
    except Exception as e:
        logger.error(f"Database validation failed: {e}")
        return False


def validate_network():
    """Validate network components"""
    logger.info("\n" + "=" * 60)
    logger.info("Network Components Validation")
    logger.info("=" * 60)
    
    try:
        from src.core.network import NetworkManager, NetworkConfig
        from src.core.config import Config
        
        config_path = project_root / "config" / "settings.ini"
        config = Config(str(config_path))
        
        logger.info("Creating NetworkManager...")
        network_manager = NetworkManager(config)
        
        logger.info("  ✓ UDP Server initialized")
        logger.info("  ✓ UDP Client initialized")
        logger.info("  ✓ TCP Client initialized")
        
        logger.info("  ✓ Network components validated")
        
        return True
    except Exception as e:
        logger.error(f"Network validation failed: {e}")
        return False


def run_all_validations():
    """Run all validation checks"""
    checks = [
        ("Environment", validate_environment),
        ("Configuration", validate_config),
        ("Core Modules", validate_core_modules),
        ("GUI Modules", validate_gui_modules),
        ("Database", validate_database),
        ("Network", validate_network),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            logger.error(f"Unexpected error during {name} validation: {e}")
            results[name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{name:.<50} {status}")
    
    logger.info("=" * 60)
    logger.info(f"Total: {passed}/{total} checks passed")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("\n✓ All validations passed! Application is ready to run.")
        return True
    else:
        logger.error(f"\n✗ {total - passed} validation(s) failed. Fix issues before running.")
        return False


if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)
