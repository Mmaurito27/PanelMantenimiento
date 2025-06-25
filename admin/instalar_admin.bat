@echo off
setlocal
cd /d "%~dp0"

set LOGFILE=logs\admin_installer.log
if not exist logs mkdir logs

>> %LOGFILE% echo ===== Inicio instalacion %date% %time% =====

rem 1. Verificar python embebido
if not exist "python\python.exe" (
    if exist "_internal\python_runtime.zip" (
        >> %LOGFILE% echo Extrayendo runtime de Python
        powershell -Command "Expand-Archive -Path '_internal\\python_runtime.zip' -DestinationPath 'python' -Force" >> %LOGFILE% 2>&1
    ) else (
        >> %LOGFILE% echo ERROR: _internal\python_runtime.zip no encontrado
        echo No se encontro _internal\python_runtime.zip
        goto END
    )
) else (
    >> %LOGFILE% echo Python embebido ya existente
)

rem 2. Copiar sitecustomize.py
if exist "sitecustomize.py" (
    if not exist "python\Lib\site-packages" mkdir "python\Lib\site-packages"
    copy /Y "sitecustomize.py" "python\Lib\site-packages\sitecustomize.py" >nul
    >> %LOGFILE% echo Copiado sitecustomize.py
) else (
    >> %LOGFILE% echo sitecustomize.py no encontrado
)

rem 3. Instalar dependencias
>> %LOGFILE% echo Instalando dependencias
"python\python.exe" -m pip install -r requirements.txt >> %LOGFILE% 2>&1

rem 4. Crear carpetas necesarias
for %%D in (logs config launchers subpanels docs) do (
    if not exist "%%D" (
        mkdir "%%D"
        >> %LOGFILE% echo Creada carpeta %%D
    )
)

rem 5. Verificar ejecutables
set FALTANTES=
if not exist "launchers\cv_api_launcher.exe" set FALTANTES=%FALTANTES% cv_api_launcher.exe
if not exist "launchers\n8n_launcher.exe" set FALTANTES=%FALTANTES% n8n_launcher.exe
if not "%FALTANTES%"=="" (
    >> %LOGFILE% echo ADVERTENCIA: faltan%FALTANTES%
    echo Faltan ejecutables:%FALTANTES%
)

rem 6. Lanzar panel
>> %LOGFILE% echo Lanzando panel
"python\python.exe" panel_mantenimiento_general.py >> %LOGFILE% 2>&1

:END
>> %LOGFILE% echo ===== Fin instalacion %date% %time% =====
endlocal
