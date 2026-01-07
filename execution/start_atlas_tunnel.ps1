# ===========================================
# Atlas Cloud Tunnel - Script de demarrage
# ===========================================
# Lance le tunnel Cloudflare pour exposer Atlas sur internet
# URL: https://atlas.ran-ai-agency.ca

$cloudflared = "C:\Program Files (x86)\cloudflared\cloudflared.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ATLAS CLOUD TUNNEL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier que cloudflared est installe
if (!(Test-Path $cloudflared)) {
    Write-Host "ERREUR: cloudflared n'est pas installe!" -ForegroundColor Red
    Write-Host "Installer avec: winget install cloudflare.cloudflared" -ForegroundColor Yellow
    exit 1
}

# Verifier que Docker/LibreChat tourne
$response = $null
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3080" -UseBasicParsing -TimeoutSec 5
} catch {
    Write-Host "ERREUR: LibreChat n'est pas accessible sur localhost:3080" -ForegroundColor Red
    Write-Host "Lancer d'abord: cd ui && docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "LibreChat OK (localhost:3080)" -ForegroundColor Green
Write-Host ""

# Choix du mode
Write-Host "Choisir le mode:" -ForegroundColor Yellow
Write-Host "  1. Tunnel permanent (atlas.ran-ai-agency.ca)" -ForegroundColor White
Write-Host "  2. Tunnel temporaire (URL aleatoire)" -ForegroundColor White
Write-Host ""
$choice = Read-Host "Votre choix (1/2)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Demarrage du tunnel permanent..." -ForegroundColor Yellow
    Write-Host "URL: https://atlas.ran-ai-agency.ca" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Appuyez sur Ctrl+C pour arreter" -ForegroundColor Gray
    & $cloudflared tunnel run atlas
} else {
    Write-Host ""
    Write-Host "Demarrage du tunnel temporaire..." -ForegroundColor Yellow
    Write-Host "L'URL s'affichera ci-dessous" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Appuyez sur Ctrl+C pour arreter" -ForegroundColor Gray
    & $cloudflared tunnel --url http://localhost:3080
}
