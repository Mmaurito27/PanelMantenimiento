@echo off
setlocal
cd /d "%~dp0"

set LOGFILE=logs\usuario_installer.log
if not exist logs mkdir logs
>> %LOGFILE% echo ===== Inicio instalacion %date% %time% =====

if not exist panel_mantenimiento_general.exe (
    >> %LOGFILE% echo ERROR: panel_mantenimiento_general.exe no encontrado
    echo No se encontro panel_mantenimiento_general.exe
    goto END
)

for %%D in (config logs) do (
    if not exist "%%D" (
        mkdir "%%D"
        >> %LOGFILE% echo Creada carpeta %%D
    )
)

if exist requirements.txt (
    >> %LOGFILE% echo Instalando dependencias
    pip install -r requirements.txt >> %LOGFILE% 2>&1
)

:END
>> %LOGFILE% echo ===== Fin instalacion %date% %time% =====
endlocal
