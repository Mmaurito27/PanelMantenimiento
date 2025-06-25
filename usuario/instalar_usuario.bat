@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
set "PY_DIR=%ROOT%_internal\python"
set "ZIP=%ROOT%_internal\python_runtime.zip"
set "PY_EXE=%PY_DIR%\python.exe"

set "LOGFILE=%ROOT%logs\usuario_installer.log"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
>> "%LOGFILE%" echo ===== Inicio instalacion %date% %time% =====

if not exist panel_mantenimiento_general.exe (
    >> "%LOGFILE%" echo ERROR: panel_mantenimiento_general.exe no encontrado
    echo No se encontro panel_mantenimiento_general.exe
    goto END
)

rem Extraer Python embebido si es necesario
if not exist "%PY_EXE%" (
    if exist "%ZIP%" (
        powershell -Command "try { Expand-Archive -Path '%ZIP%' -DestinationPath '%PY_DIR%' -Force } catch { exit 1 }" >> "%LOGFILE%" 2>&1
    ) else (
        >> "%LOGFILE%" echo python_runtime.zip no encontrado
    )
)

if exist "%PY_EXE%" (
    "%PY_EXE%" -m ensurepip >> "%LOGFILE%" 2>&1
    "%PY_EXE%" -m pip install --upgrade pip >> "%LOGFILE%" 2>&1
    if exist requirements.txt (
        "%PY_EXE%" -m pip install -r requirements.txt >> "%LOGFILE%" 2>&1
    )
)

for %%D in (config logs) do (
    if not exist "%%D" (
        mkdir "%%D"
        >> "%LOGFILE%" echo Creada carpeta %%D
    )
)

>> "%LOGFILE%" echo Lanzando aplicacion
start "" panel_mantenimiento_general.exe

:END
>> "%LOGFILE%" echo ===== Fin instalacion %date% %time% =====
endlocal
