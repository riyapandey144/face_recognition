@echo off
setlocal

cd /d "%~dp0"

if exist ".project_venv\Scripts\activate.bat" (
    call ".project_venv\Scripts\activate.bat"
)

if not exist ".project_venv\Scripts\activate.bat" if exist ".venv310\Scripts\activate.bat" (
    call ".venv310\Scripts\activate.bat"
)

if not exist ".project_venv\Scripts\activate.bat" if not exist ".venv310\Scripts\activate.bat" if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

python -m pip install opencv-python
pause
