# Guide: Configuration OAuth Zoho Books pour le Bilan Financier 2025

## 🎯 Objectif

Configurer l'authentification OAuth Zoho Books pour permettre au script Python `generate_financial_report_2025.py` de récupérer automatiquement les données financières.

## 📋 Prérequis

- Compte Zoho Books actif
- Accès administrateur à votre organisation Zoho
- Données financières 2025 dans Zoho Books

## 🔧 Étapes de Configuration

### Étape 1: Créer une Application Zoho

1. Allez sur **Zoho API Console**: https://api-console.zoho.eu/ (ou .com selon votre région)

2. Cliquez sur **"Add Client"** → **"Self Client"**

3. Remplissez les informations:
   - **Client Name**: `Atlas Bilan Financier`
   - **Homepage URL**: `https://localhost`
   - **Authorized Redirect URIs**: `https://localhost`

4. Cliquez sur **"Create"**

5. **Notez** le `Client ID` et le `Client Secret` affichés

### Étape 2: Générer le Code d'Autorisation

1. Construisez l'URL d'autorisation (remplacez `YOUR_CLIENT_ID` et `YOUR_REGION`):

```
https://accounts.zoho.eu/oauth/v2/auth?scope=ZohoBooks.fullaccess.all&client_id=YOUR_CLIENT_ID&response_type=code&access_type=offline&redirect_uri=https://localhost
```

Pour la région US, utilisez `.com` au lieu de `.eu`

2. Ouvrez cette URL dans votre navigateur

3. Connectez-vous à votre compte Zoho et **autorisez** l'application

4. Vous serez redirigé vers `https://localhost?code=XXXXX`

5. **Copiez le code** dans l'URL (la partie après `code=`)

### Étape 3: Échanger le Code contre un Refresh Token

Utilisez PowerShell pour faire l'appel API:

```powershell
$clientId = "VOTRE_CLIENT_ID"
$clientSecret = "VOTRE_CLIENT_SECRET"
$code = "VOTRE_CODE_AUTORISATION"
$region = "eu"  # ou "com"

$body = @{
    code = $code
    client_id = $clientId
    client_secret = $clientSecret
    redirect_uri = "https://localhost"
    grant_type = "authorization_code"
}

$response = Invoke-RestMethod -Uri "https://accounts.zoho.$region/oauth/v2/token" -Method Post -Body $body

Write-Host "Refresh Token: $($response.refresh_token)"
Write-Host "Access Token: $($response.access_token)"
```

6. **Notez le `refresh_token`** - c'est le plus important!

### Étape 4: Obtenir l'Organization ID

1. Connectez-vous à **Zoho Books**: https://books.zoho.eu/

2. Allez dans **Settings** → **Organization Profile**

3. L'**Organization ID** est affiché dans l'URL ou dans la page

   Exemple d'URL: `https://books.zoho.eu/app/123456789#/settings/organization`
   
   L'Organization ID est `123456789`

### Étape 5: Configurer le fichier .env

Ouvrez le fichier `.env` à la racine du projet et ajoutez:

```bash
# Zoho Books OAuth Configuration
ZOHO_CLIENT_ID=votre_client_id_ici
ZOHO_CLIENT_SECRET=votre_client_secret_ici
ZOHO_REFRESH_TOKEN=votre_refresh_token_ici
ZOHO_ORG_ID=votre_organization_id_ici
ZOHO_REGION=eu
```

**Important:** Remplacez toutes les valeurs par vos credentials réels.

### Étape 6: Tester la Configuration

```powershell
cd "c:\Users\ranai\Documents\Atlas - Copie"
python execution/verify_zoho_books.py
```

Vous devriez voir:
```
✅ Connexion Zoho Books réussie
Organization: Ran.AI Agency
```

### Étape 7: Générer le Bilan Financier

```powershell
python execution/generate_financial_report_2025.py
```

Le rapport sera généré dans `.tmp/bilan_financier_2025.md`

## 🔒 Sécurité

- ⚠️ **Ne commitez JAMAIS le fichier `.env`** (il est déjà dans `.gitignore`)
- 🔑 Le `refresh_token` ne expire pas (sauf inactivité de 1 an)
- 🔄 L'`access_token` est régénéré automatiquement par le script

## ❓ Dépannage

### Erreur: "invalid_code"
- Le code d'autorisation a expiré (valide 60 secondes)
- Recommencez l'Étape 2

### Erreur: "invalid_client"
- Vérifiez le `Client ID` et `Client Secret`
- Assurez-vous d'utiliser la bonne région (.eu vs .com)

### Erreur: "invalid oauth token"
- Le `refresh_token` a expiré
- Régénérez un nouveau token (Étapes 2-3)

### Erreur: "organization_id not found"
- Vérifiez l'`Organization ID` dans Zoho Books
- Assurez-vous d'avoir accès à cette organisation

## 📚 Ressources

- [Zoho OAuth Documentation](https://www.zoho.com/accounts/protocol/oauth.html)
- [Zoho Books API](https://www.zoho.com/books/api/v3/)
- [API Console](https://api-console.zoho.eu/)

## ✅ Checklist

- [ ] Application Zoho créée
- [ ] Client ID et Client Secret obtenus
- [ ] Code d'autorisation généré
- [ ] Refresh Token obtenu
- [ ] Organization ID trouvé
- [ ] Fichier `.env` configuré
- [ ] Test de connexion réussi
- [ ] Bilan financier généré

---

**Besoin d'aide?** Demandez-moi à n'importe quelle étape!
