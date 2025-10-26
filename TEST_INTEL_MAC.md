# 🧪 Тестирование SurveyApp на Intel Mac

## 🎯 Цель
Убедиться, что приложение работает на Intel Mac через Rosetta 2

## 🔧 Как это работает

### Структура приложения:
```
SurveyApp.app/
├── Contents/
│   └── MacOS/
│       ├── SurveyApp          # Wrapper скрипт (запускает правильную версию)
│       └── SurveyApp_Original # Оригинальное приложение (arm64)
```

### Логика работы:
1. **Apple Silicon Mac** → запускает `SurveyApp_Original` нативно
2. **Intel Mac** → запускает `SurveyApp_Original` через Rosetta 2

## 🚀 Тестирование

### На Apple Silicon Mac (M1/M2/M3/M4):
```bash
# Проверяем архитектуру
uname -m  # должно показать: arm64

# Запускаем приложение
open dist/SurveyApp.app

# Проверяем, что запустилось нативно
ps aux | grep SurveyApp
```

### На Intel Mac:
```bash
# Проверяем архитектуру
uname -m  # должно показать: x86_64

# Устанавливаем Rosetta 2 (если не установлен)
softwareupdate --install-rosetta

# Запускаем приложение
open dist/SurveyApp.app

# Проверяем, что запустилось через Rosetta
ps aux | grep SurveyApp
```

## 🔍 Проверка совместимости

### Проверка архитектуры приложения:
```bash
# Проверяем оригинальное приложение
file dist/SurveyApp.app/Contents/MacOS/SurveyApp_Original
# Должно показать: Mach-O 64-bit executable arm64

# Проверяем wrapper
file dist/SurveyApp.app/Contents/MacOS/SurveyApp
# Должно показать: Bourne-Again shell script
```

### Проверка работы wrapper:
```bash
# Запускаем wrapper напрямую
dist/SurveyApp.app/Contents/MacOS/SurveyApp

# Должно показать:
# 🔍 Архитектура: arm64 (или x86_64)
# ⚡ Apple Silicon Mac - запуск нативной версии
# (или)
# 🔄 Intel Mac - запуск через Rosetta 2
```

## 🛠️ Устранение проблем

### Проблема: "App is not supported on this Mac"
```bash
# Проверяем, что Rosetta 2 установлен
softwareupdate --install-rosetta

# Запускаем через Rosetta вручную
arch -x86_64 dist/SurveyApp.app/Contents/MacOS/SurveyApp_Original
```

### Проблема: "Permission denied"
```bash
# Даем права на выполнение
chmod +x dist/SurveyApp.app/Contents/MacOS/SurveyApp
chmod +x dist/SurveyApp.app/Contents/MacOS/SurveyApp_Original
```

### Проблема: "App is damaged"
```bash
# Разрешаем запуск
sudo xattr -rd com.apple.quarantine dist/SurveyApp.app
```

## 📊 Ожидаемые результаты

### Apple Silicon Mac:
- ✅ **Быстрый запуск** (~1-2 секунды)
- ✅ **Нативная производительность** (100%)
- ✅ **Автоматический запуск** без дополнительных действий

### Intel Mac:
- ✅ **Запуск через Rosetta 2** (~3-5 секунд)
- ✅ **Хорошая производительность** (~80-90%)
- ✅ **Автоматический запуск** после установки Rosetta 2

## 🔧 Отладка

### Проверка логов:
```bash
# Запускаем с выводом в консоль
dist/SurveyApp.app/Contents/MacOS/SurveyApp 2>&1 | tee surveyapp.log
```

### Проверка процессов:
```bash
# Смотрим, как запустилось приложение
ps aux | grep SurveyApp

# Должно показать что-то вроде:
# /Applications/SurveyApp.app/Contents/MacOS/SurveyApp_Original
```

## 📝 Результаты тестирования

### ✅ Успешное тестирование:
- [ ] Apple Silicon Mac - нативный запуск
- [ ] Intel Mac - запуск через Rosetta 2
- [ ] Все функции работают корректно
- [ ] Производительность приемлемая

### ❌ Проблемы:
- [ ] Приложение не запускается
- [ ] Медленная работа
- [ ] Ошибки при запуске
- [ ] Неправильное отображение

## 🚀 Готовое решение

Если все работает корректно:
1. **Копируйте** папку `dist/` на любой Mac
2. **Запустите** `install.sh` для установки
3. **Приложение** будет работать на Intel и Apple Silicon

---

**Автор**: ASRR Team  
**Версия**: 1.0.0  
**Дата**: 2025


