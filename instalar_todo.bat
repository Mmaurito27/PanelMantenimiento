@echo off
rem Instalador del Panel de Mantenimiento General
setlocal

echo === Inicio de instalacion ===

rem 1. Verificar carpeta python y extraer runtime si es necesario
if not exist "python\python.exe" (
    echo Extrayendo Python embebido...
    if exist "_internal\python_runtime.zip" (
        powershell -Command "Expand-Archive -Path '_internal\\python_runtime.zip' -DestinationPath 'python' -Force"
    ) else (
        echo ERROR: No se encontro _internal\python_runtime.zip
        pause
        exit /b 1
    )
) else (
    echo Carpeta python existente.
)

rem 2. Copiar sitecustomize.py a site-packages
if not exist "python\Lib\site-packages" (
    mkdir "python\Lib\site-packages" >nul 2>&1
)
if exist "sitecustomize.py" (
    copy /Y "sitecustomize.py" "python\Lib\site-packages\" >nul
    echo sitecustomize.py copiado.
) else (
    echo ADVERTENCIA: sitecustomize.py no encontrado.
)

rem 3. Instalar dependencias con pip del python embebido
echo Instalando dependencias...
"python\python.exe" -m pip install -r requirements.txt

rem 4. Lanzar el panel con el mismo Python
echo Lanzando Panel de Mantenimiento...
"python\python.exe" panel_mantenimiento_general.py

echo === Instalacion finalizada ===
pause

