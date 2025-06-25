@echo off
rem Prepara entorno portable e inicia el panel
setlocal
if not exist _internal mkdir _internal
if not exist _internal\python\python.exe (
    if exist _internal\python_runtime.zip (
        powershell -Command "Expand-Archive -Path '_internal\python_runtime.zip' -DestinationPath '_internal\python' -Force"
    ) else (
        echo Falta runtime de Python en _internal\python_runtime.zip
    )
)
call instalar_todo.bat >nul
start "" panel_mantenimiento_general.exe
