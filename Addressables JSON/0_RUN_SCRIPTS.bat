@echo off
echo Running Python Scripts...

REM Change to the directory of the batch file (inside AddressablesJSON)
cd /d "%~dp0"






REM Run 1. Parse JSON extracting aim cover.py
python "1. Parse JSON extracting aim cover.py"
if %errorlevel% neq 0 (
    echo 1. Parse JSON extracting aim cover.py failed
    pause
    exit /b %errorlevel%
)
echo 1. Parse JSON extracting aim cover.py ran successfully







REM Run 2. Parse JSON extracting standing.py
python "2. Parse JSON extracting standing.py"
if %errorlevel% neq 0 (
    echo 2. Parse JSON extracting standing.py failed
    pause
    exit /b %errorlevel%
)
echo 2. Parse JSON extracting standing.py ran successfully








REM Run 3. Parse JSON extracting portraits.py
python "3. Parse JSON extracting portraits.py"
if %errorlevel% neq 0 (
    echo 3. Parse JSON extracting portraits.py failed
    pause
    exit /b %errorlevel%
)
echo 3. Parse JSON extracting portraits.py ran successfully







echo All scripts ran successfully.
exit
