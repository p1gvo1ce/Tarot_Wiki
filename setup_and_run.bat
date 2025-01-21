@echo off
REM setup_and_run.bat – настройка окружения и запуск приложения

echo Создаём виртуальное окружение...
python -m venv venv

echo Активируем виртуальное окружение...
call venv\Scripts\activate

echo Обновляем pip...
pip install --upgrade pip

echo Устанавливаем зависимости...
pip install -r requirements.txt

echo Настройка завершена. Запускаем приложение через run_app.bat...
call run_app.bat

pause
