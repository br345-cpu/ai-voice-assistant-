@echo off
setlocal

if exist ".venv\Scripts\python.exe" (
    echo Virtual environment already exists.
) else (
    where py >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        py -3.13 -m venv .venv
    ) else (
        python -m venv .venv
    )
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    echo.
    echo Setup complete. Run run.bat to start the project.
) else (
    echo Failed to create a virtual environment.
    exit /b 1
)
