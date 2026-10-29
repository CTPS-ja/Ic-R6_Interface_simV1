@echo off
chcp 65001 >nul
echo ===================================================
echo FreqHub IC-R6 Interface Simulator Launcher
echo ===================================================

echo [1/2] Starting Virtual IC-R6 Simulator...
start "Virtual IC-R6" cmd /k "python -m virtual_icr6.main"

timeout /t 2 >nul

echo [2/2] Starting Virtual ESP32 & Web Server...
start "Virtual ESP32" cmd /k "python -m virtual_esp32.main"

echo.
echo IC-R6 Simulator : READY (TCP 7600)
echo Virtual ESP32    : READY
echo Web UI           : http://localhost:8080/
echo.
echo Press any key to close this launcher window (running services will keep running)...
pause >nul
