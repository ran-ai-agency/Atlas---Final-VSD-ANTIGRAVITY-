"""
Generateur de Bilan Financier 2025 - Ran.AI Agency
Utilise les MCP servers Zoho Books pour recuperer les donnees financieres
"""

import sys
import os
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Ajouter le repertoire parent au path pour importer zoho_client
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zoho_client import ZohoClient


def format_currency(amount):
    """Formate un montant en EUR"""
    return f"{amount:,.2f} EUR".replace(",", " ")


def calculate_percentage(value, total):
    """Calcule un pourcentage"""
    if total == 0:
        return 0
    return (value / total) * 100


def get_quarter(date_str):
    """Determine le trimestre a partir d'une date"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        month = date.month
        if month <= 3:
            return "Q1"
        elif month <= 6:
            return "Q2"
        elif month <= 9:
            return "Q3"
        else:
            return "Q4"
    except:
        return "Unknown"


def generate_financial_report_2025():
    """Genere le bilan financier complet pour 2025"""
    
    print("=" * 80)
    print("GENERATION DU BILAN FINANCIER 2025 - RAN.AI AGENCY")
    print("=" * 80)
    print()
    
    # Initialiser le client Zoho
    print("📡 Connexion a Zoho Books...")
    try:
        client = ZohoClient()
        print("✅ Connexion reussie!")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("\n⚠️  Verifiez vos credentials Zoho dans le fichier .env")
        return
    
    print()
    print("📊 Recuperation des donnees financieres 2025...")
    print()
    
    # ========================================
    # 1. RECUPERATION DES FACTURES
    # ========================================
    print("  → Factures...")
    invoices_2025 = []
    invoices_paid = []
    invoices_unpaid = []
    
    try:
        # Recuperer toutes les factures
        all_invoices = client.books_list_invoices(status="all")
        
        if all_invoices and "invoices" in all_invoices:
            for invoice in all_invoices["invoices"]:
                # Filtrer pour 2025
                invoice_date = invoice.get("date", "")
                if invoice_date.startswith("2025"):
                    invoices_2025.append(invoice)
                    
                    # Separer payees et impayees
                    status = invoice.get("status", "").lower()
                    if status == "paid":
                        invoices_paid.append(invoice)
                    elif status in ["sent", "overdue"]:
                        invoices_unpaid.append(invoice)
        
        print(f"    ✓ {len(invoices_2025)} factures trouvees pour 2025")
        print(f"    ✓ {len(invoices_paid)} factures payees")
        print(f"    ✓ {len(invoices_unpaid)} factures impayees")
    
    except Exception as e:
        print(f"    ⚠️  Erreur lors de la recuperation des factures: {e}")
        invoices_2025 = []
        invoices_paid = []
        invoices_unpaid = []
    
    # ========================================
    # 2. RECUPERATION DES DEPENSES
    # ========================================
    print("  → Depenses...")
    expenses_2025 = []
    
    try:
        all_expenses = client.books_list_expenses(
            from_date="2025-01-01",
            to_date="2025-12-31"
        )
        
        if all_expenses and "expenses" in all_expenses:
            expenses_2025 = all_expenses["expenses"]
        
        print(f"    ✓ {len(expenses_2025)} depenses trouvees pour 2025")
    
    except Exception as e:
        print(f"    ⚠️  Erreur lors de la recuperation des depenses: {e}")
        expenses_2025 = []
    
    # ========================================
    # 3. RECUPERATION DES CLIENTS
    # ========================================
    print("  → Clients...")
    customers = []
    
    try:
        all_customers = client.books_list_customers()
        
        if all_customers and "contacts" in all_customers:
            customers = all_customers["contacts"]
        
        print(f"    ✓ {len(customers)} clients trouves")
    
    except Exception as e:
        print(f"    ⚠️  Erreur lors de la recuperation des clients: {e}")
        customers = []
    
    print()
    print("=" * 80)
    print("CALCULS FINANCIERS")
    print("=" * 80)
    print()
    
    # ========================================
    # CALCULS: CHIFFRE D'AFFAIRES
    # ========================================
    ca_total = sum(float(inv.get("total", 0)) for inv in invoices_paid)
    
    # CA par trimestre
    ca_by_quarter = defaultdict(float)
    for inv in invoices_paid:
        quarter = get_quarter(inv.get("date", ""))
        ca_by_quarter[quarter] += float(inv.get("total", 0))
    
    # CA par mois
    ca_by_month = defaultdict(float)
    for inv in invoices_paid:
        try:
            month = datetime.strptime(inv.get("date", ""), "%Y-%m-%d").strftime("%Y-%m")
            ca_by_month[month] += float(inv.get("total", 0))
        except:
            pass
    
    # ========================================
    # CALCULS: DEPENSES
    # ========================================
    depenses_total = sum(float(exp.get("total", 0)) for exp in expenses_2025)
    
    # Depenses par categorie
    depenses_by_category = defaultdict(float)
    for exp in expenses_2025:
        category = exp.get("account_name", "Non categorise")
        depenses_by_category[category] += float(exp.get("total", 0))
    
    # Depenses par trimestre
    depenses_by_quarter = defaultdict(float)
    for exp in expenses_2025:
        quarter = get_quarter(exp.get("date", ""))
        depenses_by_quarter[quarter] += float(exp.get("total", 0))
    
    # ========================================
    # CALCULS: RENTABILITE
    # ========================================
    marge_brute = ca_total - depenses_total
    taux_marge = calculate_percentage(marge_brute, ca_total) if ca_total > 0 else 0
    ratio_depenses_ca = calculate_percentage(depenses_total, ca_total) if ca_total > 0 else 0
    
    # ========================================
    # CALCULS: CLIENTS
    # ========================================
    # CA par client
    ca_by_customer = defaultdict(float)
    for inv in invoices_paid:
        customer_name = inv.get("customer_name", "Inconnu")
        ca_by_customer[customer_name] += float(inv.get("total", 0))
    
    # Top 10 clients
    top_10_clients = sorted(ca_by_customer.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Panier moyen
    panier_moyen = ca_total / len(ca_by_customer) if len(ca_by_customer) > 0 else 0
    
    # ========================================
    # CALCULS: FACTURATION
    # ========================================
    nb_factures_total = len(invoices_2025)
    nb_factures_payees = len(invoices_paid)
    nb_factures_impayees = len(invoices_unpaid)
    taux_paiement = calculate_percentage(nb_factures_payees, nb_factures_total) if nb_factures_total > 0 else 0
    montant_moyen_facture = ca_total / nb_factures_payees if nb_factures_payees > 0 else 0
    montant_impaye = sum(float(inv.get("total", 0)) for inv in invoices_unpaid)
    
    # ========================================
    # OBJECTIFS (depuis cfo.md)
    # ========================================
    objectif_ca = 500000  # 500K EUR
    objectif_clients = 50
    
    ecart_ca = calculate_percentage(ca_total - objectif_ca, objectif_ca)
    ecart_clients = len(ca_by_customer) - objectif_clients
    
    # ========================================
    # AFFICHAGE CONSOLE
    # ========================================
    print(f"💰 CA Total 2025: {format_currency(ca_total)}")
    print(f"💸 Depenses Totales: {format_currency(depenses_total)}")
    print(f"📈 Marge Brute: {format_currency(marge_brute)} ({taux_marge:.1f}%)")
    print(f"👥 Clients Actifs: {len(ca_by_customer)}")
    print(f"🧾 Factures Emises: {nb_factures_total} ({nb_factures_payees} payees, {nb_factures_impayees} impayees)")
    print()
    
    # ========================================
    # GENERATION DU RAPPORT MARKDOWN
    # ========================================
    print("=" * 80)
    print("GENERATION DU RAPPORT")
    print("=" * 80)
    print()
    
    report_path = Path(__file__).parent.parent / ".tmp" / "bilan_financier_2025.md"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Bilan Financier 2025 - Ran.AI Agency\n\n")
        f.write(f"**Période**: 01/01/2025 - 31/12/2025\n")
        f.write(f"**Généré le**: {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n")
        f.write(f"**Source**: Zoho Books (via MCP)\n\n")
        f.write("---\n\n")
        
        # SYNTHESE EXECUTIVE
        f.write("## 📊 Synthèse Exécutive\n\n")
        f.write("| Indicateur | Valeur | Objectif 2025 | Écart |\n")
        f.write("|------------|--------|---------------|-------|\n")
        f.write(f"| CA Total | {format_currency(ca_total)} | {format_currency(objectif_ca)} | {ecart_ca:+.1f}% |\n")
        f.write(f"| Dépenses Totales | {format_currency(depenses_total)} | - | - |\n")
        f.write(f"| Marge Brute | {format_currency(marge_brute)} | - | - |\n")
        f.write(f"| Taux de Marge | {taux_marge:.1f}% | - | - |\n")
        f.write(f"| Nombre de Clients | {len(ca_by_customer)} | {objectif_clients} | {ecart_clients:+d} |\n\n")
        f.write("---\n\n")
        
        # CHIFFRE D'AFFAIRES
        f.write("## 💰 Chiffre d'Affaires\n\n")
        f.write(f"### CA Total: {format_currency(ca_total)}\n\n")
        
        f.write("### Évolution Trimestrielle\n\n")
        f.write("| Trimestre | CA | % du Total |\n")
        f.write("|-----------|-----|------------|\n")
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            ca_q = ca_by_quarter.get(quarter, 0)
            pct = calculate_percentage(ca_q, ca_total)
            f.write(f"| {quarter} 2025 | {format_currency(ca_q)} | {pct:.1f}% |\n")
        f.write("\n")
        
        f.write("### Évolution Mensuelle\n\n")
        f.write("| Mois | CA |\n")
        f.write("|------|-----|\n")
        for month in sorted(ca_by_month.keys()):
            f.write(f"| {month} | {format_currency(ca_by_month[month])} |\n")
        f.write("\n---\n\n")
        
        # DEPENSES
        f.write("## 💸 Dépenses\n\n")
        f.write(f"### Dépenses Totales: {format_currency(depenses_total)}\n\n")
        
        if depenses_by_category:
            f.write("### Par Catégorie\n\n")
            f.write("| Catégorie | Montant | % du Total |\n")
            f.write("|-----------|---------|------------|\n")
            for category, amount in sorted(depenses_by_category.items(), key=lambda x: x[1], reverse=True):
                pct = calculate_percentage(amount, depenses_total)
                f.write(f"| {category} | {format_currency(amount)} | {pct:.1f}% |\n")
            f.write("\n")
        
        f.write("### Par Trimestre\n\n")
        f.write("| Trimestre | Dépenses |\n")
        f.write("|-----------|----------|\n")
        for quarter in ["Q1", "Q2", "Q3", "Q4"]:
            f.write(f"| {quarter} 2025 | {format_currency(depenses_by_quarter.get(quarter, 0))} |\n")
        f.write("\n---\n\n")
        
        # RENTABILITE
        f.write("## 📈 Rentabilité\n\n")
        f.write(f"- **Marge Brute**: {format_currency(marge_brute)}\n")
        f.write(f"- **Taux de Marge**: {taux_marge:.1f}%\n")
        f.write(f"- **Ratio Dépenses/CA**: {ratio_depenses_ca:.1f}%\n\n")
        f.write("---\n\n")
        
        # ANALYSE CLIENTS
        f.write("## 👥 Analyse Clients\n\n")
        
        if top_10_clients:
            f.write("### Top 10 Clients par CA\n\n")
            f.write("| Rang | Client | CA 2025 | % du CA Total |\n")
            f.write("|------|--------|---------|---------------|\n")
            for i, (client, ca) in enumerate(top_10_clients, 1):
                pct = calculate_percentage(ca, ca_total)
                f.write(f"| {i} | {client} | {format_currency(ca)} | {pct:.1f}% |\n")
            f.write("\n")
        
        f.write("### Statistiques Clients\n\n")
        f.write(f"- **Clients actifs**: {len(ca_by_customer)}\n")
        f.write(f"- **Panier moyen**: {format_currency(panier_moyen)}\n\n")
        f.write("---\n\n")
        
        # FACTURATION
        f.write("## 🧾 Facturation\n\n")
        f.write(f"- **Factures émises**: {nb_factures_total}\n")
        f.write(f"- **Factures payées**: {nb_factures_payees} ({taux_paiement:.1f}%)\n")
        f.write(f"- **Factures impayées**: {nb_factures_impayees} ({format_currency(montant_impaye)})\n")
        f.write(f"- **Montant moyen/facture**: {format_currency(montant_moyen_facture)}\n\n")
        f.write("---\n\n")
        
        # PERFORMANCE VS OBJECTIFS
        f.write("## 🎯 Performance vs Objectifs\n\n")
        f.write("| Objectif | Cible | Réalisé | Atteint |\n")
        f.write("|----------|-------|---------|----------|\n")
        
        ca_atteint = "✅" if ca_total >= objectif_ca else "❌"
        f.write(f"| CA Annuel | {format_currency(objectif_ca)} | {format_currency(ca_total)} | {ca_atteint} {ecart_ca:+.1f}% |\n")
        
        clients_atteint = "✅" if len(ca_by_customer) >= objectif_clients else "❌"
        f.write(f"| Nouveaux Clients | {objectif_clients} | {len(ca_by_customer)} | {clients_atteint} {ecart_clients:+d} |\n")
        
        panier_ok = "✅" if 2000 <= panier_moyen <= 10000 else "⚠️"
        f.write(f"| Panier Moyen | 2 000 - 10 000 EUR | {format_currency(panier_moyen)} | {panier_ok} |\n\n")
        f.write("---\n\n")
        
        # RECOMMANDATIONS
        f.write("## 💡 Recommandations pour 2026\n\n")
        
        recommendations = []
        
        if ca_total < objectif_ca:
            gap = objectif_ca - ca_total
            recommendations.append(f"**Accélérer la croissance du CA**: Il manque {format_currency(gap)} pour atteindre l'objectif de 500K EUR. Considérer l'augmentation des efforts commerciaux ou l'ajustement des prix.")
        
        if len(ca_by_customer) < objectif_clients:
            gap_clients = objectif_clients - len(ca_by_customer)
            recommendations.append(f"**Acquisition de nouveaux clients**: {gap_clients} clients supplémentaires nécessaires pour atteindre l'objectif de 50 clients.")
        
        if taux_marge < 30:
            recommendations.append(f"**Optimiser la rentabilité**: Le taux de marge de {taux_marge:.1f}% pourrait être amélioré en réduisant les coûts ou en augmentant les prix.")
        
        if nb_factures_impayees > 0:
            recommendations.append(f"**Améliorer le recouvrement**: {nb_factures_impayees} factures impayées représentant {format_currency(montant_impaye)}. Mettre en place un processus de relance systématique.")
        
        if panier_moyen < 2000:
            recommendations.append(f"**Augmenter le panier moyen**: Le panier moyen de {format_currency(panier_moyen)} est en dessous de la cible. Proposer des offres premium ou des packages.")
        
        if not recommendations:
            recommendations.append("**Maintenir la performance**: Les objectifs sont atteints. Continuer sur cette lancée et envisager des objectifs plus ambitieux pour 2026.")
        
        for i, rec in enumerate(recommendations, 1):
            f.write(f"{i}. {rec}\n\n")
        
        f.write("---\n\n")
        
        # NOTES METHODOLOGIQUES
        f.write("## 📝 Notes Méthodologiques\n\n")
        f.write("- **Source des données**: Zoho Books API (via MCP servers)\n")
        f.write("- **Périmètre**: Toutes les factures et dépenses de 2025\n")
        f.write("- **CA comptabilisé**: Factures payées uniquement\n")
        f.write("- **Devise**: EUR (devise de référence)\n")
        f.write(f"- **Données récupérées**: {len(invoices_2025)} factures, {len(expenses_2025)} dépenses, {len(customers)} clients\n")
    
    print(f"✅ Rapport genere: {report_path}")
    print()
    print("=" * 80)
    print("BILAN FINANCIER 2025 - TERMINE")
    print("=" * 80)
    print()
    print(f"📄 Consultez le rapport complet: {report_path}")
    print()


if __name__ == "__main__":
    generate_financial_report_2025()
