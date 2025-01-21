@echo off
SETLOCAL

REM Убедитесь, что Python установлен
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python не установлен или не добавлен в PATH.
    pause
    exit /b 1
)

REM Проверьте, существует ли виртуальное окружение
IF NOT EXIST ".venv" (
    echo Виртуальное окружение не найдено. Запустите setup_and_run.bat для настройки.
    pause
    exit /b 1
)

REM Активируйте виртуальное окружение
CALL .venv\Scripts\activate

REM Запустите приложение
python spread_app.py

REM Деактивируйте виртуальное окружение после завершения
deactivate
ENDLOCAL
