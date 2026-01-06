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
    result = call_tool("ZohoBooks_list_bank_accounts", query_params={"organization_id": org_id})

    if result:
        accounts = result.get("bankaccounts", [])
        print(f"\n=== COMPTES BANCAIRES ({len(accounts)}) ===")
        for acc in accounts:
            print(f"  [{acc.get('account_id')}] {acc.get('account_name')} ({acc.get('account_type')})")
        return accounts
    return []


def list_chart_of_accounts(org_id: str):
    """Liste le plan comptable."""
    result = call_tool("ZohoBooks_list_chart_of_accounts", query_params={"organization_id": org_id})

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

    result = call_tool(
        "ZohoBooks_create_expense",
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
    result = call_tool("ZohoBooks_list_expenses", query_params={"organization_id": org_id})

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
        "ZohoBooks_delete_expense",
        query_params={"organization_id": org_id},
        path_variables={"expense_id": expense_id}
    )

    if result:
        print(f"Resultat: {result}")
        return result
    return None


def list_taxes(org_id: str):
    """Liste les taxes disponibles."""
    result = call_tool("ZohoBooks_list_taxes", query_params={"organization_id": org_id})

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

    result = call_tool(
        "ZohoBooks_create_expense",
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


if __name__ == "__main__":
    print("=" * 60)
    print("ZOHO BOOKS - CREATION DEPENSE POULET ROUGE")
    print("=" * 60)

    ORG_ID = ORGANIZATION_ID

    # Recu Poulet Rouge - 2026-01-06:
    # Sous-total: $38.58
    # TPS (5%): $1.93
    # TVQ (9.975%): $3.85
    # Total avant pourboire: $44.36
    # Pourboire: $3.86
    # Total paye: $48.22

    # 1. Depense principale avec TPS+TVQ
    print("\n1. Creation depense repas avec taxes...")
    expense = create_expense_with_tax(
        org_id=ORG_ID,
        account_id="89554000000000406",  # Repas et divertissements
        paid_through_account_id="89554000000057009",  # RBC MasterCard
        date="2026-01-06",
        amount=38.58,  # Sous-total avant taxes
        tax_id="89554000000113107",  # TPS+TVQ Quebec 14.975%
        vendor_name="Poulet Rouge Ile Perrot",
        description="Repas d'affaires - Recu #21706",
        reference_number="21706"
    )

    # 2. Depense pour le pourboire (sans taxe)
    print("\n2. Creation depense pourboire...")
    pourboire = create_expense_with_tax(
        org_id=ORG_ID,
        account_id="89554000000000406",  # Repas et divertissements
        paid_through_account_id="89554000000057009",  # RBC MasterCard
        date="2026-01-06",
        amount=3.86,  # Pourboire
        tax_id=None,  # Pas de taxe
        vendor_name="Poulet Rouge Ile Perrot",
        description="Pourboire - Recu #21706",
        reference_number="21706-TIP"
    )

    # Verifier
    print("\n3. Verification...")
    list_expenses(ORG_ID, limit=5)
