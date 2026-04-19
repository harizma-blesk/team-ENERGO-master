# 🧪 Quick Testing Guide

## 1️⃣ Fastest Check (30 seconds)

```bash
python quick_check.py
```

This runs basic functionality tests without servers. If it passes, your setup is correct.

## 2️⃣ Full Test Suite (2 minutes)

```bash
python run_tests.py
```

Runs all tests:
- ✓ Database operations
- ✓ Algorithm logic  
- ✓ Mock servers (Java + ESP)
- ✓ Full integration workflow

## 3️⃣ Individual Tests

```bash
# Database only
python tests/test_database.py

# Algorithms only
python tests/test_algorithms.py

# Integration only
python tests/test_integration.py

# Mock servers only
python tests/mock_servers.py
```

## What's Being Tested

| Test | What | Requires |
|------|------|----------|
| `quick_check.py` | Basic setup | Nothing |
| `test_database.py` | SQLite operations | Nothing |
| `test_algorithms.py` | Room booking logic | Nothing |
| `test_integration.py` | Full workflow | Mock servers |
| `mock_servers.py` | TCP communication | Nothing |

## Expected Output

```
✓ Database: connected, tables created
✓ Data: 5 auditories, 3 cameras added
✓ Query: all records retrieved successfully
✓ Booking: room booking logic working
✓ Conflicts: schedule conflicts detected
✓ Mock Java server: listening on 127.0.0.1:2222
✓ Mock ESP server: listening on 127.0.0.1:4444

ALL TESTS PASSED ✓
```

## Requirements

```bash
pip install -r requirements.txt
```

Minimal required:
- PyQt5
- SQLAlchemy  
- Python 3.7+

## Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: sqlalchemy` | `pip install sqlalchemy` |
| `Address already in use` | Change port in `mock_servers.py` |
| `Permission denied` | Check file permissions on database files |
| `No module named settings` | Run from `CameraServer/` directory |

## After Tests Pass

1. **Integrate real servers**: Update `settings.ini`
2. **Add real cameras**: Insert RTSP URLs in database
3. **Connect ESP32**: Update database with real IP
4. **Run full app**: `python Server/main.py`

## Notes

- Tests use **SQLite** (no external database needed)
- Mock servers run on **localhost** 
- All data is **automatically cleaned up**
- Tests are **repeatable** - run multiple times
