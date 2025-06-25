@echo off
rem Instalador del Panel de Mantenimiento General
setlocal enabledelayedexpansion

set ROOT=%~dp0
set PYTHON_DIR=%ROOT%python
set ZIP=%ROOT%_internal\python_runtime.zip
set PYTHON_EXE=%PYTHON_DIR%\python.exe

echo === Inicio de instalacion ===

rem 1. Verificar carpeta python y extraer runtime si es necesario
if not exist "%PYTHON_EXE%" (
    echo Extrayendo Python embebido...
    if exist "%ZIP%" (
        powershell -Command "try { Expand-Archive -Path '%ZIP%' -DestinationPath '%PYTHON_DIR%' -Force } catch { exit 1 }"
    ) else (
        echo ERROR: No se encontro %ZIP%
        pause
        exit /b 1
    )
) else (
    echo Carpeta python existente.
)

if not exist "%PYTHON_EXE%" (
    echo No se pudo extraer el runtime de Python
    exit /b 1
)

rem 2. Copiar sitecustomize.py a site-packages
if not exist "%PYTHON_DIR%\Lib\site-packages" (
    mkdir "%PYTHON_DIR%\Lib\site-packages" >nul 2>&1
)
if exist "sitecustomize.py" (
    copy /Y "sitecustomize.py" "%PYTHON_DIR%\Lib\site-packages\sitecustomize.py" >nul
    echo sitecustomize.py copiado.
) else (
    echo ADVERTENCIA: sitecustomize.py no encontrado.
)

rem 3. Instalar dependencias con pip del python embebido
echo Instalando dependencias...
"%PYTHON_EXE%" -m ensurepip
"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r requirements.txt

rem 4. Lanzar el panel con el mismo Python
echo Lanzando Panel de Mantenimiento...
"%PYTHON_EXE%" panel_mantenimiento_general.py

echo === Instalacion finalizada ===
pause

