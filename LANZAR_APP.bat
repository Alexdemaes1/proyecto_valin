@echo off
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ===================================================
echo   INICIALIZANDO SISTEMA VALIN E HIJOS S.A.
echo ===================================================

:: 1. Comprobar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no detectado. Instala Python y marcalo en el PATH.
    pause
    exit /b
)

:: 2. Entorno Virtual (RELATIVO)
if not exist "venv" (
    echo [INFO] Creando entorno virtual local...
    python -m venv venv
)

:: 3. Activar entorno e instalar dependencias
echo [INFO] Verificando dependencias activas...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python -m pip install --upgrade pip
pip install -r requirements.txt

:: 4. Config base .env
if not exist ".env" (
    echo [INFO] Generando configuracion de entorno .env...
    (
      echo FLASK_APP=run.py
      echo FLASK_ENV=development
      echo SECRET_KEY=valin-!secure-v1-!
    ) > .env
)

:: 5. Crear carpetas necesarias
if not exist "instance" mkdir "instance"
if not exist "instance\backups" mkdir "instance\backups"

:: 6. Inicializar Admin y Roles con la nueva pass
echo [INFO] Preparando base de datos y usuario admin...
python scripts\create_admin.py

:: 7. Lanzamiento Web
echo.
echo [OK] SISTEMA LISTO PARA OPERAR EN LA RED LOCAL.
echo [INFO] Accesible desde este PC en: http://127.0.0.1:5000
echo [INFO] Para acceder desde otro ordenador, busque su IP en el texto de abajo.
echo [INFO] Si es la primera vez, configure Google Drive en el Dashboard.
echo.
start http://127.0.0.1:5000
python run.py

pause
