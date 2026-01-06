"""
Liste tous les documents dans Zoho WorkDrive via MCP
Utilise le transport HTTP Streamable pour les MCP servers Zoho
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Forcer UTF-8 pour Windows
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()


class ZohoWorkDriveMCP:
    """Client MCP pour Zoho WorkDrive."""

    def __init__(self):
        base_url = os.getenv("MCP_ZOHO_WORKDRIVE_URL")
        key = os.getenv("MCP_ZOHO_WORKDRIVE_KEY")

        if not base_url or not key:
            raise ValueError("MCP_ZOHO_WORKDRIVE_URL et MCP_ZOHO_WORKDRIVE_KEY requis")

        self.url = f"{base_url}?key={key}"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        self.session = requests.Session()
        self.request_id = 0
        self._initialize()

    def _next_id(self):
        self.request_id += 1
        return self.request_id

    def _initialize(self):
        """Initialise la session MCP."""
        init_payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "atlas", "version": "1.0.0"}
            }
        }

        resp = self.session.post(self.url, json=init_payload, headers=self.headers, timeout=30)
        resp.raise_for_status()

        # Envoyer notification initialized
        notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        self.session.post(self.url, json=notif, headers=self.headers, timeout=30)

    def list_tools(self):
        """Liste tous les outils MCP disponibles."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }

        resp = self.session.post(self.url, json=payload, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json().get("result", {}).get("tools", [])

    def call_tool(self, tool_name: str, arguments: dict = None):
        """Appelle un outil MCP."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        }

        resp = self.session.post(self.url, json=payload, headers=self.headers, timeout=60)
        resp.raise_for_status()

        result = resp.json()
        if "error" in result:
            raise Exception(f"Erreur MCP: {result['error']}")

        return result.get("result", {})

    def get_folder_files(self, folder_id: str):
        """Liste les fichiers d'un dossier."""
        return self.call_tool("ZohoWorkdrive_getFolderFiles", {
            "path_variables": {"folder_id": folder_id}
        })

    def get_file_details(self, resource_id: str):
        """Obtient les details d'un fichier ou dossier."""
        return self.call_tool("ZohoWorkdrive_getFileOrFolderDetails", {
            "path_variables": {"resource_id": resource_id}
        })

    def search_files(self, team_id: str, keyword: str):
        """Recherche des fichiers dans une team."""
        return self.call_tool("ZohoWorkdrive_searchTeamFoldersFiles", {
            "path_variables": {"team_id": team_id},
            "query_params": {"keyword": keyword}
        })

    def get_team_folder_info(self, team_folder_id: str):
        """Obtient les infos d'un Team Folder."""
        return self.call_tool("ZohoWorkdrive_getTeamFolderInfo", {
            "path_variables": {"team_folder_id": team_folder_id}
        })


def extract_text_content(result):
    """Extrait le texte du resultat MCP."""
    content = result.get("content", [])
    texts = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            texts.append(item.get("text", ""))
    return "\n".join(texts)


def parse_workdrive_response(text):
    """Parse la reponse WorkDrive et retourne les donnees."""
    try:
        data = json.loads(text)
        return data.get("data", [])
    except json.JSONDecodeError:
        return []


def format_size(size_bytes):
    """Formate une taille en bytes en format lisible."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def list_all_documents():
    """Liste tous les documents dans Zoho WorkDrive."""
    print("=" * 70)
    print("ZOHO WORKDRIVE - LISTE DES DOCUMENTS")
    print("=" * 70)
    print()

    try:
        client = ZohoWorkDriveMCP()
        print("✅ Connexion MCP etablie")
        print()

        # Lire le Team ID depuis .env
        team_id = os.getenv("ZOHO_WORKDRIVE_TEAM_ID")

        if not team_id:
            print("❌ ZOHO_WORKDRIVE_TEAM_ID non defini dans .env")
            return

        # D'abord, obtenir les infos de la team
        print(f"📂 Team ID: {team_id}")
        result = client.get_file_details(team_id)
        text = extract_text_content(result)

        if text:
            data = json.loads(text)
            attrs = data.get("data", {}).get("attributes", {})
            name = attrs.get("name", "?")
            storage = attrs.get("storage_info", {})

            print(f"📋 Team: {name}")
            print(f"   Fichiers: {storage.get('files_count', 0)}")
            print(f"   Dossiers: {storage.get('folders_count', 0)}")
            print(f"   Taille: {storage.get('size', '?')}")
            print()

        # Maintenant, lister le contenu
        # Les Teams ont un endpoint /files pour lister le contenu
        # On va utiliser getTeamFolderInfo pour obtenir les Team Folders

        print("🔍 Exploration de la structure...")
        print()

        # Essayer avec getFolderFiles sur le team ID
        print("📁 Contenu de la racine:")
        list_folder_content(client, team_id, indent=1)

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 70)


def list_folder_content(client, folder_id: str, indent: int = 0, visited: set = None):
    """Liste le contenu d'un dossier."""
    if visited is None:
        visited = set()

    if folder_id in visited:
        return
    visited.add(folder_id)

    prefix = "  " * indent

    try:
        result = client.get_folder_files(folder_id)
        text = extract_text_content(result)

        if text:
            data = json.loads(text)
            items = data.get("data", [])

            if not items:
                print(f"{prefix}(vide)")
                return

            for item in items:
                attrs = item.get("attributes", {})
                name = attrs.get("name", "?")
                item_type = attrs.get("type", "?")
                item_id = item.get("id", "")
                is_folder = attrs.get("is_folder", False)
                size = attrs.get("storage_info", {}).get("size", "")
                modified = attrs.get("modified_time", "")

                # Determiner l'icone selon le type
                if is_folder or item_type in ["folder", "teamfolder", "privatespace"]:
                    icon = "📁"
                    type_label = "Dossier"
                elif item_type == "image":
                    icon = "🖼️"
                    type_label = "Image"
                elif item_type == "document" or attrs.get("extn", "") in ["pdf", "doc", "docx"]:
                    icon = "📄"
                    type_label = "Document"
                elif attrs.get("extn", "") in ["xls", "xlsx", "csv"]:
                    icon = "📊"
                    type_label = "Tableur"
                elif attrs.get("extn", "") in ["ppt", "pptx"]:
                    icon = "📽️"
                    type_label = "Presentation"
                else:
                    icon = "📄"
                    type_label = item_type or "Fichier"

                # Afficher l'element
                print(f"{prefix}{icon} {name}")
                if size:
                    print(f"{prefix}   Taille: {size}")
                if modified:
                    print(f"{prefix}   Modifie: {modified}")
                print(f"{prefix}   ID: {item_id}")
                print()

                # Recurser dans les sous-dossiers
                if (is_folder or item_type in ["folder", "teamfolder"]) and item_id:
                    list_folder_content(client, item_id, indent + 1, visited)

        else:
            # Peut-etre que getFolderFiles ne marche pas pour les teams
            # Essayons avec search
            print(f"{prefix}(utilisation de la recherche...)")

    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "404" in error_msg:
            print(f"{prefix}(acces non autorise ou dossier vide)")
        else:
            print(f"{prefix}❌ Erreur: {e}")


def list_folder(folder_id: str):
    """Liste le contenu d'un dossier specifique."""
    print(f"📂 Contenu du dossier {folder_id}:")
    print()

    try:
        client = ZohoWorkDriveMCP()
        list_folder_content(client, folder_id, indent=0)

    except Exception as e:
        print(f"❌ Erreur: {e}")


def get_details(resource_id: str):
    """Affiche les details d'un fichier ou dossier."""
    print(f"📋 Details de {resource_id}:")
    print()

    try:
        client = ZohoWorkDriveMCP()
        result = client.get_file_details(resource_id)
        text = extract_text_content(result)

        if text:
            data = json.loads(text)
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("  (reponse vide)")

    except Exception as e:
        print(f"❌ Erreur: {e}")


def search(keyword: str):
    """Recherche des fichiers avec un mot-cle."""
    print(f"🔍 Recherche: '{keyword}'")
    print()

    try:
        client = ZohoWorkDriveMCP()
        team_id = os.getenv("ZOHO_WORKDRIVE_TEAM_ID")

        if not team_id:
            print("❌ ZOHO_WORKDRIVE_TEAM_ID requis")
            return

        result = client.search_files(team_id, keyword)
        text = extract_text_content(result)

        if text:
            data = json.loads(text)
            items = data.get("data", [])

            if items:
                print(f"📄 {len(items)} resultat(s):")
                print()

                for item in items:
                    attrs = item.get("attributes", {})
                    name = attrs.get("name", "?")
                    item_id = item.get("id", "")

                    print(f"  📄 {name}")
                    print(f"     ID: {item_id}")
                    print()
            else:
                print("Aucun resultat")
        else:
            print("Reponse vide")

    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        list_all_documents()
    elif args[0] == "--folder" and len(args) > 1:
        list_folder(args[1])
    elif args[0] == "--details" and len(args) > 1:
        get_details(args[1])
    elif args[0] == "--search" and len(args) > 1:
        search(args[1])
    elif args[0] == "--help":
        print("Usage:")
        print("  python zoho_workdrive_list.py                # Liste tous les documents")
        print("  python zoho_workdrive_list.py --folder ID    # Liste un dossier")
        print("  python zoho_workdrive_list.py --details ID   # Details d'un element")
        print("  python zoho_workdrive_list.py --search KEYWORD # Recherche")
    else:
        # Ancien comportement: folder_id en argument direct
        list_folder(args[0])
