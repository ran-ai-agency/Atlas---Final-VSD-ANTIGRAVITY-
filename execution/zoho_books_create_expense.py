"""
Script pour créer une dépense dans Zoho Books via MCP Server
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Organisation ID - stocké dans .env
ORGANIZATION_ID = os.getenv("ZOHO_BOOKS_ORGANIZATION_ID", "110002033190")


def call_mcp(method: str, params: dict = None):
    """Appelle le MCP server Zoho Books."""
    url = os.getenv("MCP_ZOHO_BOOKS_URL")
    key = os.getenv("MCP_ZOHO_BOOKS_KEY")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(f"{url}?key={key}", json=payload, headers=headers, timeout=60)
    result = response.json()

    if "error" in result:
        print(f"Erreur MCP: {result['error']}")
        return None

    return result.get("result", {})


def call_tool(tool_name: str, query_params: dict = None, body: dict = None, path_variables: dict = None):
    """Appelle un outil spécifique avec le bon format de paramètres."""
    arguments = {}

    if query_params:
        arguments["query_params"] = query_params
    if body:
        arguments["body"] = body
    if path_variables:
        arguments["path_variables"] = path_variables

    result = call_mcp("tools/call", {
        "name": tool_name,
        "arguments": arguments
    })

    if result:
        content = result.get("content", [])
        for item in content:
            if item.get("type") == "text":
                text = item.get("text", "{}")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    print(f"Réponse: {text[:500]}")
                    return {"raw_text": text}
    return None


def list_bank_accounts(org_id: str):
    """Liste les comptes bancaires."""
    # Note: L'outil "list bank accounts" n'existe pas dans MCP officiel
    # Utiliser "get bank account" à la place (nécessite un bank_account_id)
    result = call_tool("get bank account", query_params={"organization_id": org_id})

    if result:
        accounts = result.get("bankaccounts", [])
        print(f"\n=== COMPTES BANCAIRES ({len(accounts)}) ===")
        for acc in accounts:
            print(f"  [{acc.get('account_id')}] {acc.get('account_name')} ({acc.get('account_type')})")
        return accounts
    return []


def list_chart_of_accounts(org_id: str):
    """Liste le plan comptable."""
    # Note: L'outil "list chart of accounts" n'existe pas dans MCP officiel
    # Utiliser "get chart of account" à la place (singulier, nécessite un account_id)
    result = call_tool("get chart of account", query_params={"organization_id": org_id})

    if result:
        accounts = result.get("chartofaccounts", [])
        print(f"\n=== PLAN COMPTABLE ({len(accounts)} comptes) ===\n")

        # Grouper par type
        by_type = {}
        for acc in accounts:
            acc_type = acc.get("account_type", "other")
            if acc_type not in by_type:
                by_type[acc_type] = []
            by_type[acc_type].append(acc)

        # Afficher les comptes de dépenses
        print("--- COMPTES DE DEPENSES (expense) ---")
        for acc in by_type.get("expense", []):
            name = acc.get("account_name", "").encode('ascii', 'replace').decode('ascii')
            print(f"  [{acc.get('account_id')}] {name}")

        return accounts
    return []


def create_expense(
    org_id: str,
    account_id: str,
    paid_through_account_id: str,
    date: str,
    amount: float,
    vendor_name: str = None,
    description: str = None,
    reference_number: str = None
):
    """Crée une dépense dans Zoho Books."""
    body = {
        "account_id": account_id,
        "paid_through_account_id": paid_through_account_id,
        "date": date,
        "amount": amount,
    }

    if vendor_name:
        body["vendor_name"] = vendor_name
    if description:
        body["description"] = description
    if reference_number:
        body["reference_number"] = reference_number

    print(f"\n=== CRÉATION DE DÉPENSE ===")
    print(f"Body: {json.dumps(body, indent=2)}")

    # ATTENTION: "create expense" n'existe PAS dans MCP officiel
    # Seul "create recurring expense" existe
    # Ce script ne fonctionnera probablement pas
    result = call_tool(
        "create recurring expense",
        query_params={"organization_id": org_id},
        body=body
    )

    if result:
        expense = result.get("expense", {})
        if expense:
            print(f"\n[OK] Depense creee!")
            print(f"  ID: {expense.get('expense_id')}")
            print(f"  Montant: ${expense.get('total')}")
            return expense
        else:
            print(f"\nReponse: {json.dumps(result, indent=2)}")
            return result

    return None


def list_expenses(org_id: str, limit: int = 10):
    """Liste les dépenses récentes."""
    result = call_tool("list expenses", query_params={"organization_id": org_id})

    if result:
        expenses = result.get("expenses", [])
        print(f"\n=== DEPENSES RECENTES ({len(expenses)}) ===")
        for exp in expenses[:limit]:
            name = exp.get("vendor_name", "N/A").encode('ascii', 'replace').decode('ascii')
            print(f"  [{exp.get('expense_id')}] {exp.get('date')} - {name} - ${exp.get('total')} (Ref: {exp.get('reference_number', 'N/A')})")
        return expenses
    return []


def delete_expense(org_id: str, expense_id: str):
    """Supprime une dépense."""
    print(f"\n=== SUPPRESSION DE DEPENSE {expense_id} ===")

    result = call_tool(
        "delete expense",
        query_params={"organization_id": org_id},
        path_variables={"expense_id": expense_id}
    )

    if result:
        print(f"Resultat: {result}")
        return result
    return None


def list_taxes(org_id: str):
    """Liste les taxes disponibles."""
    # ATTENTION: "list_taxes" n'existe PAS dans MCP officiel
    # Il n'y a pas d'équivalent disponible
    print("[WARNING] L'outil 'list_taxes' n'existe pas dans le MCP Zoho Books officiel")
    return []
    # result = call_tool("list_taxes", query_params={"organization_id": org_id})

    if result:
        taxes = result.get("taxes", [])
        print(f"\n=== TAXES DISPONIBLES ({len(taxes)}) ===")
        for tax in taxes:
            name = tax.get("tax_name", "N/A").encode('ascii', 'replace').decode('ascii')
            print(f"  [{tax.get('tax_id')}] {name} - {tax.get('tax_percentage')}%")
        return taxes
    return []


def create_expense_with_tax(
    org_id: str,
    account_id: str,
    paid_through_account_id: str,
    date: str,
    amount: float,
    tax_id: str = None,
    vendor_name: str = None,
    description: str = None,
    reference_number: str = None
):
    """Cree une depense avec taxes dans Zoho Books."""
    body = {
        "account_id": account_id,
        "paid_through_account_id": paid_through_account_id,
        "date": date,
        "amount": amount,
        "is_inclusive_tax": False,
    }

    if tax_id:
        body["tax_id"] = tax_id
    if vendor_name:
        body["vendor_name"] = vendor_name
    if description:
        body["description"] = description
    if reference_number:
        body["reference_number"] = reference_number

    print(f"\n=== CREATION DE DEPENSE ===")
    print(f"Body: {json.dumps(body, indent=2)}")

    # ATTENTION: "create expense" n'existe PAS dans MCP officiel
    # Seul "create recurring expense" existe
    # Ce script ne fonctionnera probablement pas
    result = call_tool(
        "create recurring expense",
        query_params={"organization_id": org_id},
        body=body
    )

    if result:
        expense = result.get("expense", {})
        if expense:
            print(f"\n[OK] Depense creee!")
            print(f"  ID: {expense.get('expense_id')}")
            print(f"  Montant HT: ${expense.get('amount')}")
            print(f"  Taxes: ${expense.get('tax_amount')}")
            print(f"  Total: ${expense.get('total')}")
            return expense
        else:
            print(f"\nReponse: {json.dumps(result, indent=2)}")
            return result

    return None


def check_duplicate(org_id: str, reference_number: str, date: str, amount: float):
    """Verifie si une depense similaire existe deja."""
    result = call_tool("list expenses", query_params={"organization_id": org_id})

    if result:
        expenses = result.get("expenses", [])
        for exp in expenses:
            # Verifier par reference_number
            if exp.get("reference_number") == reference_number:
                print(f"[DOUBLON] Depense avec ref {reference_number} existe deja (ID: {exp.get('expense_id')})")
                return True
            # Verifier par date + montant (approximatif)
            if exp.get("date") == date and abs(float(exp.get("total", 0)) - amount) < 0.01:
                print(f"[DOUBLON POTENTIEL] Depense du {date} pour ${amount} existe deja (ID: {exp.get('expense_id')})")
                return True
    return False


if __name__ == "__main__":
    print("=" * 60)
    print("ZOHO BOOKS - CREATION DEPENSES 2026-01-07")
    print("=" * 60)

    ORG_ID = ORGANIZATION_ID

    # ============================================
    # 1. STATIONNEMENT - Complexe Desjardins
    # ============================================
    print("\n" + "=" * 50)
    print("1. STATIONNEMENT - Complexe Desjardins")
    print("=" * 50)

    # Verifier doublon
    if not check_duplicate(ORG_ID, "MEMI1TESH4", "2026-01-07", 25.00):
        stationnement = create_expense_with_tax(
            org_id=ORG_ID,
            account_id="89554000000000376",  # Frais de deplacement
            paid_through_account_id="89554000000057009",  # RBC MasterCard
            date="2026-01-07",
            amount=25.00,  # Pas de taxe sur stationnement
            tax_id=None,
            vendor_name="Complexe Desjardins",
            description="Stationnement - 514 281 7000",
            reference_number="MEMI1TESH4"
        )

    # ============================================
    # 2. REPAS - Bellucci Altaglio
    # ============================================
    print("\n" + "=" * 50)
    print("2. REPAS - Bellucci Altaglio")
    print("=" * 50)

    # Verifier doublon repas
    if not check_duplicate(ORG_ID, "76502", "2026-01-07", 13.80):
        repas = create_expense_with_tax(
            org_id=ORG_ID,
            account_id="89554000000000406",  # Repas et divertissements
            paid_through_account_id="89554000000057009",  # RBC MasterCard
            date="2026-01-07",
            amount=12.00,  # Sous-total avant taxes
            tax_id="89554000000113107",  # TPS+TVQ Quebec 14.975%
            vendor_name="Bellucci Altaglio",
            description="Repas d'affaires - 150 Rue Sainte-Catherine, Montreal - Caprese Solo",
            reference_number="76502"
        )

    # Verifier doublon pourboire
    if not check_duplicate(ORG_ID, "76502-TIP", "2026-01-07", 1.20):
        pourboire = create_expense_with_tax(
            org_id=ORG_ID,
            account_id="89554000000000406",  # Repas et divertissements
            paid_through_account_id="89554000000057009",  # RBC MasterCard
            date="2026-01-07",
            amount=1.20,  # Pourboire
            tax_id=None,
            vendor_name="Bellucci Altaglio",
            description="Pourboire - Recu #76502",
            reference_number="76502-TIP"
        )

    # ============================================
    # VERIFICATION FINALE
    # ============================================
    print("\n" + "=" * 50)
    print("VERIFICATION FINALE")
    print("=" * 50)
    list_expenses(ORG_ID, limit=6)
