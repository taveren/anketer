#!/usr/bin/env python3
"""
Скрипт для сборки универсального приложения для Mac
Поддерживает Intel и Apple Silicon процессоры
"""

import os
import sys
import subprocess
import platform
import shutil

def check_platform():
    """Проверяем, что мы на macOS"""
    if platform.system() != "Darwin":
        print("❌ Этот скрипт предназначен для macOS!")
        return False
    return True

def check_architecture():
    """Проверяем архитектуру"""
    arch = platform.machine()
    print(f"🔍 Текущая архитектура: {arch}")
    
    if arch == "arm64":
        print("✅ Apple Silicon (M1/M2/M3) - можем собрать универсальное приложение")
    elif arch == "x86_64":
        print("✅ Intel Mac - можем собрать универсальное приложение")
    else:
        print(f"⚠️ Неизвестная архитектура: {arch}")
    
    return True

def build_universal():
    """Собираем универсальное приложение"""
    print("🔨 Собираем универсальное приложение...")
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Команда для универсальной сборки
    cmd = [
        "pyinstaller",
        "--onedir",  # Используем onedir вместо onefile для лучшей совместимости
        "--windowed",
        "--name", "SurveyApp",
        "--icon", "favicon.ico",
        "--target-arch", "universal2",  # Универсальная архитектура
        "survey_app_pyqt.py"
    ]
    
    try:
        print("🚀 Запускаем сборку...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Сборка успешна!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def create_dmg():
    """Создаем DMG файл для распространения"""
    print("📦 Создаем DMG файл...")
    
    app_path = "dist/SurveyApp.app"
    dmg_path = "dist/SurveyApp.dmg"
    
    if not os.path.exists(app_path):
        print("❌ Приложение не найдено!")
        return False
    
    try:
        # Создаем временную папку для DMG
        temp_dir = "dist/temp_dmg"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Копируем приложение
        shutil.copytree(app_path, f"{temp_dir}/SurveyApp.app")
        
        # Создаем DMG
        cmd = [
            "hdiutil", "create",
            "-volname", "SurveyApp",
            "-srcfolder", temp_dir,
            "-ov",
            "-format", "UDZO",
            dmg_path
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ DMG создан!")
        
        # Очищаем временную папку
        shutil.rmtree(temp_dir)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания DMG: {e}")
        return False

def create_installer_script():
    """Создаем скрипт установки"""
    script_content = """#!/bin/bash
echo "🚀 Установка SurveyApp..."

# Проверяем архитектуру
ARCH=$(uname -m)
echo "🔍 Архитектура: $ARCH"

# Копируем приложение
APP_PATH="/Applications/SurveyApp.app"
if [ -d "$APP_PATH" ]; then
    echo "🗑️ Удаляем старую версию..."
    rm -rf "$APP_PATH"
fi

echo "📦 Копируем приложение..."
cp -R "SurveyApp.app" "$APP_PATH"

echo "✅ Установка завершена!"
echo "💡 Запустите приложение из папки Программы"
"""
    
    with open("dist/install.sh", "w") as f:
        f.write(script_content)
    
    # Делаем скрипт исполняемым
    os.chmod("dist/install.sh", 0o755)
    print("✅ Создан скрипт установки")

def main():
    """Главная функция"""
    print("🍎 Сборка универсального SurveyApp для Mac")
    print("=" * 50)
    
    if not check_platform():
        return
    
    if not check_architecture():
        return
    
    if not build_universal():
        return
    
    create_installer_script()
    
    # Пытаемся создать DMG (опционально)
    if input("📦 Создать DMG файл? (y/n): ").lower() == 'y':
        create_dmg()
    
    print("\n🎉 Готово!")
    print("📁 Приложение: dist/SurveyApp.app")
    print("📁 Установка: dist/install.sh")
    if os.path.exists("dist/SurveyApp.dmg"):
        print("📁 DMG: dist/SurveyApp.dmg")
    
    print("\n💡 Для распространения:")
    print("1. Скопируйте SurveyApp.app на любой Mac")
    print("2. Или используйте DMG файл")
    print("3. Приложение работает на Intel и Apple Silicon")

if __name__ == "__main__":
    main()


