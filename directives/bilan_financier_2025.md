# Directive: Bilan Financier Annuel 2025

## Objectif
Générer un bilan financier complet de Ran.AI Agency pour l'année 2025, incluant l'analyse du chiffre d'affaires, des dépenses, de la rentabilité, et des performances par client.

## Activation
- **Manuelle**: Prompt demandant un bilan financier annuel
- **Indicateur**: Reponse préfixée par `[CFO - Bilan Annuel]`

## Inputs
- Période: 01/01/2025 - 31/12/2025
- Source de données: Zoho Books
- Objectifs financiers de référence (depuis `directives/roles/cfo.md`)

## Outputs
- Rapport de bilan financier au format Markdown
- Tableaux de synthèse (CA, dépenses, marges)
- Analyses par trimestre
- Top 10 clients par revenus
- Recommandations pour 2026

## Outils Utilisés
- **Zoho Books API**: Récupération des données financières
- **Script**: `execution/generate_financial_report_2025.py`
- **Client**: `execution/zoho_client.py`

## Workflow

### 1. Récupération des Données
```python
# Utiliser zoho_client.py pour récupérer:
- Toutes les factures de 2025 (payées, impayées, annulées)
- Toutes les dépenses de 2025
- Liste des clients avec revenus associés
- État de la trésorerie au 31/12/2025
```

### 2. Calculs Financiers

#### Chiffre d'Affaires
- CA total 2025 (factures payées uniquement)
- CA par trimestre (Q1, Q2, Q3, Q4)
- CA par mois
- Évolution mensuelle (%)

#### Dépenses
- Dépenses totales 2025
- Dépenses par catégorie
- Dépenses par trimestre
- Ratio dépenses/CA

#### Rentabilité
- Marge brute = CA - Dépenses
- Taux de marge = (Marge brute / CA) × 100
- Comparaison avec objectifs

#### Analyse Clients
- Top 10 clients par CA
- Nombre total de clients actifs
- Panier moyen par client
- Clients récurrents vs nouveaux

#### Facturation
- Nombre total de factures émises
- Montant moyen par facture
- Taux de paiement (factures payées / factures émises)
- Factures impayées au 31/12/2025
- Délai moyen de paiement

### 3. Génération du Rapport

Le rapport doit inclure:

```markdown
# Bilan Financier 2025 - Ran.AI Agency

**Période**: 01/01/2025 - 31/12/2025
**Généré le**: [Date]
**Source**: Zoho Books

---

## 📊 Synthèse Exécutive

| Indicateur | Valeur | Objectif 2025 | Écart |
|------------|--------|---------------|-------|
| CA Total | X EUR | 500K EUR | ±X% |
| Dépenses Totales | X EUR | - | - |
| Marge Brute | X EUR | - | - |
| Taux de Marge | X% | - | - |
| Nombre de Clients | X | 50 | ±X |

---

## 💰 Chiffre d'Affaires

### CA Total: X EUR

### Évolution Trimestrielle
| Trimestre | CA | Évolution |
|-----------|-----|-----------|
| Q1 2025 | X EUR | - |
| Q2 2025 | X EUR | +X% |
| Q3 2025 | X EUR | +X% |
| Q4 2025 | X EUR | +X% |

### Évolution Mensuelle
[Tableau ou graphique mensuel]

---

## 💸 Dépenses

### Dépenses Totales: X EUR

### Par Catégorie
| Catégorie | Montant | % du Total |
|-----------|---------|------------|
| [Cat 1] | X EUR | X% |
| [Cat 2] | X EUR | X% |

### Par Trimestre
| Trimestre | Dépenses |
|-----------|----------|
| Q1 2025 | X EUR |
| Q2 2025 | X EUR |
| Q3 2025 | X EUR |
| Q4 2025 | X EUR |

---

## 📈 Rentabilité

- **Marge Brute**: X EUR
- **Taux de Marge**: X%
- **Ratio Dépenses/CA**: X%

---

## 👥 Analyse Clients

### Top 10 Clients par CA
| Rang | Client | CA 2025 | % du CA Total |
|------|--------|---------|---------------|
| 1 | [Client] | X EUR | X% |
| ... | ... | ... | ... |

### Statistiques Clients
- **Clients actifs**: X
- **Nouveaux clients 2025**: X
- **Clients récurrents**: X
- **Panier moyen**: X EUR

---

## 🧾 Facturation

- **Factures émises**: X
- **Factures payées**: X (X%)
- **Factures impayées**: X (X EUR)
- **Montant moyen/facture**: X EUR
- **Délai moyen de paiement**: X jours

---

## 🎯 Performance vs Objectifs

| Objectif | Cible | Réalisé | Atteint |
|----------|-------|---------|---------|
| CA Annuel | 500K EUR | X EUR | ✅/❌ X% |
| Nouveaux Clients | 50 | X | ✅/❌ X% |
| Panier Moyen | 2-10K EUR | X EUR | ✅/❌ |

---

## 💡 Recommandations pour 2026

1. **[Recommandation 1]**: [Détails]
2. **[Recommandation 2]**: [Détails]
3. **[Recommandation 3]**: [Détails]

---

## ⚠️ Points d'Attention

- [Point 1]
- [Point 2]
- [Point 3]

---

## 📝 Notes Méthodologiques

- **Source des données**: Zoho Books API
- **Périmètre**: Toutes les factures et dépenses de 2025
- **CA comptabilisé**: Factures payées uniquement
- **Taux de change**: EUR (devise de référence)
```

## Gestion des Erreurs

- Si aucune donnée 2025 disponible: Alerter l'utilisateur
- Si API Zoho indisponible: Proposer de réessayer
- Si données incomplètes: Mentionner les limitations dans le rapport

## KPIs de Qualité

- Exactitude des calculs (vérification croisée)
- Complétude des données (% de données récupérées)
- Clarté du rapport (structure, visualisations)
- Pertinence des recommandations

## Notes
- Toujours utiliser les données réelles de Zoho Books
- Comparer avec les objectifs définis dans `cfo.md`
- Présenter les données de manière visuelle (tableaux)
- Fournir du contexte et des insights, pas seulement des chiffres
