@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "ROOT=%~dp0"
set "LOGFILE=%ROOT%logs\usuario_installer.log"
if not exist "%ROOT%logs" mkdir "%ROOT%logs"
>> "%LOGFILE%" echo ===== Inicio instalacion %date% %time% =====

rem 1. Verificar que haya Python disponible
set "PY_CMD=python"
where %PY_CMD% >nul 2>&1 || (
    set "PY_CMD=py"
    where %PY_CMD% >nul 2>&1 || (
        echo ⚠️ Este instalador requiere Python para compilar el panel.
        >> "%LOGFILE%" echo ERROR: Python no encontrado en PATH
        goto END
    )
)

rem 2. Instalar PyInstaller si es necesario
%PY_CMD% -m pip show pyinstaller >nul 2>&1
if not "%ERRORLEVEL%"=="0" (
    %PY_CMD% -m pip install pyinstaller >> "%LOGFILE%" 2>&1
)

rem 3. Instalar dependencias adicionales
if exist requirements.txt (
    %PY_CMD% -m pip install -r requirements.txt >> "%LOGFILE%" 2>&1
)

for %%D in (config logs) do (
    if not exist "%%D" (
        mkdir "%%D"
        >> "%LOGFILE%" echo Creada carpeta %%D
    )
)

rem 4. Compilar ejecutable
echo Compilando ejecutable...
%PY_CMD% -m PyInstaller ^
--onefile --noconsole ^
--add-data "config;config" ^
--add-data "subpanels;subpanels" ^
--distpath "%ROOT%" ^
"%ROOT%panel_mantenimiento_general.py" >> "%LOGFILE%" 2>&1

if exist "%ROOT%panel_mantenimiento_general.exe" (
    echo ✅ Ejecutable generado correctamente
    >> "%LOGFILE%" echo Ejecutable generado correctamente
    start "" "%ROOT%panel_mantenimiento_general.exe"
) else (
    echo ❌ Error: No se pudo generar el ejecutable
    >> "%LOGFILE%" echo ERROR: No se pudo generar el ejecutable
    echo %ROOT%panel_mantenimiento_general.exe
)

:END
>> "%LOGFILE%" echo ===== Fin instalacion %date% %time% =====
endlocal
