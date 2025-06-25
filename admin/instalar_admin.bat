@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
set "PYTHON_DIR=%ROOT%python"
set "ZIP=%ROOT%_internal\python_runtime.zip"
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"

set "LOGFILE=%ROOT%logs\admin_installer.log"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
>> "%LOGFILE%" echo ===== Inicio instalacion %date% %time% =====

rem 1. Verificar Python embebido
if not exist "%PYTHON_EXE%" (
    echo Extrayendo entorno Python embebido...
    powershell -Command "try { Expand-Archive -Path '%ZIP%' -DestinationPath '%PYTHON_DIR%' -Force } catch { exit 1 }" >> "%LOGFILE%" 2>&1
)
if not exist "%PYTHON_EXE%" (
    >> "%LOGFILE%" echo ERROR: No se pudo extraer python_runtime.zip
    echo ❌ Python embebido no disponible.
    goto END
) else (
    >> "%LOGFILE%" echo Python embebido disponible
)

rem 2. Copiar sitecustomize.py
if exist "sitecustomize.py" (
    if not exist "%PYTHON_DIR%\Lib\site-packages" mkdir "%PYTHON_DIR%\Lib\site-packages"
    copy /Y "sitecustomize.py" "%PYTHON_DIR%\Lib\site-packages\sitecustomize.py" >nul
    >> "%LOGFILE%" echo Copiado sitecustomize.py
)

rem 3. Instalar dependencias
echo Instalando dependencias...
"%PYTHON_EXE%" -m ensurepip >> "%LOGFILE%" 2>&1
"%PYTHON_EXE%" -m pip install --upgrade pip >> "%LOGFILE%" 2>&1
"%PYTHON_EXE%" -m pip install -r "%ROOT%requirements.txt" >> "%LOGFILE%" 2>&1

rem 4. Crear carpetas necesarias
for %%D in (logs config launchers subpanels docs) do (
    if not exist "%%D" (
        mkdir "%%D"
        >> "%LOGFILE%" echo Creada carpeta %%D
    )
)

rem 5. Verificar ejecutables
if not exist "%ROOT%launchers\cv_api_launcher.exe" echo ⚠️ FALTA: cv_api_launcher.exe
if not exist "%ROOT%launchers\n8n_launcher.exe" echo ⚠️ FALTA: n8n_launcher.exe

rem 6. Lanzar el panel
>> "%LOGFILE%" echo Lanzando panel
"%PYTHON_EXE%" "%ROOT%panel_mantenimiento_general.py" >> "%LOGFILE%" 2>&1

:END
>> "%LOGFILE%" echo ===== Fin instalacion %date% %time% =====
endlocal
