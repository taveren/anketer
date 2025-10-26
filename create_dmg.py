#!/usr/bin/env python3
"""
Создание DMG файла для распространения
"""

import os
import subprocess
import shutil

def create_dmg():
    """Создать DMG файл"""
    print("Создание DMG файла...")
    
    # Проверяем наличие .app
    app_path = "dist/SurveyApp.app"
    if not os.path.exists(app_path):
        print("❌ Ошибка: SurveyApp.app не найден")
        return False
    
    # Создаем временную папку для DMG
    dmg_dir = "dmg_temp"
    if os.path.exists(dmg_dir):
        shutil.rmtree(dmg_dir)
    os.makedirs(dmg_dir)
    
    # Копируем .app в временную папку
    shutil.copytree(app_path, os.path.join(dmg_dir, "SurveyApp.app"))
    
    # Создаем символическую ссылку на Applications
    os.symlink("/Applications", os.path.join(dmg_dir, "Applications"))
    
    # Создаем DMG
    dmg_name = "SurveyApp-macOS.dmg"
    if os.path.exists(dmg_name):
        os.remove(dmg_name)
    
    cmd = f"hdiutil create -volname 'SurveyApp' -srcfolder {dmg_dir} -ov -format UDZO {dmg_name}"
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print(f"✅ DMG создан: {dmg_name}")
        
        # Очищаем временную папку
        shutil.rmtree(dmg_dir)
        
        # Показываем размер
        size = os.path.getsize(dmg_name) / (1024 * 1024)
        print(f"Размер DMG: {size:.1f} MB")
        
        return True
    else:
        print("❌ Ошибка создания DMG")
        return False

if __name__ == "__main__":
    create_dmg()
