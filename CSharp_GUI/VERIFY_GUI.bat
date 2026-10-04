@echo off
setlocal
cd /d "%~dp0PANCAKE_GUI_01"
where dotnet >nul 2>nul
if errorlevel 1 (
  echo .NET 8 SDK was not found.
  echo Install the .NET 8 SDK, then run this file again.
  pause
  exit /b 1
)

echo Building and running PANCAKE GUI self-test...
dotnet run -c Release -- --self-test
set TEST_RESULT=%ERRORLEVEL%
set LOG_PATH=%CD%\bin\Release\net8.0-windows\gui_self_test.log

echo.
if exist "%LOG_PATH%" type "%LOG_PATH%"
echo.
if not "%TEST_RESULT%"=="0" (
  echo GUI self-test FAILED.
  pause
  exit /b %TEST_RESULT%
)

echo GUI self-test PASSED.
pause
endlocal
