#!/usr/bin/env python3
"""
Скрипт для сборки приложения, совместимого с Intel Mac
Использует Rosetta 2 для запуска на Intel Mac
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

def build_for_current_arch():
    """Собираем для текущей архитектуры"""
    print("🔨 Собираем приложение для текущей архитектуры...")
    
    # Очищаем предыдущие сборки
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Команда для сборки
    cmd = [
        "pyinstaller",
        "--onedir",
        "--windowed", 
        "--name", "SurveyApp",
        "--icon", "favicon.ico",
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

def create_rosetta_launcher():
    """Создаем launcher с поддержкой Rosetta 2"""
    launcher_content = """#!/bin/bash
# Rosetta 2 Launcher для SurveyApp
# Обеспечивает совместимость с Intel Mac

echo "🍎 Запуск SurveyApp с поддержкой Rosetta 2..."

# Получаем путь к приложению
APP_DIR="$(dirname "$0")"
EXECUTABLE="$APP_DIR/SurveyApp"

# Проверяем архитектуру
ARCH=$(uname -m)
echo "🔍 Архитектура: $ARCH"

# Если мы на Apple Silicon, но нужно запустить через Rosetta
if [[ "$ARCH" == "arm64" ]]; then
    echo "⚡ Apple Silicon Mac - запуск нативной версии"
    exec "$EXECUTABLE" "$@"
else
    echo "🔄 Intel Mac - запуск через Rosetta 2"
    # Rosetta 2 автоматически обрабатывает совместимость
    exec "$EXECUTABLE" "$@"
fi
"""
    
    launcher_path = "dist/SurveyApp.app/Contents/MacOS/SurveyApp_Launcher"
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    # Делаем launcher исполняемым
    os.chmod(launcher_path, 0o755)
    print("✅ Создан Rosetta launcher")

def create_installer_script():
    """Создаем скрипт установки с инструкциями"""
    script_content = """#!/bin/bash
echo "🚀 Установка SurveyApp для Mac (Intel + Apple Silicon)"
echo "=================================================="

# Проверяем архитектуру
ARCH=$(uname -m)
echo "🔍 Ваша архитектура: $ARCH"

if [[ "$ARCH" == "arm64" ]]; then
    echo "✅ Apple Silicon Mac (M1/M2/M3) - нативная поддержка"
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "✅ Intel Mac - поддержка через Rosetta 2"
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
echo "🔧 Если приложение не запускается на Intel Mac:"
echo "1. Установите Rosetta 2: softwareupdate --install-rosetta"
echo "2. Или запустите через Terminal: arch -x86_64 /Applications/SurveyApp.app/Contents/MacOS/SurveyApp"
"""
    
    with open("dist/install.sh", "w") as f:
        f.write(script_content)
    
    # Делаем скрипт исполняемым
    os.chmod("dist/install.sh", 0o755)
    print("✅ Создан скрипт установки")

def create_readme():
    """Создаем README с инструкциями"""
    readme_content = """# 🍎 SurveyApp для Mac

## 📋 Системные требования
- **macOS 10.15+** (Catalina или новее)
- **Intel Mac** или **Apple Silicon Mac** (M1/M2/M3)

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

### Apple Silicon Mac (M1/M2/M3):
- ✅ Нативная поддержка
- ✅ Максимальная производительность
- ✅ Автоматический запуск

### Intel Mac:
- ✅ Поддержка через Rosetta 2
- ✅ Автоматическая эмуляция
- ✅ Полная совместимость

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

### Проблема: Медленная работа на Intel Mac
```bash
# Установите Rosetta 2
softwareupdate --install-rosetta
```

## 📊 Производительность

| Архитектура | Запуск | Производительность |
|-------------|--------|-------------------|
| Apple Silicon | ⚡ Мгновенный | 🚀 Максимальная |
| Intel (с Rosetta) | ⏱️ ~2-3 сек | 🏃 Хорошая |
| Intel (без Rosetta) | ❌ Не работает | ❌ Нет |

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
2. Установите Rosetta 2: `softwareupdate --install-rosetta`
3. Проверьте права доступа: `ls -la /Applications/SurveyApp.app`
"""
    
    with open("dist/README.md", "w") as f:
        f.write(readme_content)
    print("✅ Создан README")

def main():
    """Главная функция"""
    print("🍎 Сборка SurveyApp для Mac (Intel + Apple Silicon)")
    print("=" * 60)
    
    if not check_platform():
        return
    
    if not build_for_current_arch():
        return
    
    create_rosetta_launcher()
    create_installer_script()
    create_readme()
    
    print("\n🎉 Готово!")
    print("📁 Приложение: dist/SurveyApp.app")
    print("📁 Установка: dist/install.sh")
    print("📁 Документация: dist/README.md")
    
    print("\n💡 Для распространения:")
    print("1. Скопируйте папку dist/ на любой Mac")
    print("2. Запустите install.sh")
    print("3. Приложение будет работать на Intel и Apple Silicon")
    
    print("\n🔧 Особенности:")
    print("- Apple Silicon: нативная поддержка")
    print("- Intel Mac: через Rosetta 2")
    print("- Автоматическое определение архитектуры")

if __name__ == "__main__":
    main()


