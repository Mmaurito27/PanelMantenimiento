@echo off
setlocal
cd /d "%~dp0"

set LOGFILE=logs\usuario_installer.log
if not exist logs mkdir logs
>> %LOGFILE% echo ===== Inicio instalador %date% %time% =====

if not exist panel_mantenimiento_general.exe (
    echo ❌ ERROR: panel_mantenimiento_general.exe no encontrado
    >> %LOGFILE% echo ERROR: exe faltante
    goto END
)

for %%D in (config logs) do if not exist "%%D" mkdir "%%D"

echo Lanzando aplicacion...
>> %LOGFILE% echo Iniciando exe %date% %time%
start "" panel_mantenimiento_general.exe

:END
>> %LOGFILE% echo ===== Fin instalador %date% %time% =====
endlocal
