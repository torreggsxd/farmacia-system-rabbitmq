Clear-Host

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SISTEMA FARMACIA - MODO DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# -------------------------------
# FUNCION: CHECK COMANDO
# -------------------------------
function Check-Command($cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Falta: $cmd" -ForegroundColor Red
        exit 1
    }
}

# -------------------------------
# VALIDACIONES BASE
# -------------------------------
Write-Host "`n[CHECK] Verificando herramientas..." -ForegroundColor Yellow
Check-Command "docker"
Check-Command "python"
Check-Command "pip"

# -------------------------------
# 1. DOCKER (MQ + MARIADB)
# -------------------------------
Write-Host "`n[1/5] Iniciando Docker (MQ + MariaDB)..." -ForegroundColor Cyan

cd docker
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker no pudo iniciarse" -ForegroundColor Red
    exit 1
}

cd ..

Start-Sleep -Seconds 5

Write-Host "[OK] Contenedores activos" -ForegroundColor Green

# -------------------------------
# 2. BACKEND DEPENDENCIAS
# -------------------------------
Write-Host "`n[2/5] Instalando dependencias backend..." -ForegroundColor Cyan

cd backend
pip install -r requirements.txt | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] pip install falló" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Dependencias listas" -ForegroundColor Green

# -------------------------------
# 3. INICIAR BACKEND
# -------------------------------
Write-Host "`n[3/5] Iniciando backend (Flask app.py)..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "cd backend; python app.py"

Start-Sleep -Seconds 3

Write-Host "[OK] Backend ejecutándose" -ForegroundColor Green

# -------------------------------
# 4. FRONTEND
# -------------------------------
Write-Host "`n[4/5] Abriendo frontend..." -ForegroundColor Cyan

Start-Process "frontend/index.html"

Write-Host "[OK] Frontend abierto" -ForegroundColor Green

# -------------------------------
# 5. RESUMEN DEMO
# -------------------------------
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "        SISTEMA LISTO PARA DEMO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nSERVICIOS:" -ForegroundColor Yellow
Write-Host " - IBM MQ: http://localhost:1414"
Write-Host " - MariaDB: activo en Docker"
Write-Host " - Backend: http://localhost:5000 (si Flask)"
Write-Host " - Frontend: abierto en navegador"

Write-Host "`nFLUJO DEMO:" -ForegroundColor Yellow
Write-Host " Frontend → Flask → IBM MQ → MariaDB"

Write-Host "`nTIP:" -ForegroundColor DarkGray
Write-Host "Si algo falla, revisa docker-compose logs"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "        FIN DEL BOOT DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan