# Bilan Financier 2025 - Guide d'Utilisation avec MCP Servers

## 🔍 Problème Identifié

Le script Python `generate_financial_report_2025.py` ne peut pas utiliser directement les MCP servers car:
- Les MCP servers sont conçus pour les agents IA (Claude/Gemini)
- Ils nécessitent le protocole MCP, pas des appels HTTP directs
- Les clés API dans `ui/.env` sont pour l'interface MCP, pas pour Python

## ✅ Solution: Génération Interactive via Agent

Pour générer le bilan financier 2025, **demandez-moi de récupérer les données** et je le ferai via les MCP servers.

### Commande à utiliser:

```
Générez le bilan financier 2025 en récupérant:
1. Toutes les factures de 2025 depuis Zoho Books
2. Toutes les dépenses de 2025 depuis Zoho Books
3. La liste des clients depuis Zoho Books
```

Je récupérerai les données via les MCP servers et générerai le rapport complet.

## 🔧 Alternative: Configuration OAuth Zoho

Si vous préférez un script Python autonome, vous devez configurer l'authentification OAuth:

### 1. Créer `.env` à la racine

```bash
cd "c:\Users\ranai\Documents\Atlas - Copie"
Copy-Item .env.example .env
```

### 2. Obtenir les Credentials OAuth

1. Allez sur https://api-console.zoho.eu/
2. Créez une application "Self Client"
3. Générez un code d'autorisation avec les scopes:
   ```
   ZohoBooks.fullaccess.all
   ```
4. Échangez le code contre un refresh token
5. Remplissez dans `.env`:
   ```
   ZOHO_CLIENT_ID=votre_client_id
   ZOHO_CLIENT_SECRET=votre_client_secret
   ZOHO_REFRESH_TOKEN=votre_refresh_token
   ZOHO_ORG_ID=votre_organization_id
   ZOHO_REGION=eu
   ```

### 3. Obtenir l'Organization ID

Dans Zoho Books:
- Settings → Organization Profile
- L'ID est affiché dans l'URL ou les paramètres

## 📊 Quelle Approche Préférez-vous?

**Option A (Recommandée)**: Demandez-moi de générer le bilan via MCP servers
- ✅ Pas de configuration supplémentaire
- ✅ Utilise vos MCP servers existants
- ✅ Immédiat

**Option B**: Configurez OAuth pour script Python autonome
- ⚠️ Nécessite configuration OAuth
- ✅ Script réutilisable sans agent
- ⚠️ Plus complexe

---

**Prochaine étape**: Dites-moi quelle option vous préférez!
