# Atlas Cloud Interface

## Objectif
Exposer l'interface Atlas (LibreChat) sur internet pour y acceder depuis n'importe quel appareil (PC, mobile).

## Architecture

```
[Mobile/PC] --> [atlas.ran-ai-agency.ca] --> [Cloudflare Tunnel] --> [Docker LibreChat local]
```

## Composants

| Composant | Description |
|-----------|-------------|
| LibreChat | Interface web (Docker, port 3080) |
| Cloudflare Tunnel | Expose localhost sur internet |
| cloudflared | Client tunnel sur Windows |

## URLs

- **Production:** https://atlas.ran-ai-agency.ca (quand DNS actif)
- **Temporaire:** Genere par `cloudflared tunnel --url http://localhost:3080`
- **Local:** http://localhost:3080

## Fichiers de configuration

| Fichier | Chemin |
|---------|--------|
| Config tunnel | `C:\Users\ranai\.cloudflared\config.yml` |
| Credentials | `C:\Users\ranai\.cloudflared\f6897cdb-f41b-46f7-b761-89efe318c8b8.json` |
| Certificat | `C:\Users\ranai\.cloudflared\cert.pem` |
| Docker Compose | `ui/docker-compose.yml` |
| LibreChat config | `ui/librechat.yaml` |

## Commandes utiles

### Demarrer LibreChat
```powershell
cd "c:\Users\ranai\Documents\Atlas - Final (VSD AntiGravity)\ui"
docker-compose up -d
```

### Demarrer le tunnel (manuel)
```powershell
# Tunnel permanent
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel run atlas

# Tunnel temporaire (URL aleatoire)
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:3080
```

### Script de demarrage
```powershell
.\execution\start_atlas_tunnel.ps1
```

### Voir le statut du tunnel
```powershell
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel list
```

### Arreter le tunnel
```powershell
taskkill /F /IM cloudflared.exe
```

## Installer comme service Windows (demarrage automatique)

```powershell
# Installer le service (en admin)
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" service install

# Demarrer le service
Start-Service cloudflared

# Verifier le statut
Get-Service cloudflared
```

## Securite

1. **Desactiver l'inscription publique** dans `ui/.env`:
   ```
   ALLOW_REGISTRATION=false
   ```

2. **Creer un compte admin** avant de desactiver l'inscription

3. **Cloudflare Access** (optionnel): Ajouter authentification supplementaire via Zero Trust

## Tunnel ID
- **Nom:** atlas
- **ID:** f6897cdb-f41b-46f7-b761-89efe318c8b8

## Prerequis

- Docker Desktop en cours d'execution
- PC allume (le tunnel passe par votre machine)
- Connexion internet stable

## Depannage

### Le tunnel ne demarre pas
1. Verifier que LibreChat tourne: `curl http://localhost:3080`
2. Verifier les credentials: `ls ~/.cloudflared/`
3. Relancer: `cloudflared tunnel run atlas`

### DNS ne resout pas
1. Verifier le statut dans Cloudflare Dashboard
2. Attendre la propagation DNS (jusqu'a 24h)
3. Utiliser le tunnel temporaire en attendant

### Erreur 404
1. Verifier que le hostname dans config.yml correspond au DNS
2. Verifier que localhost:3080 repond
