@echo off
REM ── Push changes to GitHub (origin/master) ─────────────────────────────
setlocal

cd /d "%~dp0"

echo.
echo Current status:
git status --short
echo.

set "MSG=%*"
if "%MSG%"=="" set /p "MSG=Enter commit message: "
if "%MSG%"=="" (
    echo No commit message provided. Aborting.
    exit /b 1
)

git add -A
git commit -m "%MSG%"
if errorlevel 1 (
    echo.
    echo Nothing committed ^(no changes or commit failed^).
    exit /b 1
)

git push origin main
if errorlevel 1 (
    echo.
    echo Push failed.
    exit /b 1
)

echo.
echo Done — changes pushed to origin/main.
endlocal
