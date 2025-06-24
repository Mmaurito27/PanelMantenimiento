@echo off
setlocal enableextensions

if not exist "docs\entorno_default.txt" (
    echo No se encuentra docs\entorno_default.txt
    exit /b
)
if not exist config mkdir config
copy /Y "docs\entorno_default.txt" "config\entorno.txt" >nul

echo Configuracion restaurada.
exit /b
