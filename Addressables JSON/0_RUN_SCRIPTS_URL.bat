@echo off
echo Running Python Scripts...

REM Change to the directory of the batch file (inside AddressablesJSON)
cd /d "%~dp0"






REM Run 1. Parse JSON extracting aim cover_URL.py
python "1. Parse JSON extracting aim cover_URL.py"
if %errorlevel% neq 0 (
    echo 1. Parse JSON extracting aim cover_URL.py failed
    pause
    exit /b %errorlevel%
)
echo 1. Parse JSON extracting aim cover_URL.py ran successfully







REM Run 2. Parse JSON extracting standing_URL.py
python "2. Parse JSON extracting standing_URL.py"
if %errorlevel% neq 0 (
    echo 2. Parse JSON extracting standing_URL.py failed
    pause
    exit /b %errorlevel%
)
echo 2. Parse JSON extracting standing_URL.py ran successfully














REM Run 3. Parse JSON extracting portraits_URL.py
python "3. Parse JSON extracting portraits_URL.py"
if %errorlevel% neq 0 (
    echo 3. Parse JSON extracting portraits_URL.py failed
    pause
    exit /b %errorlevel%
)
echo 3. Parse JSON extracting portraits_URL.py ran successfully








echo All scripts ran successfully.
exit
