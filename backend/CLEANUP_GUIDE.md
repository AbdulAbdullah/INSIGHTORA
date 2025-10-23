# 🧹 File Cleanup Guide - Smart BI Platform Backend

## 🟢 FILES TO KEEP (Essential for Development)

### ✅ Shell Scripts (KEEP)
- **`simple_setup.sh`** - ⭐ Main setup script (automated, works perfectly)
- **`start_simple.sh`** - ⭐ Simple server start (minimal dependencies)
- **`start.sh`** - Full server start (for production features)
- **`start.bat`** - Windows batch equivalent

### ✅ Requirements Files (KEEP)
- **`requirements_essential.txt`** - ⭐ Minimal dependencies (works great)

### ✅ Documentation (KEEP)
- **`DEVELOPER_GUIDE.md`** - ⭐ Complete developer guide
- **`README.md`** - Updated project overview
- **`SETUP.md`** - Detailed setup instructions

### ✅ Core Files (KEEP)
- **`main_simple.py`** - ⭐ Minimal server (for testing)
- **`app/`** - Main application code
- **`.env`** & **`.env.example`** - Configuration
- **`alembic/`** & **`alembic.ini`** - Database migrations

---

## 🔴 FILES TO REMOVE (Outdated/Duplicates)

### ❌ Outdated Shell Scripts (REMOVE)
- **`setup.sh`** - Replaced by `simple_setup.sh`
- **`quick_start.sh`** - Replaced by `simple_setup.sh`
- **`start_dev.sh`** - Redundant
- **`create_migration.sh`** - Can use alembic directly

### ❌ Outdated Requirements (REMOVE)
- **`requirements.txt`** - Has dependency conflicts
- **`requirements_minimal.txt`** - Duplicate of essential

### ❌ Other Files to Clean (REMOVE)
- **`test_config.py`** - Outdated test file
- **`test_docs.py`** - Outdated test file
- **`=0.29.0`** - Weird file artifact
- **`__pycache__/`** - Python cache (auto-generated)

---

## 🎯 RECOMMENDED WORKFLOW

### For New Developers:
```bash
# 1. Use the automated setup
./simple_setup.sh

# 2. Start in simple mode
./start_simple.sh

# 3. Visit API docs
open http://localhost:8000/docs
```

### For Production Features:
```bash
# 1. Use the full server (after fixing remaining issues)
./start.sh
```

---

## 📋 File Usage Summary

| File | Status | Purpose |
|------|--------|---------|
| `simple_setup.sh` | ⭐ **PRIMARY** | One-command setup |
| `start_simple.sh` | ⭐ **PRIMARY** | Simple server start |
| `requirements_essential.txt` | ⭐ **PRIMARY** | Minimal dependencies |
| `main_simple.py` | ⭐ **PRIMARY** | Test server |
| `DEVELOPER_GUIDE.md` | ⭐ **PRIMARY** | Complete guide |
| `start.sh` | ⚠️ **SECONDARY** | Full server (needs fixes) |
| `requirements.txt` | ❌ **REMOVE** | Has conflicts |
| `setup.sh` | ❌ **REMOVE** | Outdated |
| `quick_start.sh` | ❌ **REMOVE** | Redundant |
