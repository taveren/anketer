@echo off
echo 🚀 Установка зависимостей для SurveyApp
echo ========================================

echo 📦 Обновляем pip...
python -m pip install --upgrade pip

echo 📦 Устанавливаем зависимости...
pip install -r requirements_windows.txt

echo ✅ Готово!
echo.
echo 🔨 Для сборки запустите:
echo python build_windows.py
echo.
pause
