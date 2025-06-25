@echo off
rem Inicializa la estructura del Panel de Mantenimiento

setlocal

if not exist config mkdir config
if not exist logs mkdir logs
if not exist assets mkdir assets
if not exist launchers mkdir launchers
if not exist subpanels mkdir subpanels
if not exist docs mkdir docs

if not exist config\entorno.txt (
    if exist plantilla_entorno.txt (
        copy plantilla_entorno.txt config\entorno.txt >nul
    ) else (
        echo modo_oscuro=false>config\entorno.txt
        echo titulo=Panel de Mantenimiento General>>config\entorno.txt
        echo documentacion=docs/manual.pdf>>config\entorno.txt
    )
)

if not exist config\panels.json (
    echo ["rrhh"]>config\panels.json
)

if not exist version.txt (
    echo version=1.0.0>version.txt
)

echo Estructura inicial lista.
pause

