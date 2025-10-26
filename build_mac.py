#!/usr/bin/env python3
"""
Скрипт для сборки macOS приложения SurveyApp
Поддерживает Intel и ARM (M1-M4) процессоры
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Выполнить команду и вернуть результат"""
    print(f"Выполняю: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Ошибка: {result.stderr}")
        return False
    print(f"Успешно: {result.stdout}")
    return True

def install_dependencies():
    """Установить необходимые зависимости"""
    print("Устанавливаю зависимости...")
    
    # Установка PyInstaller
    if not run_command("pip install pyinstaller"):
        return False
    
    # Установка других зависимостей
    if not run_command("pip install -r requirements.txt"):
        return False
    
    return True

def build_universal_binary():
    """Создать универсальный бинарник для Intel и ARM"""
    print("Создаю универсальный бинарник...")
    
    # Создаем папку для сборки
    build_dir = Path("dist")
    build_dir.mkdir(exist_ok=True)
    
    # Команда для создания универсального бинарника
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "SurveyApp",
        "--icon", "public_icon.ico",
        "--add-data", "logo:logo",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
        "survey_app_pyqt.py"
    ]
    
    if not run_command(" ".join(cmd)):
        return False
    
    return True

def create_dmg():
    """Создать DMG файл для установки"""
    print("Создаю DMG файл...")
    
    # Создаем временную папку для DMG
    dmg_dir = Path("dmg_temp")
    if dmg_dir.exists():
        shutil.rmtree(dmg_dir)
    dmg_dir.mkdir()
    
    # Копируем приложение
    app_path = Path("dist/SurveyApp")
    if app_path.exists():
        shutil.copy2(app_path, dmg_dir / "SurveyApp")
    else:
        print("Ошибка: Приложение не найдено в dist/")
        return False
    
    # Создаем DMG
    dmg_name = "SurveyApp-macOS.dmg"
    if Path(dmg_name).exists():
        os.remove(dmg_name)
    
    cmd = f"hdiutil create -volname 'SurveyApp' -srcfolder {dmg_dir} -ov -format UDZO {dmg_name}"
    if not run_command(cmd):
        return False
    
    # Очищаем временную папку
    shutil.rmtree(dmg_dir)
    
    print(f"DMG создан: {dmg_name}")
    return True

def main():
    """Основная функция сборки"""
    print("=== Сборка SurveyApp для macOS ===")
    
    # Проверяем, что мы в правильной директории
    if not Path("survey_app_pyqt.py").exists():
        print("Ошибка: Файл survey_app_pyqt.py не найден")
        print("Запустите скрипт из корневой папки проекта")
        return False
    
    # Устанавливаем зависимости
    if not install_dependencies():
        print("Ошибка при установке зависимостей")
        return False
    
    # Создаем универсальный бинарник
    if not build_universal_binary():
        print("Ошибка при создании бинарника")
        return False
    
    # Создаем DMG
    if not create_dmg():
        print("Ошибка при создании DMG")
        return False
    
    print("\n=== Сборка завершена успешно! ===")
    print("Файлы:")
    print("- dist/SurveyApp - исполняемый файл")
    print("- SurveyApp-macOS.dmg - установочный DMG")
    print("\nПриложение поддерживает Intel и ARM процессоры")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
