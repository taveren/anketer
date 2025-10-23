# 🪟 Сборка SurveyApp для Windows

## 📋 Требования

### 1. **Windows машина**
- Windows 10/11 (рекомендуется)
- 4GB RAM минимум
- 2GB свободного места

### 2. **Python 3.8+**
```bash
# Скачать с https://python.org
# Или через Microsoft Store
```

### 3. **Зависимости**
```bash
pip install PyQt6 PyInstaller Pillow
```

## 🚀 Быстрая сборка

### Вариант 1: Автоматический скрипт
```bash
python build_windows.py
```

### Вариант 2: Ручная сборка
```bash
# Очистка
rmdir /s dist build

# Сборка
pyinstaller --onefile --windowed --name "SurveyApp" --icon="favicon.ico" survey_app_pyqt.py
```

## 📦 Результат

После сборки получите:
- `dist/SurveyApp.exe` - исполняемый файл
- `dist/run_survey_app.bat` - скрипт запуска

## 🔧 Устранение проблем

### Проблема: "Python не найден"
```bash
# Добавьте Python в PATH
# Или используйте полный путь:
C:\Python39\python.exe build_windows.py
```

### Проблема: "PyQt6 не найден"
```bash
pip install --upgrade pip
pip install PyQt6 PyInstaller Pillow
```

### Проблема: "Иконка не найдена"
- Убедитесь, что `favicon.ico` в корне проекта
- Или укажите полный путь к иконке

## 📁 Структура после сборки

```
dist/
├── SurveyApp.exe          # Основное приложение
├── run_survey_app.bat     # Скрипт запуска
└── _internal/             # Внутренние файлы (если onedir)
```

## 🚀 Распространение

### Для пользователей:
1. Скопируйте папку `dist/`
2. Запустите `SurveyApp.exe`

### Для разработчиков:
1. Скопируйте весь проект
2. Установите зависимости
3. Запустите `python build_windows.py`

## 🔍 Тестирование

```bash
# Запуск из командной строки
cd dist
SurveyApp.exe

# Или через bat файл
run_survey_app.bat
```

## 📝 Примечания

- Приложение создает папку данных в `%APPDATA%\SurveyApp\Data\`
- Все данные хранятся локально
- Не требует интернета

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте версию Python (3.8+)
2. Убедитесь, что все зависимости установлены
3. Проверьте права доступа к папкам
4. Запустите от имени администратора

---

**Автор**: ASRR Team  
**Версия**: 1.0.0
