@echo off
REM run_app.bat – запуск приложения в виртуальном окружении

if not exist "venv" (
    echo Виртуальное окружение не найдено. Запуск установки...
    call setup_and_run.bat
    exit /b
)

echo Активируем виртуальное окружение...
call venv\Scripts\activate

echo Запуск приложения...
python main.py

if errorlevel 1 (
    echo Ошибка запуска приложения, выполняется настройка...
    call setup_and_run.bat
)

pause
