# 🍎 Универсальная сборка для Mac (Intel + Apple Silicon)

## 🎯 Цель
Создать приложение, которое работает на:
- ✅ **Intel Mac** (x86_64)
- ✅ **Apple Silicon Mac** (M1/M2/M3, arm64)
- ✅ **Универсальное приложение** (Universal Binary)

## 📋 Требования

### 1. **macOS с Xcode Command Line Tools**
```bash
# Установка Xcode Command Line Tools
xcode-select --install
```

### 2. **Python с поддержкой universal2**
```bash
# Проверяем архитектуру
python -c "import platform; print(platform.machine())"

# Должно показать: arm64 или x86_64
```

### 3. **PyInstaller с universal2 поддержкой**
```bash
pip install --upgrade pyinstaller
```

## 🚀 Быстрая сборка

### Автоматический способ:
```bash
python build_universal.py
```

### Ручной способ:
```bash
# Очистка
rm -rf dist build

# Универсальная сборка
pyinstaller --onedir --windowed --name "SurveyApp" --icon="favicon.ico" --target-arch universal2 survey_app_pyqt.py
```

## 📦 Результат

После сборки получите:
- `dist/SurveyApp.app` - универсальное приложение
- `dist/install.sh` - скрипт установки
- `dist/SurveyApp.dmg` - DMG для распространения (опционально)

## 🔍 Проверка архитектуры

### Проверить приложение:
```bash
# Проверяем архитектуры в приложении
file dist/SurveyApp.app/Contents/MacOS/SurveyApp

# Должно показать что-то вроде:
# Mach-O universal binary with 2 architectures: [arm64:Mach-O 64-bit executable arm64] [x86_64:Mach-O 64-bit executable x86_64]
```

### Проверить на разных Mac:
```bash
# На Intel Mac
uname -m  # должно показать: x86_64

# На Apple Silicon Mac  
uname -m  # должно показать: arm64
```

## 🚀 Распространение

### Вариант 1: Прямое копирование
```bash
# Копируем приложение
cp -R dist/SurveyApp.app /Applications/

# Запускаем
open /Applications/SurveyApp.app
```

### Вариант 2: DMG файл
```bash
# Создаем DMG
hdiutil create -volname "SurveyApp" -srcfolder dist/SurveyApp.app -ov -format UDZO dist/SurveyApp.dmg

# Распространяем DMG файл
```

### Вариант 3: Скрипт установки
```bash
# Запускаем скрипт установки
cd dist
./install.sh
```

## 🔧 Устранение проблем

### Проблема: "target-arch universal2 not supported"
```bash
# Обновите PyInstaller
pip install --upgrade pyinstaller

# Или используйте более новую версию Python
```

### Проблема: "Architecture not supported"
```bash
# Проверьте версию macOS
sw_vers

# Убедитесь, что Xcode Command Line Tools установлены
xcode-select -p
```

### Проблема: Приложение не запускается на Intel Mac
```bash
# Проверьте архитектуру приложения
lipo -info dist/SurveyApp.app/Contents/MacOS/SurveyApp

# Должно показать: Architectures in the fat file: arm64 x86_64
```

## 📊 Сравнение размеров

| Тип сборки | Размер | Совместимость |
|------------|--------|---------------|
| Intel only | ~15MB | Только Intel Mac |
| Apple Silicon only | ~15MB | Только Apple Silicon |
| Universal Binary | ~30MB | Intel + Apple Silicon |

## 🎯 Рекомендации

### Для разработки:
- Используйте `--onedir` вместо `--onefile` для лучшей совместимости
- Тестируйте на обеих архитектурах
- Создавайте DMG для удобного распространения

### Для распространения:
- DMG файл - лучший вариант для пользователей
- Скрипт установки - для технических пользователей
- Прямое копирование - для разработчиков

## 🔍 Тестирование

### На Intel Mac:
```bash
# Запуск
open dist/SurveyApp.app

# Проверка архитектуры
arch -x86_64 python -c "import platform; print(platform.machine())"
```

### На Apple Silicon Mac:
```bash
# Запуск
open dist/SurveyApp.app

# Проверка архитектуры
arch -arm64 python -c "import platform; print(platform.machine())"
```

## 📝 Примечания

- Universal Binary увеличивает размер приложения в ~2 раза
- Но обеспечивает максимальную совместимость
- Рекомендуется для публичного распространения
- Для внутреннего использования можно собирать под конкретную архитектуру

---

**Автор**: ASRR Team  
**Версия**: 1.0.0


