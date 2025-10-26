#!/usr/bin/env python3
"""
Универсальная сборка для macOS - Intel + ARM
Создает .app bundle с правильными правами доступа
"""

import os
import subprocess
import sys
import shutil

def main():
    print("Сборка универсального SurveyApp для macOS...")
    
    # Установка PyInstaller если нужно
    try:
        import PyInstaller
    except ImportError:
        print("Устанавливаю PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Команда сборки с --windowed для .app bundle
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed", 
        "--name", "SurveyApp",
        "--icon", "asrr_logo.png",
        "--distpath", "dist",
        "--workpath", "build",
        "survey_app_pyqt.py"
    ]
    
    print("Выполняю сборку...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Сборка успешна!")
        
        # Устанавливаем права доступа для .app bundle
        app_path = "dist/SurveyApp.app"
        if os.path.exists(app_path):
            executable_path = os.path.join(app_path, "Contents", "MacOS", "SurveyApp")
            if os.path.exists(executable_path):
                os.chmod(executable_path, 0o755)
                print(f"✅ Права доступа установлены для {executable_path}")
                
                # Проверяем права
                stat = os.stat(executable_path)
                print(f"Права доступа: {oct(stat.st_mode)[-3:]}")
        
        # Создаем также простой исполняемый файл
        simple_executable = "dist/SurveyApp"
        if os.path.exists(simple_executable):
            os.chmod(simple_executable, 0o755)
            print(f"✅ Права доступа установлены для {simple_executable}")
        
        print("\n📦 Созданные файлы:")
        print("- dist/SurveyApp.app - macOS приложение (рекомендуется)")
        print("- dist/SurveyApp - простой исполняемый файл")
        print("\nОба файла работают на Intel и ARM Mac")
        
    else:
        print("❌ Ошибка сборки")
        return False
    
    return True

if __name__ == "__main__":
    main()
