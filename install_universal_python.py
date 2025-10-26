#!/usr/bin/env python3
"""
Скрипт для установки Universal Python и создания Universal Binary
"""

import os
import sys
import subprocess
import platform
import shutil

def check_current_python():
    """Проверяем текущий Python"""
    print("🔍 Проверяем текущий Python...")
    
    arch = platform.machine()
    print(f"Архитектура: {arch}")
    
    python_path = sys.executable
    print(f"Python путь: {python_path}")
    
    # Проверяем, universal ли Python
    try:
        result = subprocess.run(["file", python_path], capture_output=True, text=True)
        print(f"Тип Python: {result.stdout.strip()}")
        
        if "universal binary" in result.stdout.lower():
            print("✅ Universal Python уже установлен!")
            return True
        else:
            print("❌ Python только для arm64, нужен Universal")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

def install_universal_python():
    """Устанавливаем Universal Python"""
    print("📥 Устанавливаем Universal Python...")
    
    # Проверяем, есть ли уже Universal Python
    universal_paths = [
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
        "/usr/local/bin/python3"
    ]
    
    for path in universal_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run(["file", path], capture_output=True, text=True)
                if "universal binary" in result.stdout.lower():
                    print(f"✅ Найден Universal Python: {path}")
                    return path
            except:
                continue
    
    print("❌ Universal Python не найден!")
    print("📋 Инструкции по установке:")
    print("1. Скачайте Python с https://www.python.org/downloads/")
    print("2. Выберите версию 3.11 или 3.12")
    print("3. Установите .pkg файл")
    print("4. Python будет в /Library/Frameworks/Python.framework/")
    
    return None

def create_universal_build():
    """Создаем Universal Binary"""
    print("🔨 Создаем Universal Binary...")
    
    # Находим Universal Python
    universal_python = install_universal_python()
    if not universal_python:
        print("❌ Universal Python не найден!")
        return False
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Команда для Universal Binary
    cmd = [
        universal_python, "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name", "SurveyApp",
        "--icon", "favicon.ico",
        "--target-arch", "universal2",
        "survey_app_pyqt.py"
    ]
    
    try:
        print("🚀 Запускаем сборку Universal Binary...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Universal Binary создан!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def verify_universal_binary():
    """Проверяем Universal Binary"""
    print("🔍 Проверяем Universal Binary...")
    
    app_path = "dist/SurveyApp.app/Contents/MacOS/SurveyApp"
    
    if not os.path.exists(app_path):
        print("❌ Приложение не найдено!")
        return False
    
    # Проверяем архитектуру
    result = subprocess.run(["file", app_path], capture_output=True, text=True)
    print(f"Тип приложения: {result.stdout.strip()}")
    
    # Проверяем с помощью lipo
    result = subprocess.run(["lipo", "-info", app_path], capture_output=True, text=True)
    print(f"Архитектуры: {result.stdout.strip()}")
    
    if "universal binary" in result.stdout.lower() or "arm64 x86_64" in result.stdout:
        print("✅ Universal Binary создан успешно!")
        print("🎉 Приложение будет работать на Intel и Apple Silicon!")
        return True
    else:
        print("❌ Universal Binary не создан!")
        return False

def create_installer_script():
    """Создаем скрипт установки"""
    script_content = """#!/bin/bash
echo "🚀 Установка SurveyApp для Mac (Intel + Apple Silicon)"
echo "=================================================="

# Проверяем архитектуру
ARCH=$(uname -m)
echo "🔍 Ваша архитектура: $ARCH"

if [[ "$ARCH" == "arm64" ]]; then
    echo "✅ Apple Silicon Mac (M1/M2/M3/M4) - нативная поддержка"
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "✅ Intel Mac - нативная поддержка"
else
    echo "⚠️ Неизвестная архитектура: $ARCH"
fi

# Копируем приложение
APP_PATH="/Applications/SurveyApp.app"
if [ -d "$APP_PATH" ]; then
    echo "🗑️ Удаляем старую версию..."
    rm -rf "$APP_PATH"
fi

echo "📦 Копируем приложение..."
cp -R "SurveyApp.app" "$APP_PATH"

echo "✅ Установка завершена!"
echo ""
echo "💡 Инструкции по запуску:"
echo "1. Откройте папку 'Программы' в Finder"
echo "2. Найдите 'SurveyApp' и запустите"
echo "3. При первом запуске macOS может запросить разрешение"
echo ""
echo "🔧 Если приложение не запускается:"
echo "1. Разрешите в настройках безопасности"
echo "2. Или запустите: sudo xattr -rd com.apple.quarantine /Applications/SurveyApp.app"
"""
    
    with open("dist/install.sh", "w") as f:
        f.write(script_content)
    
    # Делаем скрипт исполняемым
    os.chmod("dist/install.sh", 0o755)
    print("✅ Создан скрипт установки")

def main():
    """Главная функция"""
    print("🍎 Создание Universal Binary для SurveyApp")
    print("=" * 60)
    
    # Проверяем текущий Python
    if check_current_python():
        print("✅ Universal Python уже установлен!")
    else:
        print("❌ Нужен Universal Python")
        universal_python = install_universal_python()
        if not universal_python:
            print("❌ Не удалось найти Universal Python!")
            print("📋 Установите Python с https://www.python.org/downloads/")
            return
    
    # Создаем Universal Binary
    if create_universal_build():
        if verify_universal_binary():
            create_installer_script()
            print("\n🎉 Готово!")
            print("📁 Приложение: dist/SurveyApp.app")
            print("📁 Установка: dist/install.sh")
            print("\n💡 Приложение работает на Intel и Apple Silicon!")
        else:
            print("❌ Universal Binary не создан!")
    else:
        print("❌ Не удалось создать Universal Binary!")

if __name__ == "__main__":
    main()


