@echo off
setlocal EnableExtensions

title Sistema de Farmacia

set "ROOT=%~dp0"
set "PYTHON=%ROOT%venv\Scripts\python.exe"
set "COMPOSE=%ROOT%docker\docker-compose.yml"

cd /d "%ROOT%"

echo ========================================
echo  SISTEMA DE FARMACIA
echo  Flask + MariaDB + RabbitMQ
echo ========================================
echo.

REM ========================================================
REM VERIFICAR DOCKER
REM ========================================================

docker info >nul 2>&1

if errorlevel 1 (
    echo [ERROR] Docker Desktop no esta iniciado.
    echo Abre Docker Desktop y vuelve a ejecutar start.bat.
    pause
    exit /b 1
)

echo [OK] Docker Desktop disponible.


REM ========================================================
REM VERIFICAR MARIADB
REM Si ya existe un servidor local en 3306, se utiliza.
REM ========================================================

powershell -NoProfile -Command ^
"$resultado = Test-NetConnection 127.0.0.1 -Port 3306 -WarningAction SilentlyContinue; if ($resultado.TcpTestSucceeded) { exit 0 } else { exit 1 }"

if not errorlevel 1 (
    echo [OK] MariaDB disponible en el puerto 3306.
) else (
    echo [INFO] MariaDB no esta disponible. Intentando iniciar farmacia_db...

    docker inspect farmacia_db >nul 2>&1

    if not errorlevel 1 (
        docker start farmacia_db >nul 2>&1
    ) else (
        docker compose -f "%COMPOSE%" up -d mariadb
    )

    timeout /t 8 /nobreak >nul

    powershell -NoProfile -Command ^
    "$resultado = Test-NetConnection 127.0.0.1 -Port 3306 -WarningAction SilentlyContinue; if ($resultado.TcpTestSucceeded) { exit 0 } else { exit 1 }"

    if errorlevel 1 (
        echo [ERROR] MariaDB no pudo iniciarse.
        pause
        exit /b 1
    )

    echo [OK] MariaDB iniciado correctamente.
)


REM ========================================================
REM VERIFICAR RABBITMQ
REM ========================================================

docker inspect farmacia_broker >nul 2>&1

if not errorlevel 1 (
    docker start farmacia_broker >nul 2>&1
) else (
    echo [INFO] Creando contenedor RabbitMQ...
    docker compose -f "%COMPOSE%" up -d rabbitmq
)

if errorlevel 1 (
    echo [ERROR] RabbitMQ no pudo iniciarse.
    pause
    exit /b 1
)

echo [OK] RabbitMQ iniciado.

timeout /t 6 /nobreak >nul


REM ========================================================
REM VERIFICAR PYTHON
REM ========================================================

if not exist "%PYTHON%" (
    echo [ERROR] No existe el entorno virtual:
    echo %PYTHON%
    echo.
    echo Ejecuta:
    echo python -m venv venv
    echo venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "%ROOT%app.py" (
    echo [ERROR] No existe app.py.
    pause
    exit /b 1
)

if not exist "%ROOT%consumer.py" (
    echo [ERROR] No existe consumer.py.
    pause
    exit /b 1
)


REM ========================================================
REM INICIAR FLASK
REM ========================================================

echo [INFO] Iniciando Flask...

start "Farmacia - Flask" cmd /k ^
""%PYTHON%" "%ROOT%app.py""

timeout /t 4 /nobreak >nul


REM ========================================================
REM INICIAR CONSUMIDOR
REM ========================================================

echo [INFO] Iniciando consumidor RabbitMQ...

start "Farmacia - RabbitMQ Consumer" cmd /k ^
""%PYTHON%" "%ROOT%consumer.py""

timeout /t 3 /nobreak >nul


REM ========================================================
REM ABRIR SISTEMA
REM ========================================================

start "" "http://127.0.0.1:5000/login"

echo.
echo ========================================
echo  SISTEMA INICIADO
echo ========================================
echo Flask:
echo   http://127.0.0.1:5000/login
echo.
echo RabbitMQ:
echo   http://localhost:15672
echo.
echo No cierres las ventanas de Flask y Consumer.
echo ========================================
echo.

pause