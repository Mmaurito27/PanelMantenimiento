@echo off
setlocal enableextensions

rem Crear carpetas necesarias
for %%d in (logs config launchers subpanels assets) do (
    if not exist "%%d" mkdir "%%d"
)

rem Copiar archivo de entorno por defecto
if not exist "config\entorno.txt" (
    if exist "entorno_ejemplo.txt" (
        copy "entorno_ejemplo.txt" "config\entorno.txt" >nul
    ) else (
        echo modo_oscuro=false>"config\entorno.txt"
        echo titulo=Panel de Mantenimiento General>>"config\entorno.txt"
        echo documentacion=docs/manual.pdf>>"config\entorno.txt"
    )
)

rem Crear archivo de log
if not exist "logs\panel.log" type nul > "logs\panel.log"

rem Verificar ejecutables
set missing=0
if not exist "launchers\cv_api_launcher.exe" (
    echo FALTA: cv_api_launcher.exe
    set missing=1
)
if not exist "launchers\n8n_launcher.exe" (
    echo FALTA: n8n_launcher.exe
    set missing=1
)

rem Comprobar presencia de Python embebido
if not exist "_internal\python3*.dll" (
    echo Aviso: Python embebido no encontrado. Instale Python si es necesario.
)

if %missing%==1 (
    echo Por favor copie los ejecutables faltantes a la carpeta launchers.
    start "" explorer "%cd%\launchers"
)

echo Entorno listo.
exit /b
