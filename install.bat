@echo off
chcp 65001 >nul
echo ============================================
echo  AOAA Project - Installation Script
echo ============================================
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    echo Please ensure Python 3.9+ is installed and in PATH.
    pause
    exit /b 1
)
echo Virtual environment created successfully.
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some dependencies failed to install.
    echo The application may still work with reduced functionality.
    echo.
)
echo.
echo ============================================
echo  Installation complete!
echo  Run 'run.bat' to start the application.
echo ============================================
pause
