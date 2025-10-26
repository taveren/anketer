#!/usr/bin/env python3
"""
Скрипт для исправления Qt-фреймворков в приложении
Добавляет недостающие x86_64 версии Qt библиотек
"""

import os
import sys
import subprocess
import shutil
import glob

def find_qt_frameworks():
    """Находим Qt-фреймворки в системе"""
    print("🔍 Ищем Qt-фреймворки в системе...")
    
    # Возможные пути к Qt
    qt_paths = [
        "/usr/local/Cellar/qt6/lib",
        "/opt/homebrew/Cellar/qt6/lib", 
        "/Library/Frameworks/Qt6.framework",
        "/usr/local/lib",
        "/opt/homebrew/lib"
    ]
    
    qt_frameworks = {}
    
    for path in qt_paths:
        if os.path.exists(path):
            print(f"📁 Проверяем: {path}")
            
            # Ищем QtWidgets.framework
            widgets_path = os.path.join(path, "QtWidgets.framework")
            if os.path.exists(widgets_path):
                print(f"✅ Найден QtWidgets: {widgets_path}")
                qt_frameworks["QtWidgets"] = widgets_path
            
            # Ищем другие Qt фреймворки
            for framework in ["QtCore", "QtGui", "QtDBus"]:
                framework_path = os.path.join(path, f"{framework}.framework")
                if os.path.exists(framework_path):
                    print(f"✅ Найден {framework}: {framework_path}")
                    qt_frameworks[framework] = framework_path
    
    return qt_frameworks

def check_qt_architecture(framework_path):
    """Проверяем архитектуру Qt фреймворка"""
    if not os.path.exists(framework_path):
        return False
    
    # Проверяем основной бинарник фреймворка
    binary_path = os.path.join(framework_path, os.path.basename(framework_path).replace(".framework", ""))
    if os.path.exists(binary_path):
        result = subprocess.run(["file", binary_path], capture_output=True, text=True)
        return "universal binary" in result.stdout.lower() or "x86_64" in result.stdout
    
    return False

def copy_qt_frameworks(qt_frameworks, app_path):
    """Копируем Qt-фреймворки в приложение"""
    print("📦 Копируем Qt-фреймворки в приложение...")
    
    frameworks_path = os.path.join(app_path, "Contents", "Frameworks")
    
    if not os.path.exists(frameworks_path):
        os.makedirs(frameworks_path)
    
    for framework_name, framework_path in qt_frameworks.items():
        print(f"📋 Копируем {framework_name}...")
        
        # Проверяем архитектуру
        if not check_qt_architecture(framework_path):
            print(f"⚠️ {framework_name} не universal, пропускаем")
            continue
        
        # Копируем фреймворк
        dest_path = os.path.join(frameworks_path, os.path.basename(framework_path))
        
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        
        shutil.copytree(framework_path, dest_path)
        print(f"✅ {framework_name} скопирован")
    
    return True

def fix_rpath_in_app(app_path):
    """Исправляем rpath в приложении"""
    print("🔧 Исправляем rpath в приложении...")
    
    exec_path = os.path.join(app_path, "Contents", "MacOS", "SurveyApp")
    
    if not os.path.exists(exec_path):
        print("❌ Исполняемый файл не найден!")
        return False
    
    # Добавляем rpath к фреймворкам
    frameworks_path = os.path.join(app_path, "Contents", "Frameworks")
    rpath = f"@executable_path/../Frameworks"
    
    try:
        # Устанавливаем rpath
        subprocess.run([
            "install_name_tool", "-add_rpath", rpath, exec_path
        ], check=True)
        print("✅ rpath добавлен")
        
        # Исправляем пути к Qt библиотекам
        for root, dirs, files in os.walk(frameworks_path):
            for file in files:
                if file.endswith('.so') or file.endswith('.dylib'):
                    file_path = os.path.join(root, file)
                    
                    # Получаем зависимости
                    result = subprocess.run([
                        "otool", "-L", file_path
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Qt' in line and '@rpath' not in line:
                                # Заменяем путь на @rpath
                                old_path = line.strip().split(' ')[0]
                                new_path = f"@rpath/{os.path.basename(old_path)}"
                                
                                subprocess.run([
                                    "install_name_tool", "-change", old_path, new_path, file_path
                                ], check=False)  # Игнорируем ошибки
        
        print("✅ rpath исправлен")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка исправления rpath: {e}")
        return False

def create_qt_launcher():
    """Создаем launcher с правильными путями к Qt"""
    print("🔧 Создаем Qt launcher...")
    
    app_path = "dist/SurveyApp.app"
    exec_path = os.path.join(app_path, "Contents", "MacOS", "SurveyApp")
    launcher_path = os.path.join(app_path, "Contents", "MacOS", "SurveyApp_Qt")
    
    launcher_content = """#!/bin/bash
# Qt Launcher для SurveyApp
# Обеспечивает правильную работу с Qt-фреймворками

# Получаем путь к приложению
APP_DIR="$(dirname "$0")"
EXECUTABLE="$APP_DIR/SurveyApp"

# Устанавливаем переменные окружения для Qt
export QT_PLUGIN_PATH="$APP_DIR/../Frameworks"
export QML2_IMPORT_PATH="$APP_DIR/../Frameworks"

# Проверяем архитектуру
ARCH=$(uname -m)
echo "🔍 Архитектура: $ARCH"

# Проверяем, что исполняемый файл существует
if [ ! -f "$EXECUTABLE" ]; then
    echo "❌ Ошибка: Исполняемый файл не найден: $EXECUTABLE"
    exit 1
fi

# Запускаем приложение
echo "🚀 Запускаем SurveyApp с Qt-фреймворками..."
exec "$EXECUTABLE" "$@"
"""
    
    # Создаем launcher
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    # Делаем launcher исполняемым
    os.chmod(launcher_path, 0o755)
    
    # Заменяем оригинальный файл
    if os.path.exists(exec_path):
        backup_path = f"{exec_path}_Original"
        shutil.move(exec_path, backup_path)
        shutil.move(launcher_path, exec_path)
        print("✅ Qt launcher создан!")
        return True
    else:
        print("❌ Оригинальный исполняемый файл не найден!")
        return False

def main():
    """Главная функция"""
    print("🔧 Исправление Qt-фреймворков для SurveyApp")
    print("=" * 50)
    
    app_path = "dist/SurveyApp.app"
    
    if not os.path.exists(app_path):
        print("❌ Приложение не найдено!")
        print("📋 Сначала соберите приложение: python build_fixed_universal.py")
        return
    
    # Ищем Qt-фреймворки
    qt_frameworks = find_qt_frameworks()
    
    if not qt_frameworks:
        print("❌ Qt-фреймворки не найдены!")
        print("📋 Установите Qt6: brew install qt6")
        return
    
    # Копируем Qt-фреймворки
    if not copy_qt_frameworks(qt_frameworks, app_path):
        return
    
    # Исправляем rpath
    if not fix_rpath_in_app(app_path):
        return
    
    # Создаем Qt launcher
    if not create_qt_launcher():
        return
    
    print("\n🎉 Qt-фреймворки исправлены!")
    print("📁 Приложение: dist/SurveyApp.app")
    print("💡 Теперь должно работать на Intel и Apple Silicon!")

if __name__ == "__main__":
    main()


