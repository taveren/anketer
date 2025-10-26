#!/usr/bin/env python3
"""
Скрипт для исправления PyQt6 Universal Binary
Пересобирает PyQt6 с правильными архитектурами
"""

import os
import sys
import subprocess
import shutil

def check_pyqt6_architecture():
    """Проверяем архитектуру PyQt6"""
    print("🔍 Проверяем архитектуру PyQt6...")
    
    pyqt6_path = "dist/SurveyApp.app/Contents/Frameworks/PyQt6"
    if not os.path.exists(pyqt6_path):
        print("❌ PyQt6 не найден!")
        return False
    
    # Проверяем основные библиотеки
    libs = ["QtWidgets.abi3.so", "QtCore.abi3.so", "QtGui.abi3.so"]
    
    for lib in libs:
        lib_path = os.path.join(pyqt6_path, lib)
        if os.path.exists(lib_path):
            result = subprocess.run(["file", lib_path], capture_output=True, text=True)
            print(f"📁 {lib}: {result.stdout.strip()}")
            
            # Проверяем, universal ли
            if "universal binary" not in result.stdout.lower():
                print(f"❌ {lib} не universal!")
                return False
        else:
            print(f"❌ {lib} не найден!")
            return False
    
    print("✅ PyQt6 библиотеки universal!")
    return True

def reinstall_pyqt6_universal():
    """Переустанавливаем PyQt6 как universal"""
    print("🔄 Переустанавливаем PyQt6 как universal...")
    
    # Удаляем старый PyQt6
    subprocess.run(["/Library/Frameworks/Python.framework/Versions/3.12/bin/python3", "-m", "pip", "uninstall", "PyQt6", "-y"])
    
    # Устанавливаем заново
    try:
        result = subprocess.run([
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3", "-m", "pip", "install", "PyQt6"
        ], check=True, capture_output=True, text=True)
        print("✅ PyQt6 переустановлен!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка переустановки PyQt6: {e}")
        return False

def rebuild_with_universal_pyqt6():
    """Пересобираем приложение с universal PyQt6"""
    print("🔨 Пересобираем приложение...")
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("SurveyApp.spec"):
        os.remove("SurveyApp.spec")
    
    # Команда для сборки
    cmd = [
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3", "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name", "SurveyApp",
        "--icon", "favicon.icns",
        "--target-arch", "universal2",
        "survey_app_pyqt.py"
    ]
    
    try:
        print("🚀 Запускаем сборку...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Приложение пересобрано!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def create_alternative_solution():
    """Создаем альтернативное решение - отдельные версии"""
    print("🔧 Создаем альтернативное решение...")
    
    # Собираем ARM64 версию
    print("📱 Собираем ARM64 версию...")
    cmd_arm64 = [
        "python3", "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name", "SurveyApp_ARM64",
        "--icon", "favicon.icns",
        "survey_app_pyqt.py"
    ]
    
    try:
        subprocess.run(cmd_arm64, check=True)
        print("✅ ARM64 версия создана!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки ARM64: {e}")
        return False
    
    # Собираем Intel версию через Rosetta
    print("💻 Собираем Intel версию...")
    cmd_intel = [
        "arch", "-x86_64", "python3", "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name", "SurveyApp_Intel",
        "--icon", "favicon.icns",
        "survey_app_pyqt.py"
    ]
    
    try:
        subprocess.run(cmd_intel, check=True)
        print("✅ Intel версия создана!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки Intel: {e}")
        return False
    
    # Создаем универсальное приложение
    print("🔗 Создаем универсальное приложение...")
    
    # Копируем ARM64 как основу
    if os.path.exists("dist/SurveyApp.app"):
        shutil.rmtree("dist/SurveyApp.app")
    
    shutil.copytree("dist/SurveyApp_ARM64.app", "dist/SurveyApp.app")
    
    # Заменяем исполняемый файл на универсальный
    intel_exec = "dist/SurveyApp_Intel.app/Contents/MacOS/SurveyApp_Intel"
    arm64_exec = "dist/SurveyApp_ARM64.app/Contents/MacOS/SurveyApp_ARM64"
    universal_exec = "dist/SurveyApp.app/Contents/MacOS/SurveyApp"
    
    if os.path.exists(intel_exec) and os.path.exists(arm64_exec):
        try:
            subprocess.run([
                "lipo", "-create",
                "-arch", "x86_64", intel_exec,
                "-arch", "arm64", arm64_exec,
                "-output", universal_exec
            ], check=True)
            print("✅ Универсальный бинарник создан!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка создания универсального бинарника: {e}")
            return False
    
    # Очищаем временные файлы
    shutil.rmtree("dist/SurveyApp_ARM64.app", ignore_errors=True)
    shutil.rmtree("dist/SurveyApp_Intel.app", ignore_errors=True)
    
    return True

def main():
    """Главная функция"""
    print("🔧 Исправление PyQt6 Universal Binary")
    print("=" * 50)
    
    # Проверяем текущее состояние
    if not check_pyqt6_architecture():
        print("❌ PyQt6 не universal, исправляем...")
        
        # Переустанавливаем PyQt6
        if not reinstall_pyqt6_universal():
            print("❌ Не удалось переустановить PyQt6!")
            return
        
        # Пересобираем приложение
        if not rebuild_with_universal_pyqt6():
            print("❌ Не удалось пересобрать приложение!")
            return
        
        # Проверяем результат
        if not check_pyqt6_architecture():
            print("❌ PyQt6 все еще не universal, используем альтернативное решение...")
            if not create_alternative_solution():
                print("❌ Альтернативное решение не сработало!")
                return
    
    print("✅ PyQt6 Universal Binary исправлен!")
    print("📁 Приложение: dist/SurveyApp.app")
    print("💡 Теперь должно работать на Intel и Apple Silicon!")

if __name__ == "__main__":
    main()


