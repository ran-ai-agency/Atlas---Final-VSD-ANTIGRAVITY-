"""
Atlas Cliq Webhook - Webhook bidirectionnel pour Zoho Cliq
Permet a Atlas de recevoir et repondre aux messages dans le canal #Atlas
"""

import os
import json
import anthropic
import requests
from datetime import datetime
from typing import Optional, Dict, Any

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ZOHO_CLIQ_MCP_URL = "https://zohocliq-110002203871.zohomcp.ca/mcp/message"
ZOHO_CLIQ_MCP_KEY = os.getenv("ZOHO_CLIQ_MCP_KEY", "9241f481c09d7a572947950e02f06fa5")
ZOHO_CRM_MCP_URL = "https://ranaiagencymcpserver-110002203871.zohomcp.ca/mcp/message"
ZOHO_CRM_MCP_KEY = os.getenv("ZOHO_CRM_MCP_KEY", "24b2eccb52404a48493523ce75c970b5")
ZOHO_BOOKS_MCP_URL = "https://zohobooks-110002203871.zohomcp.ca/mcp/message"
ZOHO_BOOKS_MCP_KEY = os.getenv("ZOHO_BOOKS_MCP_KEY", "83dbcaeb92ce495f6db617540ecc6f90")
ATLAS_CHANNEL_NAME = "atlas"
ZOHO_BOOKS_ORG_ID = "110002033190"

# System prompt pour Atlas
ATLAS_SYSTEM_PROMPT = """Tu es Atlas, l'assistant IA de direction pour Ran.AI Agency.

IMPORTANT: Tu n'es PAS Claude. Tu es Atlas. Ne mentionne JAMAIS Anthropic ou Claude.
Quand on te demande qui tu es, reponds: "Je suis Atlas, votre assistant IA pour Ran.AI Agency."

Date et heure actuelles: {current_date}

Tu reponds aux messages dans Zoho Cliq. Sois concis et utile.

Tu as acces aux donnees:
- Zoho CRM: 39 contacts, 2 deals gagnes (9,100$ total)
- Zoho Books: Finances, factures (organization_id: 110002033190)

Regles:
- Reponds toujours en francais
- Sois concis (messages Cliq doivent etre courts)
- Fournis des informations utiles
- Si tu ne sais pas, dis-le clairement
"""


def call_mcp_tool(mcp_url: str, mcp_key: str, tool_name: str, arguments: Dict) -> Dict:
    """Appelle un outil MCP."""
    url = f"{mcp_url}?key={mcp_key}"
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        },
        "id": 1
    }
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    return response.json()


def get_crm_summary() -> str:
    """Obtient un resume du CRM."""
    result = call_mcp_tool(
        ZOHO_CRM_MCP_URL,
        ZOHO_CRM_MCP_KEY,
        "ZohoCRM_Get_Records",
        {
            "path_variables": {"module_api_name": "Deals"},
            "query_params": {"fields": "Deal_Name,Amount,Stage"}
        }
    )
    try:
        data = json.loads(result["result"]["content"][0]["text"])
        deals = data.get("data", [])
        total = sum(d.get("Amount", 0) or 0 for d in deals)
        won = [d for d in deals if d.get("Stage") == "Closed Won"]
        return f"CRM: {len(deals)} deals, {len(won)} gagnes, {total}$ total"
    except:
        return "CRM: Donnees non disponibles"


def post_to_cliq_channel(message: str, channel_name: str = ATLAS_CHANNEL_NAME) -> Dict:
    """Poste un message dans le canal Atlas."""
    return call_mcp_tool(
        ZOHO_CLIQ_MCP_URL,
        ZOHO_CLIQ_MCP_KEY,
        "Post message in a channel",
        {
            "body": {"text": message},
            "path_variables": {"CHANNEL_UNIQUE_NAME": channel_name}
        }
    )


def generate_atlas_response(user_message: str, user_name: str = "Utilisateur") -> str:
    """Genere une reponse Atlas via Claude."""
    if not ANTHROPIC_API_KEY:
        return "Erreur: Cle API Anthropic non configuree."

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    system = ATLAS_SYSTEM_PROMPT.format(current_date=current_date)

    # Contexte additionnel si necessaire
    context = ""
    if any(word in user_message.lower() for word in ["crm", "contact", "deal", "client", "prospect"]):
        context = f"\n\nContexte CRM: {get_crm_summary()}"

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,  # Court pour Cliq
        system=system + context,
        messages=[
            {"role": "user", "content": f"{user_name} dit: {user_message}"}
        ]
    )

    return message.content[0].text


def handle_cliq_message(payload: Dict) -> Dict:
    """Gere un message entrant de Zoho Cliq."""
    try:
        # Extraire les informations du message
        message_text = payload.get("message", {}).get("text", "")
        user_name = payload.get("sender", {}).get("name", "Utilisateur")
        chat_id = payload.get("chat", {}).get("id", "")

        # Ignorer les messages vides ou de bot
        if not message_text or payload.get("sender", {}).get("type") == "bot":
            return {"status": "ignored"}

        # Generer la reponse Atlas
        response = generate_atlas_response(message_text, user_name)

        # Poster la reponse dans le canal
        result = post_to_cliq_channel(response)

        return {
            "status": "success",
            "user_message": message_text,
            "atlas_response": response[:200] + "..." if len(response) > 200 else response
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================
# Modal Webhook Endpoint
# ============================================

try:
    import modal

    app = modal.App("atlas-cliq-webhook")

    image = modal.Image.debian_slim().pip_install(
        "anthropic",
        "requests"
    )

    @app.function(
        image=image,
        secrets=[modal.Secret.from_name("atlas-secrets")]
    )
    @modal.web_endpoint(method="POST")
    def atlas_webhook(payload: Dict) -> Dict:
        """Webhook endpoint pour recevoir les messages Cliq."""
        return handle_cliq_message(payload)

    @app.function(
        image=image,
        secrets=[modal.Secret.from_name("atlas-secrets")]
    )
    @modal.web_endpoint(method="GET")
    def health_check() -> Dict:
        """Health check endpoint."""
        return {
            "status": "ok",
            "service": "Atlas Cliq Webhook",
            "timestamp": datetime.now().isoformat()
        }

except ImportError:
    # Modal non installe - mode standalone
    pass


# ============================================
# Mode Standalone (pour tests locaux)
# ============================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Test avec un message
        test_message = " ".join(sys.argv[1:])
        print(f"Message: {test_message}")
        print("-" * 40)
        response = generate_atlas_response(test_message, "Test User")
        print(f"Atlas: {response}")
        print("-" * 40)

        # Poster dans Cliq
        if input("Poster dans #Atlas? (o/n): ").lower() == "o":
            result = post_to_cliq_channel(response)
            print(f"Resultat: {result}")
    else:
        print("Atlas Cliq Webhook")
        print("Usage: python atlas_cliq_webhook.py <message>")
        print("\nTest de connexion...")

        # Test Cliq
        result = call_mcp_tool(
            ZOHO_CLIQ_MCP_URL,
            ZOHO_CLIQ_MCP_KEY,
            "List all channels",
            {"query_params": {"name": "Atlas"}}
        )
        print(f"Canal Atlas: {result}")
