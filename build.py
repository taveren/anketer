#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сборки исполняемых файлов системы анкетирования
Поддерживает Windows, macOS и Linux
"""

import os
import sys
import subprocess
import platform
import shutil

def build_executable():
    """Собираем исполняемый файл для текущей ОС"""
    
    print("🔨 Сборка системы анкетирования...")
    print(f"ОС: {platform.system()} {platform.release()}")
    print(f"Архитектура: {platform.machine()}")
    
    # Параметры для PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Один исполняемый файл
        "--windowed",                   # Без консоли (только для Windows/macOS)
        "--name=SurveyApp",             # Имя исполняемого файла
        "--icon=build/icon.ico",        # Иконка (если есть)
        "--add-data=build;build",       # Добавляем папку build
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui", 
        "--hidden-import=PyQt6.QtWidgets",
        "survey_app_pyqt.py"
    ]
    
    # Убираем windowed для Linux (чтобы видеть ошибки)
    if platform.system() == "Linux":
        cmd.remove("--windowed")
    
    # Убираем иконку если файла нет
    if not os.path.exists("build/icon.ico"):
        cmd = [c for c in cmd if not c.startswith("--icon")]
        cmd = [c for c in cmd if not c.startswith("--add-data")]
    
    try:
        print("Выполняем команду:", " ".join(cmd))
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Сборка успешна!")
        
        # Определяем путь к исполняемому файлу
        if platform.system() == "Windows":
            exe_path = "dist/SurveyApp.exe"
        else:
            exe_path = "dist/SurveyApp"
        
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📦 Исполняемый файл: {exe_path}")
            print(f"📏 Размер: {size:.1f} MB")
            
            # Создаем папку для распространения
            dist_dir = f"SurveyApp-{platform.system()}-{platform.machine()}"
            if os.path.exists(dist_dir):
                shutil.rmtree(dist_dir)
            os.makedirs(dist_dir)
            
            # Копируем исполняемый файл
            if platform.system() == "Windows":
                shutil.copy2(exe_path, f"{dist_dir}/SurveyApp.exe")
            else:
                shutil.copy2(exe_path, f"{dist_dir}/SurveyApp")
                # Делаем исполняемым
                os.chmod(f"{dist_dir}/SurveyApp", 0o755)
            
            # Создаем README
            readme_content = f"""# Система анкетирования

## Установка и запуск

### Windows
1. Запустите `SurveyApp.exe`
2. При первом запуске будет создана папка с данными в:
   `%APPDATA%\\ASRR\\SurveyApp\\`

### macOS  
1. Запустите `SurveyApp`
2. При первом запуске будет создана папка с данными в:
   `~/Library/Application Support/ASRR/SurveyApp/`

### Linux
1. Запустите `./SurveyApp`
2. При первом запуске будет создана папка с данными в:
   `~/.local/share/ASRR/SurveyApp/`

## Использование

1. **Создание анкет**: Нажмите "Админ" → введите пароль "admin123" → "Создать анкету"
2. **Прохождение анкет**: Нажмите "СТАРТ" или выберите анкету из списка
3. **Экспорт/импорт**: В админке используйте кнопки "Экспорт данных" и "Импорт данных"

## Файлы данных

Все данные сохраняются в JSON файлах:
- `surveys.json` - анкеты
- `responses.json` - ответы пользователей

Эти файлы можно копировать между компьютерами для синхронизации данных.

## Поддержка

При возникновении проблем проверьте:
1. Права доступа к папке с данными
2. Наличие свободного места на диске
3. Версию операционной системы

---
Собрано: {platform.system()} {platform.release()}
Архитектура: {platform.machine()}
"""
            
            with open(f"{dist_dir}/README.txt", "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            print(f"📁 Папка для распространения: {dist_dir}/")
            print("✅ Готово к распространению!")
            
        else:
            print("❌ Исполняемый файл не найден!")
            
    except subprocess.CalledProcessError as e:
        print("❌ Ошибка сборки:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("❌ PyInstaller не найден. Установите его:")
        print("pip install pyinstaller")
        return False
    
    return True

def clean_build():
    """Очищаем временные файлы сборки"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ Удалена папка: {dir_name}")
    
    import glob
    for pattern in files_to_clean:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"🗑️ Удален файл: {file}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_build()
    else:
        build_executable()
