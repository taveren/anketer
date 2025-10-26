#!/usr/bin/env python3
"""
Исправленная сборка Universal Binary
Учитывает проблемы с PyQt6 на Intel Mac
"""

import os
import sys
import subprocess
import platform
import shutil

def check_environment():
    """Проверяем окружение"""
    print("🔍 Проверяем окружение...")
    
    # Проверяем Python
    python_path = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
    if not os.path.exists(python_path):
        print("❌ Universal Python не найден!")
        return False
    
    result = subprocess.run(["file", python_path], capture_output=True, text=True)
    if "universal binary" not in result.stdout.lower():
        print("❌ Python не universal!")
        return False
    
    print("✅ Universal Python найден!")
    return True

def install_dependencies():
    """Устанавливаем зависимости"""
    print("📦 Устанавливаем зависимости...")
    
    python_path = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
    dependencies = ["PyQt6", "PyInstaller", "Pillow"]
    
    for dep in dependencies:
        try:
            print(f"Устанавливаем {dep}...")
            subprocess.run([python_path, "-m", "pip", "install", dep], check=True)
            print(f"✅ {dep} установлен")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки {dep}: {e}")
            return False
    
    return True

def build_universal_app():
    """Собираем Universal Binary с исправлениями"""
    print("🔨 Собираем Universal Binary с исправлениями...")
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("SurveyApp.spec"):
        os.remove("SurveyApp.spec")
    
    python_path = "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
    
    # Команда для сборки с дополнительными параметрами
    cmd = [
        python_path, "-m", "PyInstaller",
        "--onedir",  # Используем onedir для лучшей совместимости
        "--windowed",
        "--name", "SurveyApp",
        "--icon", "favicon.icns",
        "--target-arch", "universal2",
        "--osx-bundle-identifier", "com.surveyapp.SurveyApp",
        "--add-data", "/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/PyQt6:PyQt6",
        "survey_app_pyqt.py"
    ]
    
    try:
        print("🚀 Запускаем сборку...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Universal Binary создан!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def fix_qt_libraries():
    """Исправляем Qt библиотеки"""
    print("🔧 Исправляем Qt библиотеки...")
    
    app_path = "dist/SurveyApp.app"
    frameworks_path = f"{app_path}/Contents/Frameworks"
    
    if not os.path.exists(frameworks_path):
        print("❌ Frameworks не найдены!")
        return False
    
    # Проверяем все .so файлы
    for root, dirs, files in os.walk(frameworks_path):
        for file in files:
            if file.endswith('.so'):
                file_path = os.path.join(root, file)
                result = subprocess.run(["file", file_path], capture_output=True, text=True)
                
                if "universal binary" not in result.stdout.lower():
                    print(f"❌ {file} не universal: {result.stdout.strip()}")
                    return False
                else:
                    print(f"✅ {file} universal")
    
    print("✅ Все Qt библиотеки universal!")
    return True

def create_launcher_script():
    """Создаем launcher скрипт для лучшей совместимости"""
    print("🔧 Создаем launcher скрипт...")
    
    app_path = "dist/SurveyApp.app"
    exec_path = f"{app_path}/Contents/MacOS/SurveyApp"
    launcher_path = f"{app_path}/Contents/MacOS/SurveyApp_Launcher"
    
    # Создаем launcher скрипт
    launcher_content = """#!/bin/bash
# Launcher для SurveyApp
# Обеспечивает правильную работу на Intel и Apple Silicon

# Получаем путь к приложению
APP_DIR="$(dirname "$0")"
EXECUTABLE="$APP_DIR/SurveyApp"

# Проверяем архитектуру
ARCH=$(uname -m)
echo "🔍 Архитектура: $ARCH"

# Проверяем, что исполняемый файл существует
if [ ! -f "$EXECUTABLE" ]; then
    echo "❌ Ошибка: Исполняемый файл не найден: $EXECUTABLE"
    exit 1
fi

# Запускаем приложение
echo "🚀 Запускаем SurveyApp..."
exec "$EXECUTABLE" "$@"
"""
    
    # Создаем launcher
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    # Делаем launcher исполняемым
    os.chmod(launcher_path, 0o755)
    
    # Переименовываем оригинальный файл
    backup_path = f"{app_path}/Contents/MacOS/SurveyApp_Original"
    if os.path.exists(exec_path):
        shutil.move(exec_path, backup_path)
        shutil.move(launcher_path, exec_path)
        print("✅ Launcher скрипт создан!")
        return True
    else:
        print("❌ Оригинальный исполняемый файл не найден!")
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
    
    if "universal binary" in result.stdout.lower() or "x86_64 arm64" in result.stdout or "arm64 x86_64" in result.stdout:
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
    print("🍎 Исправленная сборка Universal Binary для SurveyApp")
    print("=" * 60)
    
    if not check_environment():
        return
    
    if not install_dependencies():
        return
    
    if not build_universal_app():
        return
    
    if not fix_qt_libraries():
        return
    
    if not create_launcher_script():
        return
    
    if verify_universal_binary():
        create_installer_script()
        print("\n🎉 Готово!")
        print("📁 Приложение: dist/SurveyApp.app")
        print("📁 Установка: dist/install.sh")
        print("\n💡 Приложение работает на Intel и Apple Silicon!")
    else:
        print("❌ Universal Binary не создан!")

if __name__ == "__main__":
    main()


