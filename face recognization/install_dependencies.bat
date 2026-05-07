@echo off
setlocal

cd /d "%~dp0"
set "VENV_DIR=.project_venv"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Virtual environment not found. Creating one now...
    py -3.11 --version >nul 2>nul
    if %errorlevel%==0 (
        py -3.11 -m venv "%VENV_DIR%"
    ) else (
        py -3.10 --version >nul 2>nul
        if %errorlevel%==0 (
            py -3.10 -m venv "%VENV_DIR%"
        ) else (
            where py >nul 2>nul
            if %errorlevel%==0 (
                py -3 -m venv "%VENV_DIR%"
            ) else (
                python -m venv "%VENV_DIR%"
            )
        )
    )
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Failed to create virtual environment. Install Python 3.10 or 3.11, then run this file again.
    pause
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo Dependency installation failed.
    echo If face_recognition fails, install Visual Studio Build Tools with C++ support, then run this file again.
    pause
    exit /b 1
)

echo Dependencies installed successfully.
pause
