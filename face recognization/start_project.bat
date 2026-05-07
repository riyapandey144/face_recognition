@echo off
setlocal

cd /d "%~dp0"
set "VENV_DIR=.project_venv"

call :find_python
if errorlevel 1 exit /b 1

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating virtual environment...
    %PY_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Installing required packages...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Failed to upgrade pip.
    pause
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    echo If face_recognition fails, install Visual Studio Build Tools with C++ support, then run this file again.
    pause
    exit /b 1
)

cd project
if errorlevel 1 (
    echo Could not open the Django project folder.
    pause
    exit /b 1
)

echo Applying database migrations...
python manage.py migrate
if errorlevel 1 (
    echo Database migration failed.
    pause
    exit /b 1
)

echo.
echo Project is starting at http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server.
echo.
python manage.py runserver 127.0.0.1:8000
exit /b %errorlevel%

:find_python
py -3.11 --version >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py -3.11"
    exit /b 0
)

py -3.10 --version >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py -3.10"
    exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py -3"
    exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=python"
    exit /b 0
)

echo Python was not found. Install Python 3.10 or 3.11, then run this file again.
pause
exit /b 1
