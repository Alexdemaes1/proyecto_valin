@echo off
setlocal enabledelayedexpansion
echo ===================================================
echo   INSTALADOR CORPORATIVO - TRANSPORTES VALIN
echo ===================================================

:: 1. Verificar/Instalar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Python no detectado. Descargando instalador...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe -OutFile python_installer.exe"
    echo [INFO] Ejecutando instalador de Python. POR FAVOR MARQUE 'Add Python to PATH'.
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo [OK] Python instalado. Reinicie este script si falla el siguiente paso.
) else (
    echo [OK] Python detectado.
)

:: 2. Verificar/Instalar Git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Git no detectado. Descargando Git para Windows...
    powershell -Command "Invoke-WebRequest -Uri https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe -OutFile git_installer.exe"
    echo [INFO] Ejecutando instalador de Git. Siga los pasos por defecto.
    start /wait git_installer.exe /SILENT
    del git_installer.exe
    echo [OK] Git instalado.
) else (
    echo [OK] Git detectado.
)

:: 3. Definir Carpeta de Destino en el Escritorio
set "TARGET_DIR=%USERPROFILE%\Desktop\Gestion_Valin"
if exist "%TARGET_DIR%" (
    echo [WARNING] La carpeta %TARGET_DIR% ya existe.
    set /p "choice=¿Desea borrarla y re-instalar? (S/N): "
    if /i "!choice!"=="S" (
        rd /s /q "%TARGET_DIR%"
    ) else (
        echo [INFO] Abriendo aplicacion existente...
        cd /d "%TARGET_DIR%"
        goto launch
    )
)

:: 4. Clonar el repositorio
echo [INFO] Clonando repositorio privado...
git clone https://github.com/Alexdemaes1/proyecto_valin.git "%TARGET_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo clonar el repositorio. Asegurese de tener permisos.
    pause
    exit /b
)

:: 5. Entrar y Lanzar
cd /d "%TARGET_DIR%"

:launch
echo [OK] Instalacion completa. Iniciando sistema...
if exist "LANZAR_APP.bat" (
    call LANZAR_APP.bat
) else (
    echo [ERROR] No se encuentra LANZAR_APP.bat en el repositorio clonado.
    pause
)

exit /b
