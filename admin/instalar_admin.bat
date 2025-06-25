@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set ROOT=%~dp0
set PYTHON_DIR=%ROOT%python
set ZIP=%ROOT%_internal\python_runtime.zip
set PYTHON_EXE=%PYTHON_DIR%\python.exe

set LOGFILE=logs\admin_installer.log
if not exist logs mkdir logs
>> %LOGFILE% echo ===== Inicio instalacion %date% %time% =====

echo === Instalador del Panel ===

rem 1. Verificar entorno Python
if not exist "%PYTHON_EXE%" (
    echo Extrayendo entorno Python embebido...
    if not exist "%ZIP%" (
        echo ❌ ERROR: No se encontro %ZIP%
        >> %LOGFILE% echo ERROR: zip no encontrado
        goto FAIL
    )
    if not exist "%PYTHON_DIR%" mkdir "%PYTHON_DIR%"
    tar -xf "%ZIP%" -C "%PYTHON_DIR%" >> %LOGFILE% 2>&1
)

if not exist "%PYTHON_EXE%" (
    echo ❌ ERROR: No se pudo extraer el entorno Python.
    >> %LOGFILE% echo ERROR: python no extraido
    goto FAIL
)

rem 2. Copiar sitecustomize.py
echo Copiando sitecustomize.py...
if not exist "%PYTHON_DIR%\Lib\site-packages" mkdir "%PYTHON_DIR%\Lib\site-packages"
copy /Y "sitecustomize.py" "%PYTHON_DIR%\Lib\site-packages\sitecustomize.py" >nul

rem 3. Instalar dependencias
echo Instalando dependencias...
"%PYTHON_EXE%" -m ensurepip >> %LOGFILE% 2>&1
"%PYTHON_EXE%" -m pip install --upgrade pip >> %LOGFILE% 2>&1
"%PYTHON_EXE%" -m pip install -r requirements.txt >> %LOGFILE% 2>&1

rem 4. Lanzar panel
echo Lanzando Panel de Mantenimiento...
"%PYTHON_EXE%" panel_mantenimiento_general.py

>> %LOGFILE% echo ===== Fin instalacion %date% %time% =====
goto END

:FAIL
echo Instalacion abortada.
>> %LOGFILE% echo ===== Instalacion FALLIDA %date% %time% =====

:END
pause
endlocal
