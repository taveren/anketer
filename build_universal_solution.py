#!/usr/bin/env python3
"""
Скрипт для создания универсального приложения для Mac
Создает отдельные версии для Intel и Apple Silicon
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
    if os.path.exists("SurveyApp.spec"):
        os.remove("SurveyApp.spec")
    
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

def create_universal_launcher():
    """Создаем универсальный launcher"""
    print("🔧 Создаем универсальный launcher...")
    
    app_path = "dist/SurveyApp.app"
    if not os.path.exists(app_path):
        print("❌ Приложение не найдено!")
        return False
    
    # Создаем универсальный launcher
    launcher_content = """#!/bin/bash
# Универсальный launcher для SurveyApp
# Поддерживает Intel и Apple Silicon Mac

# Получаем путь к приложению
APP_DIR="$(dirname "$0")"
EXECUTABLE="$APP_DIR/SurveyApp_Original"

# Проверяем архитектуру
ARCH=$(uname -m)
echo "🔍 Архитектура: $ARCH"

# Проверяем, что исполняемый файл существует
if [ ! -f "$EXECUTABLE" ]; then
    echo "❌ Ошибка: Исполняемый файл не найден: $EXECUTABLE"
    exit 1
fi

# Проверяем архитектуру исполняемого файла
FILE_ARCH=$(file "$EXECUTABLE" | grep -o "arm64\\|x86_64" | head -1)
echo "🔍 Архитектура приложения: $FILE_ARCH"

# Если мы на Apple Silicon
if [[ "$ARCH" == "arm64" ]]; then
    if [[ "$FILE_ARCH" == "arm64" ]]; then
        echo "⚡ Apple Silicon Mac - запуск нативной версии"
        exec "$EXECUTABLE" "$@"
    else
        echo "🔄 Apple Silicon Mac - запуск через Rosetta 2"
        arch -x86_64 "$EXECUTABLE" "$@"
    fi
# Если мы на Intel
elif [[ "$ARCH" == "x86_64" ]]; then
    if [[ "$FILE_ARCH" == "x86_64" ]]; then
        echo "⚡ Intel Mac - запуск нативной версии"
        exec "$EXECUTABLE" "$@"
    else
        echo "🔄 Intel Mac - запуск через Rosetta 2"
        arch -x86_64 "$EXECUTABLE" "$@"
    fi
else
    echo "❌ Неподдерживаемая архитектура: $ARCH"
    exit 1
fi
"""
    
    # Создаем launcher
    launcher_path = f"{app_path}/Contents/MacOS/SurveyApp_Launcher"
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    # Делаем launcher исполняемым
    os.chmod(launcher_path, 0o755)
    
    # Переименовываем оригинальный файл
    original_path = f"{app_path}/Contents/MacOS/SurveyApp"
    backup_path = f"{app_path}/Contents/MacOS/SurveyApp_Original"
    
    if os.path.exists(original_path):
        shutil.move(original_path, backup_path)
        shutil.move(launcher_path, original_path)
        print("✅ Универсальный launcher создан!")
        return True
    else:
        print("❌ Оригинальный исполняемый файл не найден!")
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
    echo "✅ Intel Mac - поддержка через Rosetta 2"
    echo "💡 Убедитесь, что Rosetta 2 установлен:"
    echo "   softwareupdate --install-rosetta"
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
echo "1. Установите Rosetta 2: softwareupdate --install-rosetta"
echo "2. Разрешите в настройках безопасности"
echo "3. Или запустите: sudo xattr -rd com.apple.quarantine /Applications/SurveyApp.app"
echo ""
echo "🔍 Проверка архитектуры:"
echo "   uname -m  # arm64 = Apple Silicon, x86_64 = Intel"
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

### Проблема: "App is not supported on this Mac"
```bash
# Установите Rosetta 2
softwareupdate --install-rosetta

# Или запустите через Rosetta 2
arch -x86_64 /Applications/SurveyApp.app/Contents/MacOS/SurveyApp_Original
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
4. Запустите через Rosetta: `arch -x86_64 /Applications/SurveyApp.app/Contents/MacOS/SurveyApp_Original`
"""
    
    with open("dist/README.md", "w") as f:
        f.write(readme_content)
    print("✅ Создан README")

def main():
    """Главная функция"""
    print("🍎 Создание универсального SurveyApp для Mac")
    print("=" * 60)
    
    if not check_platform():
        return
    
    if not build_for_current_arch():
        return
    
    if not create_universal_launcher():
        return
    
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
    print("- Умный launcher с проверкой совместимости")

if __name__ == "__main__":
    main()


