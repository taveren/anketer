#!/usr/bin/env python3
"""
Скрипт для сборки приложения под Windows
Использование: python build_windows.py
"""

import os
import sys
import subprocess
import platform

def check_platform():
    """Проверяем платформу"""
    if platform.system() != "Windows":
        print("❌ Этот скрипт предназначен для Windows!")
        print("💡 Для сборки под Windows с macOS используйте виртуальную машину")
        return False
    return True

def check_dependencies():
    """Проверяем зависимости"""
    print("🔍 Проверяем зависимости...")
    
    try:
        import PyQt6
        print("✅ PyQt6 установлен")
    except ImportError:
        print("❌ PyQt6 не найден. Установите: pip install PyQt6")
        return False
    
    try:
        import PyInstaller
        print("✅ PyInstaller установлен")
    except ImportError:
        print("❌ PyInstaller не найден. Установите: pip install PyInstaller")
        return False
    
    try:
        import PIL
        print("✅ Pillow установлен")
    except ImportError:
        print("❌ Pillow не найден. Установите: pip install Pillow")
        return False
    
    return True

def build_application():
    """Собираем приложение"""
    print("🔨 Собираем приложение...")
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        import shutil
        shutil.rmtree("dist")
    if os.path.exists("build"):
        import shutil
        shutil.rmtree("build")
    
    # Команда сборки для Windows
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name", "SurveyApp",
        "--icon", "favicon.ico",
        "--add-data", "favicon.ico;.",
        "survey_app_pyqt.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Сборка успешна!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def create_installer():
    """Создаем установщик (опционально)"""
    print("📦 Создаем установщик...")
    
    # Простой bat файл для запуска
    bat_content = """@echo off
echo Запуск SurveyApp...
SurveyApp.exe
pause
"""
    
    with open("dist/run_survey_app.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)
    
    print("✅ Создан run_survey_app.bat")

def main():
    """Главная функция"""
    print("🚀 Сборка SurveyApp для Windows")
    print("=" * 40)
    
    if not check_platform():
        return
    
    if not check_dependencies():
        print("\n💡 Установите зависимости:")
        print("pip install PyQt6 PyInstaller Pillow")
        return
    
    if not build_application():
        return
    
    create_installer()
    
    print("\n🎉 Готово!")
    print("📁 Приложение: dist/SurveyApp.exe")
    print("📁 Запуск: dist/run_survey_app.bat")
    print("\n💡 Для распространения:")
    print("1. Скопируйте папку dist/")
    print("2. Запустите SurveyApp.exe")

if __name__ == "__main__":
    main()
