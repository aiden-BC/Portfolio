@echo off
cd /d "%~dp0"

REM Iniciar un servidor web local
start cmd /k python -m http.server 8001

REM Esperar unos segundos para que el servidor se inicie correctamente
timeout /t 2 /nobreak > NUL

REM Abrir el navegador en la dirección del servidor
start http://localhost:8001/index.html