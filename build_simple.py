#!/usr/bin/env python3
"""
Простая сборка для macOS - один исполняемый файл
"""

import os
import subprocess
import sys

def main():
    print("Сборка SurveyApp для macOS...")
    
    # Установка PyInstaller если нужно
    try:
        import PyInstaller
    except ImportError:
        print("Устанавливаю PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Команда сборки
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name", "SurveyApp",
        "survey_app_pyqt.py"
    ]
    
    print("Выполняю сборку...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Сборка успешна!")
        
        # Устанавливаем права доступа для .app bundle
        import os
        app_path = "dist/SurveyApp.app"
        if os.path.exists(app_path):
            executable_path = os.path.join(app_path, "Contents", "MacOS", "SurveyApp")
            if os.path.exists(executable_path):
                os.chmod(executable_path, 0o755)
                print(f"✅ Права доступа установлены для {executable_path}")
        
        print("Файл: dist/SurveyApp")
        print("Этот файл работает на Intel и ARM Mac")
    else:
        print("❌ Ошибка сборки")
        return False
    
    return True

if __name__ == "__main__":
    main()
