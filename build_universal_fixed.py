#!/usr/bin/env python3
"""
Скрипт для создания универсального приложения для Mac
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

def build_universal_app():
    """Собираем универсальное приложение"""
    print("🔨 Собираем универсальное приложение...")
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("SurveyApp.spec"):
        os.remove("SurveyApp.spec")
    
    # Команда для универсальной сборки
    cmd = [
        "pyinstaller",
        "--onedir",
        "--windowed",
        "--name", "SurveyApp",
        "--icon", "favicon.ico",
        "--target-arch", "universal2",
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

def create_universal_binary():
    """Создаем универсальный бинарник вручную"""
    print("🔧 Создаем универсальный бинарник...")
    
    app_path = "dist/SurveyApp.app"
    if not os.path.exists(app_path):
        print("❌ Приложение не найдено!")
        return False
    
    # Путь к исполняемому файлу
    exec_path = f"{app_path}/Contents/MacOS/SurveyApp"
    
    if not os.path.exists(exec_path):
        print("❌ Исполняемый файл не найден!")
        return False
    
    # Проверяем текущую архитектуру
    result = subprocess.run(["file", exec_path], capture_output=True, text=True)
    print(f"🔍 Текущая архитектура: {result.stdout.strip()}")
    
    # Если уже универсальный, ничего не делаем
    if "universal binary" in result.stdout.lower():
        print("✅ Уже универсальный бинарник!")
        return True
    
    # Создаем универсальный бинарник
    try:
        # Создаем копию для arm64
        arm64_path = f"{exec_path}.arm64"
        shutil.copy2(exec_path, arm64_path)
        
        # Создаем копию для x86_64 (через Rosetta)
        x86_64_path = f"{exec_path}.x86_64"
        
        # Запускаем через Rosetta для создания x86_64 версии
        rosetta_cmd = [
            "arch", "-x86_64", "python", "-m", "PyInstaller",
            "--onedir",
            "--windowed", 
            "--name", "SurveyApp_x86",
            "--icon", "favicon.ico",
            "survey_app_pyqt.py"
        ]
        
        print("🔄 Создаем x86_64 версию через Rosetta...")
        result = subprocess.run(rosetta_cmd, check=True, capture_output=True, text=True)
        
        # Копируем x86_64 версию
        x86_exec_path = "dist/SurveyApp_x86/SurveyApp_x86"
        if os.path.exists(x86_exec_path):
            shutil.copy2(x86_exec_path, x86_64_path)
            print("✅ x86_64 версия создана!")
        else:
            print("❌ Не удалось создать x86_64 версию")
            return False
        
        # Создаем универсальный бинарник
        print("🔗 Создаем универсальный бинарник...")
        lipo_cmd = [
            "lipo", "-create",
            "-arch", "arm64", arm64_path,
            "-arch", "x86_64", x86_64_path,
            "-output", exec_path
        ]
        
        result = subprocess.run(lipo_cmd, check=True, capture_output=True, text=True)
        print("✅ Универсальный бинарник создан!")
        
        # Очищаем временные файлы
        os.remove(arm64_path)
        os.remove(x86_64_path)
        shutil.rmtree("dist/SurveyApp_x86", ignore_errors=True)
        shutil.rmtree("build", ignore_errors=True)
        if os.path.exists("SurveyApp_x86.spec"):
            os.remove("SurveyApp_x86.spec")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка создания универсального бинарника: {e}")
        return False

def verify_universal_binary():
    """Проверяем универсальный бинарник"""
    print("🔍 Проверяем универсальный бинарник...")
    
    app_path = "dist/SurveyApp.app/Contents/MacOS/SurveyApp"
    
    if not os.path.exists(app_path):
        print("❌ Приложение не найдено!")
        return False
    
    # Проверяем архитектуру
    result = subprocess.run(["file", app_path], capture_output=True, text=True)
    print(f"🔍 Архитектура: {result.stdout.strip()}")
    
    # Проверяем с помощью lipo
    result = subprocess.run(["lipo", "-info", app_path], capture_output=True, text=True)
    print(f"🔍 Lipo info: {result.stdout.strip()}")
    
    if "universal binary" in result.stdout.lower() or "arm64 x86_64" in result.stdout:
        print("✅ Универсальный бинарник создан успешно!")
        return True
    else:
        print("❌ Универсальный бинарник не создан!")
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
    echo "✅ Apple Silicon Mac (M1/M2/M3) - нативная поддержка"
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
    print("🍎 Создание универсального SurveyApp для Mac")
    print("=" * 60)
    
    if not check_platform():
        return
    
    # Сначала пытаемся стандартную сборку
    if build_universal_app():
        if verify_universal_binary():
            create_installer_script()
            print("\n🎉 Готово!")
            print("📁 Приложение: dist/SurveyApp.app")
            print("📁 Установка: dist/install.sh")
            print("\n💡 Приложение работает на Intel и Apple Silicon Mac!")
            return
    
    # Если не получилось, создаем вручную
    print("\n🔧 Стандартная сборка не удалась, создаем вручную...")
    
    if create_universal_binary():
        if verify_universal_binary():
            create_installer_script()
            print("\n🎉 Готово!")
            print("📁 Приложение: dist/SurveyApp.app")
            print("📁 Установка: dist/install.sh")
            print("\n💡 Приложение работает на Intel и Apple Silicon Mac!")
        else:
            print("❌ Не удалось создать универсальный бинарник")
    else:
        print("❌ Не удалось создать универсальное приложение")

if __name__ == "__main__":
    main()


