#!/usr/bin/env python3
"""
Скрипт для создания Intel версии приложения
Использует Rosetta 2 для эмуляции Intel на Apple Silicon
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

def build_intel_version():
    """Собираем Intel версию через Rosetta 2"""
    print("🔨 Собираем Intel версию через Rosetta 2...")
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("SurveyApp.spec"):
        os.remove("SurveyApp.spec")
    
    # Команда для Intel версии через Rosetta 2
    cmd = [
        "arch", "-x86_64", "python3", "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name", "SurveyApp_Intel",
        "--icon", "favicon.ico",
        "survey_app_pyqt.py"
    ]
    
    try:
        print("🚀 Запускаем сборку Intel версии...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Intel версия создана!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки Intel версии: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def build_arm64_version():
    """Собираем ARM64 версию"""
    print("🔨 Собираем ARM64 версию...")
    
    # Команда для ARM64 версии
    cmd = [
        "python3", "-m", "PyInstaller",
        "--onedir",
        "--windowed",
        "--name", "SurveyApp_ARM64",
        "--icon", "favicon.ico",
        "survey_app_pyqt.py"
    ]
    
    try:
        print("🚀 Запускаем сборку ARM64 версии...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ ARM64 версия создана!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка сборки ARM64 версии: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def create_universal_app():
    """Создаем универсальное приложение из двух версий"""
    print("🔗 Создаем универсальное приложение...")
    
    intel_app = "dist/SurveyApp_Intel.app"
    arm64_app = "dist/SurveyApp_ARM64.app"
    universal_app = "dist/SurveyApp.app"
    
    if not os.path.exists(intel_app) or not os.path.exists(arm64_app):
        print("❌ Не найдены обе версии приложения!")
        return False
    
    # Создаем универсальное приложение
    if os.path.exists(universal_app):
        shutil.rmtree(universal_app)
    
    # Копируем ARM64 версию как основу
    shutil.copytree(arm64_app, universal_app)
    
    # Заменяем исполняемый файл на универсальный
    intel_exec = f"{intel_app}/Contents/MacOS/SurveyApp_Intel"
    arm64_exec = f"{arm64_app}/Contents/MacOS/SurveyApp_ARM64"
    universal_exec = f"{universal_app}/Contents/MacOS/SurveyApp"
    
    if os.path.exists(intel_exec) and os.path.exists(arm64_exec):
        try:
            # Создаем универсальный бинарник
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
    shutil.rmtree(intel_app, ignore_errors=True)
    shutil.rmtree(arm64_app, ignore_errors=True)
    
    return True

def verify_universal_binary():
    """Проверяем универсальный бинарник"""
    print("🔍 Проверяем универсальный бинарник...")
    
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
        print("✅ Универсальный бинарник создан успешно!")
        print("🎉 Приложение будет работать на Intel и Apple Silicon!")
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
    
    if not check_platform():
        return
    
    # Собираем ARM64 версию
    if not build_arm64_version():
        print("❌ Не удалось собрать ARM64 версию!")
        return
    
    # Собираем Intel версию через Rosetta 2
    if not build_intel_version():
        print("❌ Не удалось собрать Intel версию!")
        return
    
    # Создаем универсальное приложение
    if not create_universal_app():
        print("❌ Не удалось создать универсальное приложение!")
        return
    
    # Проверяем результат
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

if __name__ == "__main__":
    main()


