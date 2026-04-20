#!/usr/bin/env python3
"""
Camera Monitor Python - Скрипт запуска
Простой способ запуска приложения без установки в систему
"""

import sys
import os
from pathlib import Path

def main():
    """Главная функция запуска"""
    # Определяем пути
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src"

    # Добавляем src в путь
    sys.path.insert(0, str(src_dir))

    # Импортируем и запускаем приложение
    try:
        from src.main import main as app_main
        sys.exit(app_main())
    except ImportError as e:
        print(f"Ошибка импорта: {e}")
        print("Убедитесь что все зависимости установлены: pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nПриложение остановлено пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()