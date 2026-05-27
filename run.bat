@echo off
chcp 65001 >nul
echo ============================================
echo  AOAA Project - Starting Application
echo ============================================
echo.

:: Configuration
set "AOAA_PORT=8503"

:: Kill any previous streamlit on this port to prevent port conflict
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%AOAA_PORT%" ^| findstr "LISTENING" 2^>nul') do (
    echo Killing previous process on port %AOAA_PORT% (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo WARNING: No virtual environment found.
    echo Running with system Python. Run install.bat first if needed.
)
echo.
echo Starting Streamlit application on port %AOAA_PORT%...
echo Press Ctrl+C to stop the application.
echo.

:: Start streamlit in foreground; on exit (Ctrl+C or window close), cleanup runs
streamlit run app.py --server.port %AOAA_PORT%

:: === Cleanup on exit ===
echo.
echo Shutting down AOAA...

:: Kill any remaining streamlit processes on our port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%AOAA_PORT%" ^| findstr "LISTENING" 2^>nul') do (
    echo Cleaning up process on port %AOAA_PORT% (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

:: Also kill any orphaned streamlit processes started from this directory
for /f "tokens=2" %%a in ('wmic process where "commandline like '%%streamlit%%app.py%%'" get processid /value 2^>nul ^| findstr "="') do (
    echo Cleaning up orphaned streamlit process (PID: %%a)
    taskkill /PID %%a /F >nul 2>&1
)

echo AOAA stopped. Port %AOAA_PORT% released.
