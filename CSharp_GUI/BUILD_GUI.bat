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
dotnet clean -c Release
dotnet build -c Release
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)
echo.
echo Build completed successfully.
echo Output: PANCAKE_GUI_01\bin\Release\net8.0-windows\
pause
endlocal
