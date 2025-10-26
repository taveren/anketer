#!/usr/bin/env python3
"""
Финальный скрипт для создания Universal Binary
Требует Universal Python с python.org
"""

import os
import sys
import subprocess
import platform
import shutil

def find_universal_python():
    """Находим Universal Python"""
    print("🔍 Ищем Universal Python...")
    
    # Возможные пути Universal Python
    possible_paths = [
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
        "/usr/local/bin/python3",
        "/opt/homebrew/bin/python3"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                # Проверяем, universal ли Python
                result = subprocess.run(["file", path], capture_output=True, text=True)
                if "universal binary" in result.stdout.lower():
                    print(f"✅ Найден Universal Python: {path}")
                    return path
                else:
                    print(f"❌ Python не universal: {path}")
            except:
                continue
    
    print("❌ Universal Python не найден!")
    print("📋 Установите Python с https://www.python.org/downloads/")
    return None

def install_dependencies(python_path):
    """Устанавливаем зависимости в Universal Python"""
    print("📦 Устанавливаем зависимости...")
    
    dependencies = ["PyQt6", "PyInstaller"]
    
    for dep in dependencies:
        try:
            print(f"Устанавливаем {dep}...")
            result = subprocess.run([
                python_path, "-m", "pip", "install", dep
            ], check=True, capture_output=True, text=True)
            print(f"✅ {dep} установлен")
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки {dep}: {e}")
            return False
    
    return True

def build_universal_binary(python_path):
    """Собираем Universal Binary"""
    print("🔨 Собираем Universal Binary...")
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("SurveyApp.spec"):
        os.remove("SurveyApp.spec")
    
    # Команда для Universal Binary
    cmd = [
        python_path, "-m", "PyInstaller",
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

def create_readme():
    """Создаем README с инструкциями"""
    readme_content = """# 🍎 SurveyApp для Mac (Universal Binary)

## 📋 Системные требования
- **macOS 10.15+** (Catalina или новее)
- **Intel Mac** или **Apple Silicon Mac** (M1/M2/M3/M4)

## 🚀 Установка

### Автоматическая установка:
```bash
./install.sh
```

### Ручная установка:
```bash
# Копируем приложение
cp -R SurveyApp.app /Applications/

# Запускаем
open /Applications/SurveyApp.app
```

## 🔧 Совместимость

### Apple Silicon Mac (M1/M2/M3/M4):
- ✅ Нативная поддержка
- ✅ Максимальная производительность
- ✅ Автоматический запуск

### Intel Mac:
- ✅ Нативная поддержка
- ✅ Максимальная производительность
- ✅ Автоматический запуск

## 🛠️ Устранение проблем

### Проблема: "App is damaged"
```bash
# Разрешаем запуск
sudo xattr -rd com.apple.quarantine /Applications/SurveyApp.app
```

### Проблема: "Cannot be opened because it is from an unidentified developer"
```bash
# Разрешаем в настройках безопасности
# Системные настройки → Безопасность и конфиденциальность → Разрешить
```

## 📊 Производительность

| Архитектура | Запуск | Производительность |
|-------------|--------|-------------------|
| Apple Silicon | ⚡ Мгновенный | 🚀 Максимальная |
| Intel Mac | ⚡ Мгновенный | 🚀 Максимальная |

## 🔍 Проверка архитектуры

```bash
# Проверяем архитектуру Mac
uname -m

# arm64 = Apple Silicon
# x86_64 = Intel
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте версию macOS: `sw_vers`
2. Проверьте права доступа: `ls -la /Applications/SurveyApp.app`
3. Запустите: `sudo xattr -rd com.apple.quarantine /Applications/SurveyApp.app`
"""
    
    with open("dist/README.md", "w") as f:
        f.write(readme_content)
    print("✅ Создан README")

def main():
    """Главная функция"""
    print("🍎 Создание Universal Binary для SurveyApp")
    print("=" * 60)
    
    # Находим Universal Python
    python_path = find_universal_python()
    if not python_path:
        print("❌ Universal Python не найден!")
        print("📋 Установите Python с https://www.python.org/downloads/")
        return
    
    # Устанавливаем зависимости
    if not install_dependencies(python_path):
        print("❌ Не удалось установить зависимости!")
        return
    
    # Собираем Universal Binary
    if build_universal_binary(python_path):
        if verify_universal_binary():
            create_installer_script()
            create_readme()
            print("\n🎉 Готово!")
            print("📁 Приложение: dist/SurveyApp.app")
            print("📁 Установка: dist/install.sh")
            print("📁 Документация: dist/README.md")
            print("\n💡 Приложение работает на Intel и Apple Silicon!")
        else:
            print("❌ Universal Binary не создан!")
    else:
        print("❌ Не удалось создать Universal Binary!")

if __name__ == "__main__":
    main()
