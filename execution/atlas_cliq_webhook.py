"""
Atlas Cliq Webhook v8.0 - Full Capability Bot with Unipile Integration
Webhook bidirectionnel pour Zoho Cliq avec toutes les capacités Atlas
+ Reception des messages WhatsApp/LinkedIn via Unipile
"""

import os
import json
import anthropic
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List

# Timezone for Montreal/Eastern
TIMEZONE = ZoneInfo("America/Montreal")

# ============================================
# CONFIGURATION
# ============================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ZOHO_CLIQ_MCP_URL = "https://zohocliq-110002203871.zohomcp.ca/mcp/message"
ZOHO_CLIQ_MCP_KEY = os.getenv("ZOHO_CLIQ_MCP_KEY", "9241f481c09d7a572947950e02f06fa5")
ZOHO_CRM_MCP_URL = "https://ranaiagencymcpserver-110002203871.zohomcp.ca/mcp/message"
ZOHO_CRM_MCP_KEY = os.getenv("ZOHO_CRM_MCP_KEY", "24b2eccb52404a48493523ce75c970b5")
ZOHO_BOOKS_MCP_URL = "https://zohobooks-110002203871.zohomcp.ca/mcp/message"
ZOHO_BOOKS_MCP_KEY = os.getenv("ZOHO_BOOKS_MCP_KEY", "fe27da4127ce343dfb37c45a220fa5d7")
ZOHO_MAIL_MCP_URL = "https://zohomail-110002203871.zohomcp.ca/mcp/message"
ZOHO_MAIL_MCP_KEY = os.getenv("ZOHO_MAIL_MCP_KEY", "9659d07223d5ee608ac325269f952b5e")
ZOHO_CALENDAR_MCP_URL = "https://zohocalendar-110002203871.zohomcp.ca/mcp/message"
ZOHO_CALENDAR_MCP_KEY = os.getenv("ZOHO_CALENDAR_MCP_KEY", "e8e366a6a3e982cf1e21fbd9dcb5ee97")
ZOHO_PROJECTS_MCP_URL = "https://zohoprojects-110002203871.zohomcp.ca/mcp/message"
ZOHO_PROJECTS_MCP_KEY = os.getenv("ZOHO_PROJECTS_MCP_KEY", "46a30b92be8110df324506e2a2f91cbb")
ZOHO_PROJECTS_PORTAL_ID = "ranaivisionagency"

# Zoho WorkDrive MCP
ZOHO_WORKDRIVE_MCP_URL = "https://zohoworkdrive-110002203871.zohomcp.ca/mcp/message"
ZOHO_WORKDRIVE_MCP_KEY = os.getenv("ZOHO_WORKDRIVE_MCP_KEY", "73c9965dfb3795e9c2956344eaee90f6")
ZOHO_WORKDRIVE_TEAM_ID = "joftg5092ea79ef2a431981e41d791cfe5f40"

# Notion API
NOTION_API_TOKEN = os.getenv("MCP_NOTION_TOKEN", "")
NOTION_API_URL = "https://api.notion.com/v1"

ATLAS_CHANNEL_NAME = "atlas"
ZOHO_BOOKS_ORG_ID = "110002033190"

# Configuration multi-comptes email
# Compte principal Zoho
ZOHO_MAIL_ACCOUNT_ID = "219196000000002002"
ZOHO_MAIL_INBOX_FOLDER_ID = "219196000000002014"
ZOHO_MAIL_SPAM_FOLDER_ID = "219196000000002024"
ZOHO_MAIL_NEWSLETTER_FOLDER_ID = "219196000000003011"

# Compte Gmail (ranai.vision.agency@gmail.com) via IMAP
GMAIL_ACCOUNT_ID = "219196000000072002"
GMAIL_INBOX_FOLDER_ID = "219196000000068020"

# Liste de tous les comptes a surveiller pour les emails
ALL_EMAIL_ACCOUNTS = [
    {"id": "219196000000002002", "inbox": "219196000000002014", "name": "Zoho Principal"},
    {"id": "219196000000072002", "inbox": "219196000000068020", "name": "Gmail ranai.vision.agency"},
]

# Unipile Configuration
UNIPILE_API_URL = "https://api24.unipile.com:15414"
UNIPILE_API_KEY = os.getenv("UNIPILE_API_KEY", "sJxSM/6I.XGPuToXO8lJPtHiz86QqO22yw4GNCoLvdjM/5ZnLosY=")
UNIPILE_WHATSAPP_ACCOUNT_ID = "-lsiQxxcSsam7n9uloiTxQ"
UNIPILE_LINKEDIN_ACCOUNT_ID = "3GmkExQJRZmAQER1uAVC7w"

# viaSocket MCP for Facebook Messenger (Page Agence Ran.AI)
VIASOCKET_MCP_URL = "https://mcp.viasocket.com/mcp/696805f08e4418552628bd68-58029"

# ============================================
# SYSTEM PROMPT
# ============================================
ATLAS_SYSTEM_PROMPT = """Tu es Atlas, l'assistant IA de direction pour Ran.AI Agency.
Tu n'es PAS Claude. Tu es Atlas. Ne mentionne JAMAIS Anthropic ou Claude.
Date: {current_date} (2026)

=== FORMAT REPONSE ===
1. TOUJOURS commencer par le role: [CEO], [CFO], [CMO], [CTO], [COO] ou [EA]
2. Etre CONCIS et DIRECT - pas d'explications techniques
3. Presenter les donnees de facon claire et lisible
4. Ne JAMAIS dire "je ne peux pas acceder" ou "j'aurais besoin" - presenter ce qui EST disponible

=== ROLES ===
[CEO] Strategie, vision, decisions | [CFO] Finance, factures | [CMO] Marketing
[CTO] Tech, Notion, code | [COO] Operations | [EA] Emails, calendrier, taches

=== REGLES STRICTES ===
- Presenter UNIQUEMENT les donnees dans "DONNEES RECUPEREES"
- Ne JAMAIS inventer de donnees
- Ne JAMAIS afficher de code XML ou technique
- Reponses en francais, courtes et utiles
- Si l'utilisateur demande plus de details, proposer d'approfondir
"""


# ============================================
# MCP HELPER
# ============================================
def call_mcp_tool(mcp_url: str, mcp_key: str, tool_name: str, arguments: Dict, timeout: int = 30) -> Dict:
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
    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=timeout)
    return response.json()


def extract_mcp_text(result: Dict, max_chars: int = 8000) -> str:
    """Extract text content from MCP result."""
    try:
        content = result.get("result", {}).get("content", [])
        text = ""
        for item in content:
            if item.get("type") == "text":
                text += item.get("text", "")
        return text[:max_chars] if text else "Aucune donnee."
    except Exception as e:
        return f"Erreur: {str(e)}"


def get_conversation_history(chat_id: str, limit: int = 10) -> List[Dict]:
    """
    Fetch recent conversation history from Zoho Cliq.
    
    Args:
        chat_id: The chat/channel ID
        limit: Number of messages to fetch
    
    Returns:
        List of message dicts with 'sender' and 'text'
    """
    try:
        result = call_mcp_tool(
            ZOHO_CLIQ_MCP_URL,
            ZOHO_CLIQ_MCP_KEY,
            "ZohoCliq_Get_Messages",
            {
                "path_variables": {"chat_id": chat_id},
                "query_params": {"limit": limit}
            },
            timeout=3
        )
        
        raw_text = extract_mcp_text(result, max_chars=20000)
        
        if raw_text and raw_text != "Aucune donnee.":
            data = json.loads(raw_text)
            messages = data.get("data", [])
            
            history = []
            for msg in messages[-limit:]:
                sender = msg.get("sender", {}).get("name", "Unknown")
                text = msg.get("text", "")
                if text:
                    history.append({"sender": sender, "text": text})
            
            return history
    except Exception as e:
        pass
    
    return []


# ============================================
# TOOLS: EMAIL
# ============================================
def tool_read_emails(limit: int = 10) -> str:
    """Read recent emails from all configured accounts (Zoho + Gmail)."""
    all_emails = []

    for account in ALL_EMAIL_ACCOUNTS:
        result = call_mcp_tool(
            ZOHO_MAIL_MCP_URL,
            ZOHO_MAIL_MCP_KEY,
            "ZohoMail_listEmails",
            {
                "path_variables": {"accountId": account["id"]},
                "query_params": {"limit": limit, "folderId": account["inbox"]}
            }
        )
        try:
            text = extract_mcp_text(result, max_chars=50000)
            data = json.loads(text)
            emails = data.get("data", [])
            for e in emails:
                e["_account"] = account["name"]
            all_emails.extend(emails)
        except:
            pass

    # Trier par date (receivedTime) decroissant
    all_emails.sort(key=lambda x: int(x.get("receivedTime", 0)), reverse=True)

    # Formater la sortie
    output = f"Emails recents ({datetime.now(TIMEZONE).strftime('%d/%m/%Y %H:%M')}) - {len(all_emails)} emails:\n"
    output += json.dumps({"status": {"code": 200}, "data": all_emails[:limit]})
    return output


def tool_read_spam(limit: int = 10) -> str:
    """Read spam folder."""
    result = call_mcp_tool(
        ZOHO_MAIL_MCP_URL,
        ZOHO_MAIL_MCP_KEY,
        "ZohoMail_listEmails",
        {
            "path_variables": {"accountId": ZOHO_MAIL_ACCOUNT_ID},
            "query_params": {"limit": limit, "folderId": ZOHO_MAIL_SPAM_FOLDER_ID}
        }
    )
    return f"Dossier Spam:\n{extract_mcp_text(result)}"


def tool_search_emails(keywords: str) -> str:
    """Search emails by keywords across all accounts (Zoho + Gmail)."""
    import re

    # Get keywords as list
    keyword_list = [k.strip() for k in re.split(r'[,\s]+', keywords) if k.strip()]

    if not keyword_list:
        return "Veuillez specifier des mots-cles de recherche."

    # Collect emails from all accounts
    all_emails = []
    for account in ALL_EMAIL_ACCOUNTS:
        result = call_mcp_tool(
            ZOHO_MAIL_MCP_URL,
            ZOHO_MAIL_MCP_KEY,
            "ZohoMail_listEmails",
            {
                "path_variables": {"accountId": account["id"]},
                "query_params": {"limit": 50, "folderId": account["inbox"]}
            }
        )
        try:
            raw_text = extract_mcp_text(result, max_chars=50000)
            data = json.loads(raw_text)
            emails = data.get("data", [])
            for e in emails:
                e["_account"] = account["name"]
            all_emails.extend(emails)
        except:
            pass

    # Filter by keywords
    matches = []
    for email in all_emails:
        subject = (email.get("subject") or "").lower()
        sender = (email.get("sender") or "").lower()
        from_addr = (email.get("fromAddress") or "").lower()

        for kw in keyword_list:
            kw_lower = kw.lower()
            if kw_lower in subject or kw_lower in sender or kw_lower in from_addr:
                matches.append(email)
                break

    if not matches:
        return f"Aucun email trouve avec les mots-cles: {', '.join(keyword_list)}"

    # Sort by received time
    matches.sort(key=lambda x: int(x.get("receivedTime", 0)), reverse=True)

    output = f"=== EMAILS TROUVES ({len(matches)} resultats) ===\n\n"
    for i, email in enumerate(matches[:10], 1):
        subject = email.get("subject", "Sans sujet")[:60]
        sender = email.get("sender", email.get("fromAddress", "Inconnu"))
        account = email.get("_account", "")
        is_read = "" if email.get("isRead") else " [NON LU]"
        output += f"{i}. {subject}{is_read}\n   De: {sender} ({account})\n\n"

    return output


def tool_send_email(to_address: str, subject: str, content: str) -> str:
    """Send an email via Zoho Mail."""
    try:
        result = call_mcp_tool(
            ZOHO_MAIL_MCP_URL,
            ZOHO_MAIL_MCP_KEY,
            "ZohoMail_sendEmail",
            {
                "path_variables": {"accountId": ZOHO_MAIL_ACCOUNT_ID},
                "body": {
                    "toAddress": to_address,
                    "subject": subject,
                    "content": content,
                    "mailFormat": "plaintext"
                }
            }
        )

        raw_text = extract_mcp_text(result)
        if "error" in raw_text.lower():
            return f"Erreur envoi email: {raw_text}"

        return f"Email envoye avec succes a {to_address}!\nSujet: {subject}"

    except Exception as e:
        return f"Erreur envoi email: {str(e)}"


def tool_send_email_parse(user_message: str) -> str:
    """Parse user message to send an email."""
    import re

    # Patterns to extract email components
    # Format: "envoie email a xxx@xxx.com: sujet - contenu"
    # Or: "envoie email a xxx@xxx.com sujet: xxx contenu: xxx"

    user_lower = user_message.lower()

    # Extract email address
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', user_message)
    if not email_match:
        return """Format: "Envoie email a xxx@xxx.com: Sujet - Contenu du message"
Exemple: "Envoie email a client@example.com: Confirmation RDV - Bonjour, je confirme notre rendez-vous de demain." """

    to_address = email_match.group(0)

    # Extract subject and content after the email
    after_email = user_message[email_match.end():].strip()

    # Try pattern: "sujet: xxx contenu: xxx"
    subject_content_match = re.search(r'sujet\s*:\s*(.+?)\s*(?:contenu|message|corps)\s*:\s*(.+)', after_email, re.IGNORECASE | re.DOTALL)

    if subject_content_match:
        subject = subject_content_match.group(1).strip()
        content = subject_content_match.group(2).strip()
    else:
        # Try pattern: ": Sujet - Contenu" or just ": Contenu"
        if after_email.startswith(':'):
            after_email = after_email[1:].strip()

        if ' - ' in after_email:
            parts = after_email.split(' - ', 1)
            subject = parts[0].strip()
            content = parts[1].strip()
        else:
            # No clear separator - use first line as subject
            lines = after_email.split('\n', 1)
            subject = lines[0].strip()[:100]
            content = lines[1].strip() if len(lines) > 1 else lines[0].strip()

    if not subject:
        subject = "Message de Atlas"

    if not content:
        return "Veuillez specifier le contenu du message."

    # Add signature
    content += "\n\n--\nEnvoye via Atlas | Ran.AI Agency"

    return tool_send_email(to_address, subject, content)


# ============================================
# TOOLS: CALENDAR
# ============================================
def tool_read_calendar() -> str:
    """Read calendar for the next 7 days."""
    from datetime import timedelta
    
    today = datetime.now(TIMEZONE)
    start_date = today.strftime("%Y%m%d")
    end_date = (today + timedelta(days=7)).strftime("%Y%m%d")
    
    result = call_mcp_tool(
        ZOHO_CALENDAR_MCP_URL,
        ZOHO_CALENDAR_MCP_KEY,
        "ZohoCalendar_getEventsInRange",
        {
            "query_params": {"start": start_date, "end": end_date}
        }
    )
    
    # Get raw text which contains JSON, increase limit to 100k chars
    raw_text = extract_mcp_text(result, max_chars=100000)
    
    today_str = today.strftime("%d/%m/%Y")
    end_str = (today + timedelta(days=7)).strftime("%d/%m/%Y")
    
    events_list = []
    
    try:
        # Check if we have valid JSON
        if raw_text.strip() and raw_text != "Aucune donnee.":
            data = json.loads(raw_text)
            events = data.get("events", [])
            
            for evt in events:
                title = evt.get("title", "Sans titre")
                loc = evt.get("location", "")
                
                # Times: 20260114T190000-0500
                dt = evt.get("dateandtime", {})
                start_raw = dt.get("start", "")
                end_raw = dt.get("end", "")
                
                # Parse date parts
                if len(start_raw) >= 13:
                    y, m, d = start_raw[:4], start_raw[4:6], start_raw[6:8]
                    h, mn = start_raw[9:11], start_raw[11:13]
                    
                    date_display = f"{d}/{m}"
                    time_display = f"{h}h{mn}"
                    
                    end_display = ""
                    if len(end_raw) >= 13:
                        he, mne = end_raw[9:11], end_raw[11:13]
                        end_display = f"-{he}h{mne}"
                    
                    # Sort key: YYYYMMDDHHMM
                    sort_key = f"{y}{m}{d}{h}{mn}"
                    
                    line = f"- {date_display} {time_display}{end_display} : {title}{f' ({loc})' if loc else ''}"
                    events_list.append((sort_key, line))
                else:
                    events_list.append(("99999999", f"- {title} ({start_raw})"))
    
    except Exception as e:
        return f"Erreur lecture calendrier: {str(e)}"
    
    header = f"=== DONNEES RECUPEREES: AGENDA {today_str} AU {end_str} ===\n"
    
    if not events_list:
        return header + "Aucun evenement trouve dans cette periode."
    
    # Sort by date
    events_list.sort(key=lambda x: x[0])
    formatted_events = "\n".join([x[1] for x in events_list])
    
    footer = "\n\n[FIN DONNEES CALENDRIER]"
    
    return header + formatted_events + footer


# ============================================
# TOOLS: GOOGLE CALENDAR (CREATE EVENTS)
# ============================================
GOOGLE_CALENDAR_REFRESH_TOKEN = os.getenv("GOOGLE_CALENDAR_REFRESH_TOKEN", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")


def get_google_access_token() -> str:
    """Get a fresh Google access token using refresh token."""
    if not GOOGLE_CALENDAR_REFRESH_TOKEN:
        return ""
    
    try:
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": GOOGLE_CALENDAR_REFRESH_TOKEN,
                "grant_type": "refresh_token"
            }
        )
        if response.status_code == 200:
            return response.json().get("access_token", "")
    except:
        pass
    return ""


def tool_create_google_event(title: str, date_str: str, time_str: str, duration_minutes: int = 60, description: str = "") -> str:
    """
    Create an event in Google Calendar.
    
    Args:
        title: Event title
        date_str: Date in format DD/MM/YYYY or YYYY-MM-DD
        time_str: Time in format HH:MM or HHhMM
        duration_minutes: Duration in minutes (default 60)
        description: Event description/notes
    """
    access_token = get_google_access_token()
    if not access_token:
        return "Erreur: Impossible d'obtenir un token Google Calendar. Configuration requise."
    
    # Parse date
    try:
        # Try DD/MM/YYYY format
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts[0]) == 4:  # YYYY/MM/DD
                year, month, day = parts[0], parts[1], parts[2]
            else:  # DD/MM/YYYY
                day, month, year = parts[0], parts[1], parts[2]
        else:  # YYYY-MM-DD
            year, month, day = date_str.split("-")
        
        # Parse time
        time_str = time_str.replace("h", ":").replace("H", ":")
        if ":" in time_str:
            hour, minute = time_str.split(":")[:2]
        else:
            hour, minute = time_str[:2], time_str[2:4] if len(time_str) >= 4 else "00"
        
        # Build datetime
        start_dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
    except Exception as e:
        return f"Erreur parsing date/heure: {str(e)}"
    
    # Create event via Google Calendar API
    event_body = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Montreal"
        },
        "end": {
            "dateTime": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Montreal"
        }
    }
    
    try:
        response = requests.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=event_body,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            return f"✅ Evenement cree avec succes!\n- Titre: {title}\n- Date: {start_dt.strftime('%d/%m/%Y')}\n- Heure: {start_dt.strftime('%Hh%M')} - {end_dt.strftime('%Hh%M')}\n- Lien: {result.get('htmlLink', 'N/A')}"
        else:
            return f"Erreur creation evenement: {response.status_code} - {response.text[:200]}"
    
    except Exception as e:
        return f"Erreur API Google Calendar: {str(e)}"


def search_google_events(query: str = "", date_str: str = "", max_results: int = 10) -> list:
    """
    Search events in Google Calendar.
    
    Args:
        query: Text to search in event titles
        date_str: Date to search (DD/MM/YYYY format)
        max_results: Maximum results to return
    
    Returns:
        List of matching events
    """
    access_token = get_google_access_token()
    if not access_token:
        return []
    
    # Build time range
    today = datetime.now(TIMEZONE)
    
    if date_str:
        try:
            if "/" in date_str:
                parts = date_str.split("/")
                if len(parts) == 2:
                    day, month = parts[0], parts[1]
                    year = str(today.year)
                else:
                    day, month, year = parts[0], parts[1], parts[2]
                search_date = datetime(int(year), int(month), int(day), tzinfo=TIMEZONE)
            else:
                search_date = today
        except:
            search_date = today
        
        time_min = search_date.replace(hour=0, minute=0, second=0).isoformat()
        time_max = search_date.replace(hour=23, minute=59, second=59).isoformat()
    else:
        # Search next 30 days
        time_min = today.isoformat()
        time_max = (today + timedelta(days=30)).isoformat()
    
    params = {
        "timeMin": time_min,
        "timeMax": time_max,
        "maxResults": max_results,
        "singleEvents": "true",
        "orderBy": "startTime"
    }
    
    if query:
        params["q"] = query
    
    try:
        response = requests.get(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers={"Authorization": f"Bearer {access_token}"},
            params=params,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
    except:
        pass
    
    return []


def update_google_event(event_id: str, updates: dict) -> str:
    """
    Update an existing Google Calendar event.
    
    Args:
        event_id: The event ID to update
        updates: Dict with fields to update (summary, description, start, end)
    
    Returns:
        Success/error message
    """
    access_token = get_google_access_token()
    if not access_token:
        return "Erreur: Impossible d'obtenir un token Google Calendar."
    
    try:
        # First get the current event
        response = requests.get(
            f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15
        )
        
        if response.status_code != 200:
            return f"Erreur: Evenement non trouve (ID: {event_id})"
        
        event = response.json()
        
        # Apply updates
        if "summary" in updates:
            event["summary"] = updates["summary"]
        if "description" in updates:
            # Append to existing description
            existing = event.get("description", "")
            if existing:
                event["description"] = existing + "\n\n" + updates["description"]
            else:
                event["description"] = updates["description"]
        if "start_time" in updates:
            # Parse new time and update
            new_time = updates["start_time"]
            current_start = event.get("start", {}).get("dateTime", "")
            if current_start:
                # Keep the date, change the time
                date_part = current_start[:10]  # YYYY-MM-DD
                event["start"]["dateTime"] = f"{date_part}T{new_time}:00"
                # Also update end time (assume same duration)
                current_end = event.get("end", {}).get("dateTime", "")
                if current_end:
                    event["end"]["dateTime"] = f"{date_part}T{new_time}:00"
        
        # Update the event
        response = requests.put(
            f"https://www.googleapis.com/calendar/v3/calendars/primary/events/{event_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=event,
            timeout=15
        )
        
        if response.status_code == 200:
            updated = response.json()
            return f"✅ Evenement mis a jour!\n- Titre: {updated.get('summary', 'N/A')}\n- Lien: {updated.get('htmlLink', 'N/A')}"
        else:
            return f"Erreur mise a jour: {response.status_code} - {response.text[:200]}"
    
    except Exception as e:
        return f"Erreur API: {str(e)}"


def tool_update_event_parse(user_message: str) -> str:
    """
    Parse a message to update a Google Calendar event.
    
    Supported formats:
    - "modifie rdv: SUIVI RBC, ajouter note: Appel confirme"
    - "modifie rdv du 15/01 10h30: changer heure 11h00"
    - "modifier evenement Reunion: nouvelle heure 14h30"
    """
    import re
    
    user_lower = user_message.lower()
    
    # Extract the search criteria and update
    # Pattern: modifie rdv [du DATE]? [TITRE]?: [ACTION]
    
    # Try to find what event to modify
    event_search = ""
    date_search = ""
    update_action = ""
    
    # Look for date pattern
    date_match = re.search(r"du\s+(\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?)", user_lower)
    if date_match:
        date_search = date_match.group(1).replace("-", "/")
    
    # Look for time pattern in search
    time_match = re.search(r"(\d{1,2}[h:]\d{2})", user_lower)
    search_time = time_match.group(1) if time_match else ""
    
    # Extract title/search term (between modifier and the colon before action)
    title_match = re.search(r"(?:modifie|modifier|update)\s+(?:rdv|evenement|event)\s*(?:du\s+\S+\s+)?(?:\d+h\d+\s+)?[:\s]*([^:]+?)(?:,|:|\s+(?:ajouter|changer|nouvelle|nouveau))", user_lower)
    if title_match:
        event_search = title_match.group(1).strip()
    
    # Extract action (after the last colon or action keyword)
    action_match = re.search(r"(?:ajouter\s+note|changer\s+heure|nouvelle\s+heure|nouveau\s+titre|ajouter)[:\s]+(.+)", user_lower)
    if action_match:
        update_action = action_match.group(1).strip()
    
    if not event_search and not date_search:
        return """Format non reconnu. Utilisez:
- "Modifie RDV: [Titre], ajouter note: [votre note]"
- "Modifie RDV du 15/01 10h30: changer heure 11h00"
- "Modifier evenement [Titre]: nouvelle heure 14h30" """
    
    # Search for the event
    events = search_google_events(query=event_search, date_str=date_search, max_results=5)
    
    if not events:
        return f"❌ Aucun evenement trouve correspondant a '{event_search or date_search}'"
    
    # If multiple events, filter by time if provided
    if len(events) > 1 and search_time:
        filtered = []
        search_time_normalized = search_time.replace("h", ":").replace("H", ":")
        for evt in events:
            start = evt.get("start", {}).get("dateTime", "")
            if search_time_normalized[:5] in start:
                filtered.append(evt)
        if filtered:
            events = filtered
    
    if len(events) > 1:
        # Multiple matches - show them
        result = f"⚠️ Plusieurs evenements trouves ({len(events)}). Precisez lequel:\n"
        for i, evt in enumerate(events[:5], 1):
            title = evt.get("summary", "Sans titre")
            start = evt.get("start", {}).get("dateTime", "")[:16]
            result += f"{i}. {title} ({start})\n"
        return result
    
    # Single event found - apply update
    event = events[0]
    event_id = event.get("id")
    
    updates = {}
    
    # Determine what to update
    if "ajouter note" in user_lower or "ajouter" in user_lower:
        updates["description"] = update_action
    elif "changer heure" in user_lower or "nouvelle heure" in user_lower:
        # Parse new time
        new_time_match = re.search(r"(\d{1,2})[h:](\d{2})", update_action)
        if new_time_match:
            new_hour = new_time_match.group(1).zfill(2)
            new_min = new_time_match.group(2)
            updates["start_time"] = f"{new_hour}:{new_min}"
    elif "nouveau titre" in user_lower:
        updates["summary"] = update_action
    else:
        # Default: add as note
        updates["description"] = update_action
    
    return update_google_event(event_id, updates)


# Global variable to store pending event creation
_pending_event_message = ""


def tool_quick_add_event_parse(user_message: str) -> str:
    """
    Parse a message to create a Google Calendar event.
    
    Supported formats:
    - "ajoute rdv: Titre, 15/01/2026, 10h30"
    - "creer evenement: Titre, 15/01, 14h00, 1h30"
    - "rdv: Titre, demain, 9h00"
    """
    import re
    
    # Extract the part after the trigger keyword
    patterns = [
        r"(?:ajoute|creer|créer|nouveau|ajouter)\s*(?:rdv|evenement|événement|event)\s*[:\-]?\s*(.+)",
        r"(?:rdv|evenement|événement)\s*[:\-]\s*(.+)",
    ]
    
    content = None
    for pattern in patterns:
        match = re.search(pattern, user_message.lower())
        if match:
            # Get the original case version
            start_idx = match.start(1)
            content = user_message[start_idx:].strip()
            break
    
    if not content:
        return "Format non reconnu. Utilisez: 'Ajoute RDV: Titre, DD/MM/YYYY, HHhMM'"
    
    # Split by comma
    parts = [p.strip() for p in content.split(",")]
    
    if len(parts) < 3:
        return "Format incomplet. Utilisez: 'Ajoute RDV: Titre, DD/MM/YYYY, HHhMM'"
    
    title = parts[0]
    date_str = parts[1]
    time_str = parts[2]
    duration = 60  # Default 1 hour
    
    # Check for duration in 4th part
    if len(parts) >= 4:
        dur_match = re.search(r"(\d+)\s*(?:h|hr|heure|min|m)", parts[3].lower())
        if dur_match:
            dur_val = int(dur_match.group(1))
            if "min" in parts[3].lower() or "m" in parts[3].lower():
                duration = dur_val
            else:
                duration = dur_val * 60
    
    # Handle "demain", "aujourd'hui"
    today = datetime.now(TIMEZONE)
    if "demain" in date_str.lower():
        tomorrow = today + timedelta(days=1)
        date_str = tomorrow.strftime("%d/%m/%Y")
    elif "aujourd" in date_str.lower():
        date_str = today.strftime("%d/%m/%Y")
    elif len(date_str.split("/")) == 2:
        # DD/MM format - add current year
        date_str = date_str + "/" + str(today.year)
    
    # Call the create function
    return tool_create_google_event(
        title=title,
        date_str=date_str,
        time_str=time_str,
        duration_minutes=duration,
        description=f"Cree par Atlas le {today.strftime('%d/%m/%Y %H:%M')}"
    )


def tool_quick_add_wrapper() -> str:
    """Wrapper that returns instructions for creating events."""
    return """Pour creer un evenement Google Calendar, utilisez ce format:

Exemples:
- "Ajoute RDV: Reunion equipe, 15/01/2026, 14h00"
- "Ajoute RDV: Call client, demain, 10h30"
- "Creer evenement: Formation, 20/01, 9h00, 2h"

[La date peut etre DD/MM/YYYY, DD/MM, 'demain' ou 'aujourd'hui']
[L'heure au format HHhMM ou HH:MM]
[Duree optionnelle: ex. 2h ou 30min]"""


def tool_smart_create_event(user_message: str) -> str:
    """
    Smart event creation that handles natural language.

    Handles formats like:
    - "Créez l'événement FinPima dans mon calendrier à 20h30 jusqu'à 22h00 ce soir"
    - "Ajoute rdv: Titre, date, heure"
    - "Créer reunion Team demain à 14h"
    """
    import re

    user_lower = user_message.lower()
    today = datetime.now(TIMEZONE)

    # Extract title - various patterns
    title = None
    title_patterns = [
        r"(?:evenement|événement|rdv|reunion|réunion)\s+([A-Za-z0-9À-ÿ\-_\s]+?)(?:\s+(?:dans|a|à|le|pour|de|du|ce))",
        r"(?:creer|créer|ajoute|ajouter|creez|créez)\s+(?:l')?(?:evenement|événement|rdv|reunion|réunion)?\s*:?\s*([A-Za-z0-9À-ÿ\-_\s]+?)(?:,|\s+(?:dans|a|à|le|pour|de|du|ce|demain|aujourd))",
        r"(?:creer|créer|ajoute|ajouter|creez|créez)\s+(?:l')?(?:evenement|événement|rdv|reunion|réunion)\s+([A-Za-z0-9À-ÿ\-_]+)",
    ]

    for pattern in title_patterns:
        match = re.search(pattern, user_message, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Clean up title
            title = re.sub(r'\s+(dans|a|à|le|pour|de|du|ce|demain|aujourd).*', '', title, flags=re.IGNORECASE).strip()
            if len(title) > 2:
                break
            title = None

    if not title:
        # Try to find capitalized words as title
        caps_match = re.search(r'([A-Z][A-Za-zÀ-ÿ]+(?:\s+[A-Z][A-Za-zÀ-ÿ]+)*)', user_message)
        if caps_match:
            title = caps_match.group(1)

    if not title:
        title = "Evenement"

    # Extract date
    date_str = today.strftime("%d/%m/%Y")  # Default to today

    if "demain" in user_lower:
        tomorrow = today + timedelta(days=1)
        date_str = tomorrow.strftime("%d/%m/%Y")
    elif "ce soir" in user_lower or "aujourd" in user_lower:
        date_str = today.strftime("%d/%m/%Y")
    else:
        # Try DD/MM/YYYY or DD/MM
        date_match = re.search(r'(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?', user_message)
        if date_match:
            day = date_match.group(1)
            month = date_match.group(2)
            year = date_match.group(3) or str(today.year)
            if len(year) == 2:
                year = "20" + year
            date_str = f"{day}/{month}/{year}"

    # Extract start time
    time_str = None
    time_patterns = [
        r'(?:a|à)\s*(\d{1,2})\s*[hH:]\s*(\d{0,2})',
        r'(\d{1,2})\s*[hH:]\s*(\d{0,2})\s*(?:ce soir|demain|aujourd)',
        r'(\d{1,2})\s*[hH]\s*(\d{0,2})',
    ]

    for pattern in time_patterns:
        match = re.search(pattern, user_message)
        if match:
            hour = match.group(1)
            minute = match.group(2) if match.group(2) else "00"
            time_str = f"{hour}h{minute}"
            break

    if not time_str:
        return "Erreur: Impossible de determiner l'heure. Precisez l'heure (ex: 'a 14h30')"

    # Extract end time or duration
    duration = 60  # Default 1 hour

    # Check for "jusqu'à HH:MM" pattern
    end_match = re.search(r"jusqu['\s]*(?:a|à)\s*(\d{1,2})\s*[hH:]\s*(\d{0,2})", user_message)
    if end_match:
        end_hour = int(end_match.group(1))
        end_minute = int(end_match.group(2)) if end_match.group(2) else 0

        # Calculate start time
        start_hour = int(time_str.replace("h", ":").split(":")[0])
        start_minute = int(time_str.replace("h", ":").split(":")[1]) if ":" in time_str.replace("h", ":") else 0

        # Calculate duration in minutes
        duration = (end_hour * 60 + end_minute) - (start_hour * 60 + start_minute)
        if duration <= 0:
            duration = 60  # Fallback to 1 hour
    else:
        # Check for duration like "1h30" or "2h"
        dur_match = re.search(r'(\d+)\s*[hH]\s*(\d{0,2})\s*(?:de duree|de durée|duree|durée)?', user_message)
        if dur_match and "jusqu" not in user_message:
            hours = int(dur_match.group(1))
            minutes = int(dur_match.group(2)) if dur_match.group(2) else 0
            # Only use this as duration if it looks like a duration spec, not a time
            # Skip if this matches our start time
            if f"{hours}h" not in time_str:
                duration = hours * 60 + minutes

    # Create the event
    return tool_create_google_event(
        title=title,
        date_str=date_str,
        time_str=time_str,
        duration_minutes=duration,
        description=f"Cree par Atlas via Zoho Cliq le {today.strftime('%d/%m/%Y %H:%M')}"
    )


# ============================================
# TOOLS: CRM
# ============================================
def tool_read_deals() -> str:
    """Read CRM deals."""
    result = call_mcp_tool(
        ZOHO_CRM_MCP_URL,
        ZOHO_CRM_MCP_KEY,
        "ZohoCRM_Get_Records",
        {
            "path_variables": {"module_api_name": "Deals"},
            "query_params": {"fields": "Deal_Name,Amount,Stage,Closing_Date"}
        }
    )
    return f"Deals CRM:\n{extract_mcp_text(result)}"


def tool_read_contacts() -> str:
    """Read CRM contacts."""
    result = call_mcp_tool(
        ZOHO_CRM_MCP_URL,
        ZOHO_CRM_MCP_KEY,
        "ZohoCRM_Get_Records",
        {
            "path_variables": {"module_api_name": "Contacts"},
            "query_params": {"fields": "Full_Name,Email,Phone"}
        }
    )
    return f"Contacts CRM:\n{extract_mcp_text(result)}"


# ============================================
# TOOLS: FINANCES
# ============================================
def tool_read_invoices() -> str:
    """Read invoices."""
    result = call_mcp_tool(
        ZOHO_BOOKS_MCP_URL,
        ZOHO_BOOKS_MCP_KEY,
        "ZohoBooks_list_invoices",
        {
            "query_params": {"organization_id": ZOHO_BOOKS_ORG_ID}
        }
    )
    return f"Factures:\n{extract_mcp_text(result)}"


def tool_read_expenses() -> str:
    """Read expenses."""
    result = call_mcp_tool(
        ZOHO_BOOKS_MCP_URL,
        ZOHO_BOOKS_MCP_KEY,
        "ZohoBooks_list_expenses",
        {
            "query_params": {"organization_id": ZOHO_BOOKS_ORG_ID}
        }
    )
    return f"Depenses:\n{extract_mcp_text(result)}"


def tool_financial_summary() -> str:
    """Get complete financial summary."""
    invoices = tool_read_invoices()
    expenses = tool_read_expenses()
    return f"{invoices}\n\n{expenses}"


# ============================================
# TOOLS: ZOHO PROJECTS
# ============================================
def tool_read_projects() -> str:
    """Read all projects from Zoho Projects."""
    result = call_mcp_tool(
        ZOHO_PROJECTS_MCP_URL,
        ZOHO_PROJECTS_MCP_KEY,
        "ZohoProjects_getAllProjects",
        {
            "path_variables": {"portal_id": ZOHO_PROJECTS_PORTAL_ID}
        }
    )
    
    raw_text = extract_mcp_text(result, max_chars=50000)
    
    try:
        data = json.loads(raw_text)
        
        # Handle if data is a list (direct list of projects)
        if isinstance(data, list):
            projects = data
        else:
            projects = data.get("projects", [])
        
        if not projects:
            return "Aucun projet trouve dans Zoho Projects."
        
        result_text = f"=== PROJETS ZOHO ({len(projects)} projets) ===\n\n"
        
        for p in projects:
            name = p.get("name", "Sans nom")
            status = p.get("status", "N/A")
            owner = p.get("owner_name", "N/A")
            
            # Task counts
            task_count = p.get("task_count", {})
            if isinstance(task_count, dict):
                open_tasks = task_count.get("open", 0)
                closed_tasks = task_count.get("closed", 0)
            else:
                open_tasks = "?"
                closed_tasks = "?"
            
            result_text += f"📁 **{name}**\n"
            result_text += f"   - Statut: {status}\n"
            result_text += f"   - Responsable: {owner}\n"
            result_text += f"   - Taches: {open_tasks} ouvertes, {closed_tasks} fermees\n\n"
        
        return result_text
        
    except Exception as e:
        return f"Projets Zoho:\n{raw_text[:2000]}"


def tool_read_tasks(project_id: str = None) -> str:
    """Read tasks from Zoho Projects."""
    # First get projects to find project IDs
    projects_result = call_mcp_tool(
        ZOHO_PROJECTS_MCP_URL,
        ZOHO_PROJECTS_MCP_KEY,
        "ZohoProjects_getAllProjects",
        {
            "path_variables": {"portal_id": ZOHO_PROJECTS_PORTAL_ID}
        }
    )
    
    raw_text = extract_mcp_text(projects_result, max_chars=50000)
    
    try:
        data = json.loads(raw_text)
        
        # Handle if data is a list
        if isinstance(data, list):
            projects = data
        else:
            projects = data.get("projects", [])
        
        if not projects:
            return "Aucun projet trouve."
        
        all_tasks = []
        
        # Get tasks from first 3 projects (to avoid too many API calls)
        for p in projects[:3]:
            pid = p.get("id_string", p.get("id", ""))
            pname = p.get("name", "Sans nom")
            
            if pid:
                tasks_result = call_mcp_tool(
                    ZOHO_PROJECTS_MCP_URL,
                    ZOHO_PROJECTS_MCP_KEY,
                    "ZohoProjects_getTasksByProject",
                    {
                        "path_variables": {
                            "portal_id": ZOHO_PROJECTS_PORTAL_ID,
                            "project_id": pid
                        }
                    }
                )
                
                tasks_text = extract_mcp_text(tasks_result, max_chars=20000)
                try:
                    tasks_data = json.loads(tasks_text)
                    tasks = tasks_data.get("tasks", [])
                    for t in tasks:
                        t["project_name"] = pname
                        all_tasks.append(t)
                except:
                    pass
        
        if not all_tasks:
            return "Aucune tache trouvee dans vos projets."
        
        result_text = f"=== TACHES ZOHO PROJECTS ({len(all_tasks)} taches) ===\n\n"
        
        for t in all_tasks[:20]:  # Limit to 20 tasks
            name = t.get("name", "Sans nom")
            status = t.get("status", {}).get("name", "N/A")
            priority = t.get("priority", "N/A")
            project = t.get("project_name", "N/A")
            due_date = t.get("end_date", "Pas de deadline")
            
            result_text += f"📋 **{name}**\n"
            result_text += f"   - Projet: {project}\n"
            result_text += f"   - Statut: {status} | Priorite: {priority}\n"
            result_text += f"   - Echeance: {due_date}\n\n"
        
        return result_text
        
    except Exception as e:
        return f"Erreur lecture taches: {str(e)}"


def tool_create_task(task_name: str, project_name: str = None, due_date: str = None) -> str:
    """Create a task in Zoho Projects."""
    # First, get the project ID
    projects_result = call_mcp_tool(
        ZOHO_PROJECTS_MCP_URL,
        ZOHO_PROJECTS_MCP_KEY,
        "ZohoProjects_getAllProjects",
        {
            "path_variables": {"portal_id": ZOHO_PROJECTS_PORTAL_ID}
        }
    )

    raw_text = extract_mcp_text(projects_result, max_chars=50000)

    try:
        data = json.loads(raw_text)

        if isinstance(data, list):
            projects = data
        else:
            projects = data.get("projects", [])

        if not projects:
            return "Aucun projet trouve. Impossible de creer la tache."

        # Find the right project
        target_project = None
        if project_name:
            for p in projects:
                if project_name.lower() in p.get("name", "").lower():
                    target_project = p
                    break

        if not target_project:
            # Use first active project
            target_project = projects[0]

        project_id = target_project.get("id_string", target_project.get("id", ""))
        project_display_name = target_project.get("name", "Projet")

        # Create the task
        task_body = {"name": task_name}

        if due_date:
            # Format: MM-DD-YYYY for Zoho
            task_body["end_date"] = due_date

        result = call_mcp_tool(
            ZOHO_PROJECTS_MCP_URL,
            ZOHO_PROJECTS_MCP_KEY,
            "ZohoProjects_createTask",
            {
                "path_variables": {
                    "portal_id": ZOHO_PROJECTS_PORTAL_ID,
                    "project_id": project_id
                },
                "body": task_body
            }
        )

        result_text = extract_mcp_text(result)
        if "error" in result_text.lower():
            return f"Erreur creation tache: {result_text}"

        return f"Tache creee avec succes!\n- Nom: {task_name}\n- Projet: {project_display_name}"

    except Exception as e:
        return f"Erreur creation tache: {str(e)}"


def tool_create_task_parse(user_message: str) -> str:
    """Parse user message to create a task."""
    import re

    user_lower = user_message.lower()

    # Extract task name
    # Patterns: "cree tache: xxx", "nouvelle tache xxx", "ajoute tache xxx dans projet yyy"
    patterns = [
        r"(?:cree|créer|nouvelle|ajoute|ajouter)\s+(?:une\s+)?tache\s*[:\-]?\s*(.+?)(?:\s+dans\s+(?:le\s+)?projet\s+(.+))?$",
        r"tache\s*[:\-]\s*(.+?)(?:\s+projet\s*[:\-]?\s*(.+))?$",
    ]

    task_name = None
    project_name = None

    for pattern in patterns:
        match = re.search(pattern, user_lower, re.IGNORECASE)
        if match:
            task_name = match.group(1).strip()
            if match.lastindex >= 2 and match.group(2):
                project_name = match.group(2).strip()
            break

    if not task_name:
        # Try to extract anything after the trigger word
        simple_match = re.search(r"(?:tache|task)\s*[:\-]?\s*(.+)", user_lower)
        if simple_match:
            task_name = simple_match.group(1).strip()

    if not task_name:
        return """Format: "Cree tache: Nom de la tache"
Exemple: "Cree tache: Preparer presentation client"
Avec projet: "Cree tache: Revue code dans projet ELIA" """

    return tool_create_task(task_name, project_name)


def tool_create_expense(amount: float, description: str, category: str = "Depenses generales") -> str:
    """Create an expense in Zoho Books."""
    try:
        today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

        result = call_mcp_tool(
            ZOHO_BOOKS_MCP_URL,
            ZOHO_BOOKS_MCP_KEY,
            "ZohoBooks_create_expense",
            {
                "query_params": {"organization_id": ZOHO_BOOKS_ORG_ID},
                "body": {
                    "date": today,
                    "amount": amount,
                    "description": description,
                    "account_name": category,
                    "paid_through_account_name": "Petty Cash"
                }
            }
        )

        result_text = extract_mcp_text(result)
        if "error" in result_text.lower():
            return f"Erreur creation depense: {result_text}"

        return f"Depense enregistree!\n- Montant: {amount}$\n- Description: {description}\n- Date: {today}"

    except Exception as e:
        return f"Erreur creation depense: {str(e)}"


def tool_create_expense_parse(user_message: str) -> str:
    """Parse user message to create an expense."""
    import re

    # Patterns: "enregistre depense: 50$ anthropic", "ajoute depense 25$ diner client"
    amount_match = re.search(r'(\d+(?:\.\d+)?)\s*\$?', user_message)
    if not amount_match:
        return """Format: "Enregistre depense: MONTANT$ description"
Exemple: "Enregistre depense: 50$ Abonnement Anthropic"
Ou: "Ajoute depense 25.50$ Diner client" """

    amount = float(amount_match.group(1))

    # Extract description (everything after the amount, cleaned up)
    after_amount = user_message[amount_match.end():].strip()
    after_amount = re.sub(r'^[\$\-:\s]+', '', after_amount)  # Clean leading chars

    if not after_amount:
        # Try before the amount
        before_amount = user_message[:amount_match.start()].strip()
        before_amount = re.sub(r'(?:enregistre|ajoute|nouvelle)\s+depense\s*[:\-]?\s*', '', before_amount, flags=re.IGNORECASE)
        after_amount = before_amount.strip()

    description = after_amount if after_amount else f"Depense du {datetime.now(TIMEZONE).strftime('%d/%m/%Y')}"

    return tool_create_expense(amount, description)


# ============================================
# TOOLS: GR INTERNATIONAL (SUPABASE)
# ============================================
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://zupnncewkclcnigpcsmu.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp1cG5uY2V3a2NsY25pZ3Bjc211Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5OTIyNzksImV4cCI6MjA4MzU2ODI3OX0.k9SP5myoXgzpY3yE570tDYPzvXgD7bLhQ1KchKVNu0k")

# Notion API - Use the same token as NOTION_API_TOKEN
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "") or os.getenv("MCP_NOTION_TOKEN", "")
NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"


def supabase_query(table: str, limit: int = 20, order_by: str = None) -> list:
    """Query Supabase table."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/{table}?limit={limit}"
        if order_by:
            url += f"&order={order_by}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        return []


def tool_gr_meetings() -> str:
    """List GR International meetings from Supabase."""
    meetings = supabase_query("gr_meetings", limit=15, order_by="date.desc")
    if meetings:
        result = f"Reunions GR International ({len(meetings)} prochaines):\n"
        for m in meetings:
            result += f"- {m.get('title', 'N/A')} - {m.get('date', 'N/A')} ({m.get('location', 'N/A')})\n"
        return result
    return "Aucune reunion GR trouvee."


def tool_gr_toolboxes() -> str:
    """List GR International toolboxes from Supabase."""
    toolboxes = supabase_query("gr_toolboxes", limit=15, order_by="date.desc")
    if toolboxes:
        result = f"Boites a outils GR International ({len(toolboxes)} prochaines):\n"
        for t in toolboxes:
            presenter = t.get('presenter', '')
            presenter_str = f" - Anime par: {presenter}" if presenter else ""
            result += f"- {t.get('title', 'N/A')} ({t.get('date', 'N/A')}){presenter_str}\n"
        return result
    return "Aucune boite a outils GR trouvee."


def tool_gr_groups() -> str:
    """List GR International groups from Supabase."""
    groups = supabase_query("gr_groups", limit=20, order_by="name.asc")
    if groups:
        result = f"Groupes GR International ({len(groups)} groupes):\n"
        for g in groups:
            result += f"- {g.get('name', 'N/A')} ({g.get('location', 'N/A')})\n"
        return result
    return "Aucun groupe GR trouve."


def tool_gr_youtube() -> str:
    """List GR International YouTube videos from Supabase."""
    videos = supabase_query("gr_youtube_videos", limit=10, order_by="view_count.desc")
    if videos:
        result = f"Videos YouTube GR International (Top {len(videos)} par vues):\n"
        for v in videos:
            views = v.get('view_count', 0) or 0
            result += f"- {v.get('title', 'N/A')} ({views:,} vues)\n"
        return result
    return "Aucune video GR trouvee."


# ============================================
# TOOLS: NOTION
# ============================================
def notion_headers() -> Dict:
    """Get Notion API headers."""
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_API_VERSION
    }


def notion_search(query: str, filter_type: str = None) -> List[Dict]:
    """Search Notion for pages or databases."""
    if not NOTION_API_KEY:
        return []

    try:
        url = f"{NOTION_BASE_URL}/search"
        payload = {"query": query, "page_size": 20}

        if filter_type:
            payload["filter"] = {"property": "object", "value": filter_type}

        response = requests.post(url, headers=notion_headers(), json=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get("results", [])
    except Exception as e:
        pass
    return []


def notion_get_page_content(page_id: str) -> str:
    """Get the content blocks of a Notion page."""
    if not NOTION_API_KEY:
        return ""

    try:
        url = f"{NOTION_BASE_URL}/blocks/{page_id}/children"
        response = requests.get(url, headers=notion_headers(), timeout=15)

        if response.status_code == 200:
            blocks = response.json().get("results", [])
            content = []

            for block in blocks:
                block_type = block.get("type", "")
                block_data = block.get(block_type, {})

                # Extract text from rich_text
                rich_text = block_data.get("rich_text", [])
                text = "".join([t.get("plain_text", "") for t in rich_text])

                if text:
                    if block_type.startswith("heading"):
                        content.append(f"\n**{text}**")
                    elif block_type == "bulleted_list_item":
                        content.append(f"  - {text}")
                    elif block_type == "numbered_list_item":
                        content.append(f"  • {text}")
                    elif block_type == "to_do":
                        checked = block_data.get("checked", False)
                        marker = "✓" if checked else "○"
                        content.append(f"  {marker} {text}")
                    else:
                        content.append(text)

            return "\n".join(content)
    except Exception as e:
        pass
    return ""


def notion_query_database(database_id: str, filter_dict: Dict = None) -> List[Dict]:
    """Query a Notion database."""
    if not NOTION_API_KEY:
        return []

    try:
        url = f"{NOTION_BASE_URL}/databases/{database_id}/query"
        payload = {"page_size": 50}

        if filter_dict:
            payload["filter"] = filter_dict

        response = requests.post(url, headers=notion_headers(), json=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get("results", [])
    except Exception as e:
        pass
    return []


def extract_notion_title(page: Dict) -> str:
    """Extract the title from a Notion page."""
    props = page.get("properties", {})

    # Try common title field names
    for key in ["Name", "Nom", "Title", "Titre", "name", "title"]:
        if key in props:
            title_data = props[key]
            if title_data.get("type") == "title":
                title_list = title_data.get("title", [])
                if title_list:
                    return title_list[0].get("plain_text", "Sans titre")

    # Fallback: check all properties for title type
    for key, value in props.items():
        if isinstance(value, dict) and value.get("type") == "title":
            title_list = value.get("title", [])
            if title_list:
                return title_list[0].get("plain_text", "Sans titre")

    return "Sans titre"


def extract_notion_property(page: Dict, prop_name: str) -> str:
    """Extract a property value from a Notion page."""
    props = page.get("properties", {})

    if prop_name not in props:
        return ""

    prop = props[prop_name]
    prop_type = prop.get("type", "")

    if prop_type == "rich_text":
        texts = prop.get("rich_text", [])
        return "".join([t.get("plain_text", "") for t in texts])
    elif prop_type == "select":
        select = prop.get("select")
        return select.get("name", "") if select else ""
    elif prop_type == "multi_select":
        return ", ".join([s.get("name", "") for s in prop.get("multi_select", [])])
    elif prop_type == "date":
        date = prop.get("date")
        return date.get("start", "") if date else ""
    elif prop_type == "number":
        return str(prop.get("number", ""))
    elif prop_type == "checkbox":
        return "Oui" if prop.get("checkbox") else "Non"
    elif prop_type == "status":
        status = prop.get("status")
        return status.get("name", "") if status else ""

    return ""


def tool_notion_search(query: str, fetch_content: bool = False) -> str:
    """Search Notion and return results - optimized for speed.

    Args:
        query: Search query
        fetch_content: If True, fetch page content (slower). Default False for Cliq.
    """
    if not NOTION_API_KEY:
        return "Erreur: Cle API Notion non configuree."

    results = notion_search(query)

    if not results:
        return f"Aucun resultat trouve dans Notion pour '{query}'."

    output = f"=== RESULTATS NOTION pour '{query}' ({len(results)} trouves) ===\n\n"

    for i, result in enumerate(results[:10], 1):
        obj_type = result.get("object", "")

        if obj_type == "page":
            title = extract_notion_title(result)
            page_url = result.get("url", "")
            output += f"{i}. 📄 **{title}**\n"

            # Only fetch content if explicitly requested (too slow for Cliq)
            if fetch_content:
                page_id = result.get("id", "")
                if page_id:
                    content = notion_get_page_content(page_id)
                    if content:
                        preview = content[:150] + "..." if len(content) > 150 else content
                        output += f"   {preview}\n"

            output += "\n"

        elif obj_type == "database":
            title_list = result.get("title", [])
            title = title_list[0].get("plain_text", "Sans titre") if title_list else "Sans titre"
            output += f"{i}. 📊 **Database: {title}**\n\n"

    return output


def tool_notion_search_wrapper(user_message: str) -> str:
    """Wrapper to extract search query from user message."""
    import re

    # Extract search terms after keywords - ordered by priority
    patterns = [
        # Consultation patterns with quoted text
        r"(?:consulte|consulter|ouvre|ouvrir|affiche|afficher|montre|montrer|voir)\s+['\"]([^'\"]+)['\"]",
        r"(?:consulte|consulter|ouvre|ouvrir|affiche|afficher|montre|montrer|voir)\s+(?:le\s+)?(?:rapport|document|page)?\s*[:\-]?\s*(.+)",
        # Search patterns
        r"(?:cherche|recherche|trouve|search|find)\s+(?:dans\s+)?(?:notion\s+)?[:\-]?\s*(.+)",
        r"notion\s+[:\-]?\s*(.+)",
        r"(?:projet|project)\s+(.+?)(?:\s+dans\s+notion)?",
        # Rapport/document patterns
        r"rapport\s+(?:de\s+)?(.+)",
        r"document\s+(?:de\s+)?(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, user_message.lower())
        if match:
            query = match.group(1).strip()
            # Clean up common stop words but keep important terms
            query = re.sub(r"\b(dans|notion|le|la|les|du|de|des|sur|pour)\b", " ", query)
            query = " ".join(query.split())  # Normalize whitespace
            if query and len(query) > 2:
                return tool_notion_search(query)

    # Fallback: extract key terms from message
    # Remove action words and stop words
    fallback_query = user_message.lower()
    fallback_query = re.sub(
        r"\b(consulte|consulter|ouvre|ouvrir|affiche|afficher|montre|montrer|voir|"
        r"cherche|recherche|trouve|dans|notion|le|la|les|du|de|des|sur|pour|"
        r"peux|tu|pouvez|vous|est|ce|que|qui|quoi|moi|s\'il|sil|te|plait|svp)\b",
        " ", fallback_query
    )
    fallback_query = " ".join(fallback_query.split())

    if fallback_query and len(fallback_query) > 2:
        return tool_notion_search(fallback_query)

    return "Veuillez preciser ce que vous cherchez dans Notion."


# ============================================
# UNIPILE HELPER FUNCTIONS (Forward declarations)
# ============================================
def _get_unipile_whatsapp_messages(limit: int = 10) -> str:
    """Fetch WhatsApp messages via Unipile API.
    Note: Full implementation in UNIPILE MESSAGE HANDLERS section below.
    """
    try:
        url = f"{UNIPILE_API_URL}/api/v1/messages"
        params = {"account_id": UNIPILE_WHATSAPP_ACCOUNT_ID, "limit": limit}
        headers = {"X-API-KEY": UNIPILE_API_KEY, "accept": "application/json"}

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            messages = data.get("items", [])

            if not messages:
                return "Aucun message WhatsApp recent trouve."

            output = f"=== MESSAGES WHATSAPP ({len(messages)} recents) ===\n\n"
            for i, msg in enumerate(messages[:limit], 1):
                sender = msg.get("sender_name", msg.get("from", "Inconnu"))
                text = (msg.get("text", msg.get("body", "")) or "")[:100]
                output += f"{i}. **{sender}**: {text}{'...' if len(msg.get('text', '') or '') > 100 else ''}\n"
            return output
        return f"Erreur API Unipile: {response.status_code}"
    except Exception as e:
        return f"Erreur WhatsApp: {str(e)}"


def _get_unipile_linkedin_messages(limit: int = 10) -> str:
    """Fetch LinkedIn messages via Unipile API.
    Note: Full implementation in UNIPILE MESSAGE HANDLERS section below.
    """
    try:
        url = f"{UNIPILE_API_URL}/api/v1/messages"
        params = {"account_id": UNIPILE_LINKEDIN_ACCOUNT_ID, "limit": limit}
        headers = {"X-API-KEY": UNIPILE_API_KEY, "accept": "application/json"}

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            messages = data.get("items", [])

            if not messages:
                return "Aucun message LinkedIn recent trouve."

            output = f"=== MESSAGES LINKEDIN ({len(messages)} recents) ===\n\n"
            for i, msg in enumerate(messages[:limit], 1):
                sender = msg.get("sender_name", msg.get("from", "Inconnu"))
                text = (msg.get("text", msg.get("body", "")) or "")[:100]
                output += f"{i}. **{sender}**: {text}{'...' if len(msg.get('text', '') or '') > 100 else ''}\n"
            return output
        return f"Erreur API Unipile: {response.status_code}"
    except Exception as e:
        return f"Erreur LinkedIn: {str(e)}"


def _get_unipile_telegram_messages(limit: int = 10) -> str:
    """Fetch Telegram messages via Unipile API."""
    try:
        url = f"{UNIPILE_API_URL}/api/v1/messages"
        # Telegram account ID
        telegram_account_id = "q2q8Td-bRLK2CVEQst3Mzw"
        params = {"account_id": telegram_account_id, "limit": limit}
        headers = {"X-API-KEY": UNIPILE_API_KEY, "accept": "application/json"}

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            messages = data.get("items", [])

            if not messages:
                return "Aucun message Telegram recent trouve."

            output = f"=== MESSAGES TELEGRAM ({len(messages)} recents) ===\n\n"
            for i, msg in enumerate(messages[:limit], 1):
                sender = msg.get("sender_name", msg.get("from", "Inconnu"))
                text = (msg.get("text", msg.get("body", "")) or "")[:100]
                output += f"{i}. **{sender}**: {text}{'...' if len(msg.get('text', '') or '') > 100 else ''}\n"
            return output
        return f"Erreur API Unipile: {response.status_code}"
    except Exception as e:
        return f"Erreur Telegram: {str(e)}"


def _get_unipile_chats(account_id: str, limit: int = 25) -> List[Dict]:
    """Get chats/contacts from Unipile."""
    try:
        url = f"{UNIPILE_API_URL}/api/v1/chats"
        params = {"account_id": account_id, "limit": limit}
        headers = {"X-API-KEY": UNIPILE_API_KEY, "accept": "application/json"}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
    except:
        return []


def _get_unipile_whatsapp_contacts(limit: int = 25) -> str:
    """Get WhatsApp contacts via Unipile."""
    chats = _get_unipile_chats(UNIPILE_WHATSAPP_ACCOUNT_ID, limit)

    if not chats:
        return "Aucun contact WhatsApp trouve."

    output = f"=== CONTACTS WHATSAPP ({len(chats)}) ===\n\n"

    # Separate groups and individual contacts
    groups = [c for c in chats if c.get("type") == 1]
    contacts = [c for c in chats if c.get("type") == 0 and c.get("name") != "WhatsApp"]

    if groups:
        output += "**Groupes:**\n"
        for g in groups:
            output += f"- {g.get('name', 'Sans nom')}\n"
        output += "\n"

    output += "**Contacts:**\n"
    for c in contacts[:20]:
        name = c.get("name") or c.get("attendee_public_identifier", "").replace("@s.whatsapp.net", "")
        if name and name != "status@broadcast":
            output += f"- {name}\n"

    return output


def _get_unipile_linkedin_contacts(limit: int = 25) -> str:
    """Get LinkedIn contacts via Unipile."""
    chats = _get_unipile_chats(UNIPILE_LINKEDIN_ACCOUNT_ID, limit)

    if not chats:
        return "Aucun contact LinkedIn trouve."

    output = f"=== CONTACTS LINKEDIN ({len(chats)}) ===\n\n"

    for c in chats[:25]:
        name = c.get("name", "Inconnu")
        if name:
            output += f"- {name}\n"

    return output


def _get_unipile_telegram_contacts(limit: int = 25) -> str:
    """Get Telegram contacts via Unipile."""
    telegram_account_id = "q2q8Td-bRLK2CVEQst3Mzw"
    chats = _get_unipile_chats(telegram_account_id, limit)

    if not chats:
        return "Aucun contact Telegram trouve."

    output = f"=== CONTACTS TELEGRAM ({len(chats)}) ===\n\n"

    for c in chats[:25]:
        name = c.get("name", "Inconnu")
        if name:
            output += f"- {name}\n"

    return output


# ============================================
# FACEBOOK MESSENGER VIA VIASOCKET MCP
# ============================================
def call_viasocket_mcp(instructions: str, thread_id: str = "new") -> str:
    """Call viaSocket MCP for Facebook Messenger actions."""
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "Facebook_Messenger",
                "arguments": {
                    "thread_id": thread_id,
                    "instructions": instructions
                }
            }
        }
        response = requests.post(VIASOCKET_MCP_URL, json=payload, headers=headers, timeout=60)

        # Parse SSE response
        text = response.text
        if text.startswith("event:"):
            lines = text.split("\n")
            for line in lines:
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    content = data.get("result", {}).get("content", [])
                    if content:
                        return content[0].get("text", "").strip('"')
        return "Pas de reponse du MCP Facebook Messenger."
    except Exception as e:
        return f"Erreur Facebook Messenger: {str(e)}"


def _get_facebook_messenger_info() -> str:
    """Get Facebook Messenger Page profile info."""
    result = call_viasocket_mcp("Get all Messenger Profile Fields Details for Page Agence Ran.AI")
    return f"=== FACEBOOK MESSENGER - PAGE AGENCE RAN.AI ===\n\n{result}"


def _send_facebook_message(recipient_psid: str, message: str) -> str:
    """Send a message from Page Agence Ran.AI to a user."""
    instructions = f"Send a message from Page Agence Ran.AI to user PSID {recipient_psid}. Message content: {message}"
    result = call_viasocket_mcp(instructions)
    return f"=== MESSAGE FACEBOOK ENVOYE ===\n\n{result}"


def _set_facebook_welcome_screen(greeting: str) -> str:
    """Set the Messenger welcome screen greeting."""
    instructions = f"Set the Messenger welcome screen greeting for Page Agence Ran.AI to: {greeting}"
    result = call_viasocket_mcp(instructions)
    return f"=== ECRAN D'ACCUEIL CONFIGURE ===\n\n{result}"


def _set_facebook_ice_breakers(questions: list) -> str:
    """Set Ice Breakers (FAQ) for the Messenger page."""
    questions_str = ", ".join(questions)
    instructions = f"Set Ice Breakers for Page Agence Ran.AI with these questions: {questions_str}"
    result = call_viasocket_mcp(instructions)
    return f"=== ICE BREAKERS CONFIGURES ===\n\n{result}"


def _get_facebook_actions_list() -> str:
    """List available Facebook Messenger actions."""
    return """=== FACEBOOK MESSENGER - ACTIONS DISPONIBLES ===

Page: Agence Ran.AI

Actions possibles:
1. Envoyer un message (Send Message from Page)
2. Envoyer un modele de recu (Receipt Template)
3. Configurer l'ecran d'accueil (Welcome Screen)
4. Configurer les Ice Breakers (FAQ)
5. Configurer le menu persistant (Persistent Menu)
6. Envoyer un modele generique (Generic Template)
7. Voir les parametres du profil Messenger

Note: La lecture des messages n'est pas disponible via l'API Meta Graph.
Utilisez l'app Facebook Messenger pour voir les conversations."""


# ============================================
# ZOHO WORKDRIVE FUNCTIONS
# ============================================
def workdrive_list_folders(parent_id: str = None) -> str:
    """List folders in Zoho WorkDrive."""
    try:
        # List all team folders first
        result = call_mcp_tool(
            ZOHO_WORKDRIVE_MCP_URL,
            ZOHO_WORKDRIVE_MCP_KEY,
            "ZohoWorkdrive_listAllTeamFoldersOfaTeam",
            {"path_variables": {"team_id": ZOHO_WORKDRIVE_TEAM_ID}}
        )
        text = extract_mcp_text(result)

        # Parse and format
        try:
            data = json.loads(text) if text.startswith("{") or text.startswith("[") else {"raw": text}
            items = data.get("data", []) if isinstance(data, dict) else data

            output = "=== DOSSIERS WORKDRIVE ===\n\n"
            for item in items[:20]:
                if isinstance(item, dict):
                    attrs = item.get("attributes", {})
                    name = attrs.get("name", item.get("name", "?"))
                    item_type = attrs.get("type", "teamfolder")
                    item_id = item.get("id", "")
                    icon = "📁" if "folder" in item_type.lower() else "📄"
                    output += f"{icon} {name} (ID: {item_id})\n"
            return output if len(output) > 30 else f"=== WORKDRIVE ===\n\n{text[:1000]}"
        except:
            return f"=== WORKDRIVE ===\n\n{text[:1500]}"
    except Exception as e:
        return f"Erreur WorkDrive: {str(e)}"


def workdrive_create_folder(folder_name: str, parent_id: str = None) -> str:
    """Create a new Team Folder in Zoho WorkDrive."""
    try:
        result = call_mcp_tool(
            ZOHO_WORKDRIVE_MCP_URL,
            ZOHO_WORKDRIVE_MCP_KEY,
            "ZohoWorkdrive_createTeamFolder",
            {
                "path_variables": {"team_id": ZOHO_WORKDRIVE_TEAM_ID},
                "body": {"name": folder_name}
            }
        )
        text = extract_mcp_text(result)
        return f"=== DOSSIER CREE ===\n\nNom: {folder_name}\nResultat: {text[:500]}"
    except Exception as e:
        return f"Erreur creation dossier: {str(e)}"


# ============================================
# NOTION FUNCTIONS
# ============================================
def notion_api_call(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Call Notion API directly."""
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    url = f"{NOTION_API_URL}/{endpoint}"

    if method == "GET":
        response = requests.get(url, headers=headers, timeout=30)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data, timeout=30)
    elif method == "PATCH":
        response = requests.patch(url, headers=headers, json=data, timeout=30)
    else:
        return {"error": f"Method {method} not supported"}

    return response.json()


def notion_search(query: str) -> str:
    """Search in Notion workspace."""
    try:
        result = notion_api_call("search", "POST", {
            "query": query,
            "page_size": 10
        })

        results = result.get("results", [])
        output = f"=== RECHERCHE NOTION: '{query}' ===\n\n"

        if not results:
            return output + "Aucun resultat trouve."

        for item in results:
            obj_type = item.get("object", "")
            item_id = item.get("id", "")

            # Get title
            title = "Sans titre"
            if obj_type == "page":
                props = item.get("properties", {})
                title_prop = props.get("title", props.get("Name", {}))
                if title_prop:
                    title_arr = title_prop.get("title", [])
                    if title_arr:
                        title = title_arr[0].get("plain_text", "Sans titre")
            elif obj_type == "database":
                title_arr = item.get("title", [])
                if title_arr:
                    title = title_arr[0].get("plain_text", "Sans titre")

            icon = "📄" if obj_type == "page" else "📊"
            output += f"{icon} {title}\n   ID: {item_id}\n\n"

        return output
    except Exception as e:
        return f"Erreur recherche Notion: {str(e)}"


def notion_create_page(parent_id: str, title: str, content: str = "") -> str:
    """Create a new page in Notion."""
    try:
        # Determine if parent is a page or database
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }
        }

        # Add content if provided
        if content:
            page_data["children"] = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
            ]

        result = notion_api_call("pages", "POST", page_data)

        if "id" in result:
            page_id = result["id"]
            url = result.get("url", "")
            return f"=== PAGE NOTION CREEE ===\n\nTitre: {title}\nID: {page_id}\nURL: {url}"
        else:
            error = result.get("message", str(result))
            return f"Erreur creation page: {error}"
    except Exception as e:
        return f"Erreur Notion: {str(e)}"


def notion_create_database(parent_id: str, title: str, properties: dict = None) -> str:
    """Create a new database in Notion."""
    try:
        db_data = {
            "parent": {"page_id": parent_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "properties": properties or {
                "Name": {"title": {}},
                "Status": {
                    "select": {
                        "options": [
                            {"name": "A faire", "color": "red"},
                            {"name": "En cours", "color": "yellow"},
                            {"name": "Termine", "color": "green"}
                        ]
                    }
                },
                "Date": {"date": {}}
            }
        }

        result = notion_api_call("databases", "POST", db_data)

        if "id" in result:
            db_id = result["id"]
            url = result.get("url", "")
            return f"=== BASE DE DONNEES NOTION CREEE ===\n\nTitre: {title}\nID: {db_id}\nURL: {url}"
        else:
            error = result.get("message", str(result))
            return f"Erreur creation database: {error}"
    except Exception as e:
        return f"Erreur Notion: {str(e)}"


def notion_add_link_to_page(page_id: str, link_url: str, link_title: str) -> str:
    """Add a link block to an existing Notion page."""
    try:
        block_data = {
            "children": [
                {
                    "object": "block",
                    "type": "bookmark",
                    "bookmark": {
                        "url": link_url
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": f"📎 {link_title}: "}},
                            {"type": "text", "text": {"content": link_url, "link": {"url": link_url}}}
                        ]
                    }
                }
            ]
        }

        result = notion_api_call(f"blocks/{page_id}/children", "PATCH", block_data)

        if "results" in result:
            return f"=== LIEN AJOUTE ===\n\nPage: {page_id}\nLien: {link_url}"
        else:
            error = result.get("message", str(result))
            return f"Erreur ajout lien: {error}"
    except Exception as e:
        return f"Erreur Notion: {str(e)}"


# ============================================
# TOOL DETECTION & EXECUTION
# ============================================
TOOLS_CONFIG = {
    "email": {
        "triggers": ["courriel", "email", "mail", "courrier", "inbox", "boite", "message"],
        "function": tool_read_emails
    },
    "spam": {
        "triggers": ["spam", "pourriel", "indesirable"],
        "function": tool_read_spam
    },
    "calendar": {
        "triggers": ["agenda", "calendrier", "rdv", "reunion", "evenement", "aujourd", "demain", "semaine", "janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche", "planning"],
        "function": tool_read_calendar
    },
    "deals": {
        "triggers": ["deal", "opportunite", "pipeline", "vente"],
        "function": tool_read_deals
    },
    "contacts": {
        "triggers": ["contact", "client", "prospect", "crm"],
        "function": tool_read_contacts
    },
    "invoices": {
        "triggers": ["facture", "invoice"],
        "function": tool_read_invoices
    },
    "expenses": {
        "triggers": ["depense", "dépense", "depenses", "dépenses", "expense", "expenses", "cout", "coût", "frais"],
        "function": tool_read_expenses
    },
    "financial": {
        "triggers": ["finance", "bilan", "comptable", "books", "argent"],
        "function": tool_financial_summary
    },
    "gr_meetings": {
        "triggers": ["gr reunion", "gr meeting", "gr rencontre"],
        "function": tool_gr_meetings
    },
    "gr_toolboxes": {
        "triggers": ["boite outil", "boites outil", "toolbox", "gr outil", "gr boite", "outils gr"],
        "function": tool_gr_toolboxes
    },
    "gr_groups": {
        "triggers": ["gr groupe", "gr group", "groupe gr"],
        "function": tool_gr_groups
    },
    "gr_youtube": {
        "triggers": ["gr video", "gr youtube", "youtube gr"],
        "function": tool_gr_youtube
    },
    "gr_all": {
        "triggers": ["gr international", "gr tout", "gr info"],
        "function": lambda: f"{tool_gr_meetings()}\n\n{tool_gr_toolboxes()}"
    },
    "projects": {
        "triggers": ["projet", "projets", "project", "projects", "zoho projet"],
        "function": tool_read_projects
    },
    "tasks": {
        "triggers": ["tache", "tâche", "taches", "tâches", "task", "tasks", "todo", "a faire", "à faire"],
        "function": tool_read_tasks
    },
    "notion": {
        "triggers": ["notion", "cherche dans notion", "recherche notion"],
        "function": None  # Special handling in detect_and_execute_tools
    },
    "whatsapp": {
        "triggers": ["whatsapp", "message whatsapp", "messages whatsapp", "wa message"],
        "function": None  # Special handling - defined later
    },
    "linkedin_messages": {
        "triggers": ["linkedin message", "messages linkedin", "linkedin inbox", "message linkedin"],
        "function": None  # Special handling - defined later
    },
    "telegram": {
        "triggers": ["telegram", "message telegram", "messages telegram"],
        "function": None  # Special handling - defined later
    }
}


def detect_and_execute_tools(user_message: str) -> str:
    """Detect which tools to use and execute them."""
    user_lower = user_message.lower()
    results = []
    executed = set()

    # ===== SEND EMAIL (needs full message to parse) =====
    send_email_triggers = ["envoie email", "envoyer email", "envoie courriel", "envoyer courriel",
                           "envoie un email", "envoyer un email", "email a ", "courriel a "]

    for trigger in send_email_triggers:
        if trigger in user_lower and "send_email" not in executed:
            try:
                result = tool_send_email_parse(user_message)
                results.append(result)
                executed.add("send_email")
            except Exception as e:
                results.append(f"Erreur envoi email: {str(e)}")
            break

    # ===== SEARCH EMAIL (needs full message to extract keywords) =====
    search_email_triggers = ["cherche email", "chercher email", "recherche email", "rechercher email",
                             "trouve email", "trouver email", "cherche courriel", "cherche dans mes emails"]

    for trigger in search_email_triggers:
        if trigger in user_lower and "search_email" not in executed:
            try:
                # Extract keywords from message
                import re
                keywords = re.sub(r"(?:cherche|recherche|trouve|trouver|dans|mes|emails?|courriels?|les?)\s*", "", user_lower)
                keywords = keywords.strip()
                if keywords:
                    result = tool_search_emails(keywords)
                    results.append(result)
                    executed.add("search_email")
            except Exception as e:
                results.append(f"Erreur recherche email: {str(e)}")
            break

    # ===== CREATE TASK (needs full message to parse) =====
    create_task_triggers = ["cree tache", "créer tache", "creer tache", "nouvelle tache",
                            "ajoute tache", "ajouter tache", "cree une tache", "nouvelle task"]

    for trigger in create_task_triggers:
        if trigger in user_lower and "create_task" not in executed:
            try:
                result = tool_create_task_parse(user_message)
                results.append(result)
                executed.add("create_task")
            except Exception as e:
                results.append(f"Erreur creation tache: {str(e)}")
            break

    # ===== CREATE EXPENSE (needs full message to parse) =====
    create_expense_triggers = ["enregistre depense", "enregistrer depense", "ajoute depense",
                               "ajouter depense", "nouvelle depense", "ajoute une depense"]

    for trigger in create_expense_triggers:
        if trigger in user_lower and "create_expense" not in executed:
            try:
                result = tool_create_expense_parse(user_message)
                results.append(result)
                executed.add("create_expense")
            except Exception as e:
                results.append(f"Erreur creation depense: {str(e)}")
            break

    # ===== CREATE EVENT (needs full message to parse) =====
    create_triggers = ["ajoute rdv", "ajouter rdv", "creer evenement", "créer événement",
                       "creez evenement", "créez l'evenement", "creez l'evenement",
                       "nouveau rdv", "ajoute evenement", "ajouter evenement",
                       "rdv:", "evenement:", "dans mon calendrier", "dans le calendrier",
                       "ajoute reunion", "ajouter reunion", "creer reunion"]

    for trigger in create_triggers:
        if trigger in user_lower and "create_event" not in executed:
            try:
                result = tool_smart_create_event(user_message)
                results.append(result)
                executed.add("create_event")
            except Exception as e:
                results.append(f"Erreur creation evenement: {str(e)}")
            break

    # ===== UPDATE EVENT (needs full message to parse) =====
    update_triggers = ["modifie rdv", "modifier rdv", "modifie evenement", "modifier evenement",
                       "update rdv", "update evenement", "maj rdv", "mise a jour rdv"]

    for trigger in update_triggers:
        if trigger in user_lower and "update_event" not in executed:
            try:
                result = tool_update_event_parse(user_message)
                results.append(result)
                executed.add("update_event")
            except Exception as e:
                results.append(f"Erreur modification evenement: {str(e)}")
            break

    # ===== NOTION SEARCH (needs full message to extract query) =====
    # Extended triggers to catch consultation requests
    notion_triggers = [
        "notion", "cherche dans notion", "recherche notion", "trouve dans notion",
        "consulte", "consulter", "ouvre", "ouvrir", "affiche", "afficher",
        "montre", "montrer", "voir", "rapport", "document", "page notion",
        "elia", "élia", "projet elia", "projet élia"
    ]

    for trigger in notion_triggers:
        if trigger in user_lower and "notion" not in executed:
            try:
                result = tool_notion_search_wrapper(user_message)
                results.append(result)
                executed.add("notion")
            except Exception as e:
                results.append(f"Erreur Notion: {str(e)}")
            break

    # ===== WHATSAPP (via Unipile) =====
    # Detect if user wants WhatsApp contacts or messages
    if "whatsapp" in user_lower and "whatsapp" not in executed:
        try:
            if "contact" in user_lower:
                result = _get_unipile_whatsapp_contacts()
            else:
                result = _get_unipile_whatsapp_messages()
            results.append(result)
            executed.add("whatsapp")
        except Exception as e:
            results.append(f"Erreur WhatsApp: {str(e)}")

    # ===== LINKEDIN (via Unipile) =====
    # Detect if user wants LinkedIn contacts or messages
    if "linkedin" in user_lower and "linkedin" not in executed:
        try:
            if "contact" in user_lower:
                result = _get_unipile_linkedin_contacts()
            else:
                result = _get_unipile_linkedin_messages()
            results.append(result)
            executed.add("linkedin")
        except Exception as e:
            results.append(f"Erreur LinkedIn: {str(e)}")

    # ===== TELEGRAM (via Unipile) =====
    # Detect if user wants Telegram contacts or messages
    if "telegram" in user_lower and "telegram" not in executed:
        try:
            if "contact" in user_lower:
                result = _get_unipile_telegram_contacts()
            else:
                result = _get_unipile_telegram_messages()
            results.append(result)
            executed.add("telegram")
        except Exception as e:
            results.append(f"Erreur Telegram: {str(e)}")

    # ===== FACEBOOK MESSENGER (via viaSocket MCP) =====
    # Detect if user wants Facebook Messenger info or actions
    if ("facebook" in user_lower or "messenger" in user_lower) and "facebook" not in executed:
        try:
            if "config" in user_lower or "parametre" in user_lower or "profil" in user_lower:
                result = _get_facebook_messenger_info()
            elif "action" in user_lower or "faire" in user_lower or "possible" in user_lower:
                result = _get_facebook_actions_list()
            else:
                # Default: show available actions
                result = _get_facebook_actions_list()
            results.append(result)
            executed.add("facebook")
        except Exception as e:
            results.append(f"Erreur Facebook Messenger: {str(e)}")

    # ===== ZOHO WORKDRIVE =====
    if ("workdrive" in user_lower or "drive" in user_lower) and "workdrive" not in executed:
        try:
            if "creer" in user_lower or "créer" in user_lower or "nouveau" in user_lower:
                # Extract folder name - look for patterns like "dossier X" or "appelé X"
                import re
                match = re.search(r'(?:dossier|appelé|appele|nomme|nommé)\s+["\']?([^"\']+)["\']?', user_lower)
                if match:
                    folder_name = match.group(1).strip()
                else:
                    folder_name = "Nouveau Dossier"
                result = workdrive_create_folder(folder_name)
            else:
                result = workdrive_list_folders()
            results.append(result)
            executed.add("workdrive")
        except Exception as e:
            results.append(f"Erreur WorkDrive: {str(e)}")

    # ===== NOTION (enhanced) =====
    if "notion" in user_lower and "notion" not in executed:
        try:
            import re
            if "creer" in user_lower or "créer" in user_lower or "nouveau" in user_lower:
                # Check if creating page or database
                if "base" in user_lower or "database" in user_lower or "db" in user_lower:
                    # Need parent ID - search for it first
                    result = notion_search("") + "\n\nPour creer une base de donnees, utilisez: 'creer database [nom] dans [parent_id]'"
                elif "page" in user_lower or "dossier" in user_lower:
                    # Extract title
                    match = re.search(r'(?:page|dossier)\s+(?:sur\s+)?["\']?([^"\']+)["\']?', user_lower)
                    title = match.group(1).strip() if match else "Nouvelle Page"
                    # For now, just show search results to find parent
                    result = notion_search(title) + f"\n\nPour creer la page '{title}', specifiez l'ID du parent."
                else:
                    result = notion_search("")
            elif "cherche" in user_lower or "recherche" in user_lower or "trouve" in user_lower:
                # Extract search query
                match = re.search(r'(?:cherche|recherche|trouve)\s+(?:dans\s+notion\s+)?["\']?([^"\']+)["\']?', user_lower)
                query = match.group(1).strip() if match else ""
                result = notion_search(query)
            else:
                # Default: search with any relevant terms
                result = notion_search("")
            results.append(result)
            executed.add("notion")
        except Exception as e:
            results.append(f"Erreur Notion: {str(e)}")

    # ===== STANDARD TOOL DETECTION =====
    for tool_name, config in TOOLS_CONFIG.items():
        for trigger in config["triggers"]:
            if trigger in user_lower and tool_name not in executed:
                # Skip tools with special handling
                if tool_name in ["notion", "whatsapp", "linkedin_messages", "telegram", "linkedin", "facebook", "workdrive"]:
                    continue
                try:
                    if config["function"]:
                        result = config["function"]()
                        results.append(result)
                        executed.add(tool_name)
                except Exception as e:
                    results.append(f"Erreur {tool_name}: {str(e)}")
                break

    return "\n\n---\n\n".join(results) if results else ""


# ============================================
# MAIN RESPONSE GENERATOR
# ============================================
def extract_context_from_history(user_message: str, history: List) -> str:
    """Extract relevant context from conversation history.

    If the user refers to something mentioned before (like a document name),
    try to find the full name from the history.
    """
    if not history:
        return ""

    import re
    user_lower = user_message.lower()

    # Check if user is referring to something from history
    reference_patterns = [
        r"(?:consulte|consulter|ouvre|ouvrir|voir|affiche)\s+(?:le\s+)?(?:rapport|document)",
        r"rapport\s+de\s+validation",
        r"rapport.*(?:elia|élia)",
    ]

    is_reference = any(re.search(p, user_lower) for p in reference_patterns)

    if is_reference:
        # Look for document/rapport names in history (from Atlas responses)
        for h in reversed(history[-10:]):
            text = h.get("text", "")
            sender = h.get("sender", "")

            if sender == "Atlas" and text:
                # Look for document names mentioned by Atlas
                doc_patterns = [
                    r"Rapport\s+de\s+Validation\s+Technique\s+Final[^\"'\n]*",
                    r"Rapport\s+[ÉE]LIA[^\"'\n]*",
                    r"\*\*([^*]+)\*\*",  # Bold text often contains document names
                ]

                for pattern in doc_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        # Return the first relevant match as additional context
                        for match in matches:
                            if "rapport" in match.lower() or "validation" in match.lower() or "elia" in match.lower():
                                return match.strip()

    return ""


def generate_atlas_response(user_message: str, user_name: str = "Utilisateur", history: List = None) -> str:
    """Generate Atlas response with full tool access and conversation history."""
    if not ANTHROPIC_API_KEY:
        return "Erreur: Cle API Anthropic non configuree."

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Use Eastern timezone
    current_date = datetime.now(TIMEZONE).strftime("%d janvier %Y, %H:%M")
    system = ATLAS_SYSTEM_PROMPT.format(current_date=current_date)

    # Check if user is referring to something from history
    context_hint = extract_context_from_history(user_message, history)
    enriched_message = user_message
    if context_hint:
        # Add context hint to help tool detection
        enriched_message = f"{user_message} ({context_hint})"

    # Execute relevant tools and get data
    tool_data = detect_and_execute_tools(enriched_message)
    
    if tool_data:
        system += f"\n\n=== DONNEES RECUPEREES ===\n{tool_data}"

    # Build messages with history
    messages = []
    
    # Add conversation history if available
    if history and len(history) > 0:
        history_text = "Historique de conversation recent:\n"
        for h in history[-10:]:  # Keep last 10 messages
            sender = h.get("sender", "?")
            text = h.get("text", "")[:200]
            if sender == "Atlas":
                history_text += f"Atlas: {text}\n"
            else:
                history_text += f"{sender}: {text}\n"
        system += f"\n\n=== CONTEXTE CONVERSATION ===\n{history_text}"
    
    messages.append({"role": "user", "content": f"{user_name} dit: {user_message}"})

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system,
        messages=messages
    )

    return message.content[0].text


def post_to_cliq_channel(message: str, channel_name: str = ATLAS_CHANNEL_NAME) -> Dict:
    """Post message to Cliq channel."""
    return call_mcp_tool(
        ZOHO_CLIQ_MCP_URL,
        ZOHO_CLIQ_MCP_KEY,
        "Post message in a channel",
        {
            "body": {"text": message},
            "path_variables": {"CHANNEL_UNIQUE_NAME": channel_name}
        }
    )


def handle_cliq_message(payload: Dict) -> Dict:
    """Handle incoming Cliq message with conversation history."""
    try:
        # Debug: log the payload structure
        debug_info = {
            "payload_keys": list(payload.keys()) if isinstance(payload, dict) else "not_dict",
            "message_type": type(payload.get("message")).__name__ if isinstance(payload, dict) else "unknown"
        }

        # Extract message text from various possible locations
        message_obj = payload.get("message", {})
        message_text = message_obj.get("text", "") if isinstance(message_obj, dict) else str(message_obj)

        # Also check for content field (used when files are attached)
        if not message_text:
            message_text = payload.get("text", "")
        if not message_text:
            message_text = message_obj.get("content", "") if isinstance(message_obj, dict) else ""

        # Check for file attachments
        attachments = []
        if isinstance(message_obj, dict):
            attachments = message_obj.get("files", []) or message_obj.get("attachments", [])
        if not attachments:
            attachments = payload.get("files", []) or payload.get("attachments", [])

        user_name = payload.get("sender", {}).get("name", "Utilisateur")

        # Don't ignore if we have attachments even without text
        if (not message_text and not attachments) or payload.get("sender", {}).get("type") == "bot":
            return {"status": "ignored", "debug": debug_info, "reason": "no_text_or_attachments"}

        # Get history directly from payload (sent by Deluge script)
        history = payload.get("history", [])

        # If no history in payload, try to fetch from Cliq API
        if not history:
            chat_id = payload.get("chat", {}).get("id", "")
            if chat_id:
                history = get_conversation_history(chat_id, limit=10)

        # Add attachment context to message if files are present
        enhanced_message = message_text
        if attachments:
            file_info = []
            for att in attachments:
                if isinstance(att, dict):
                    fname = att.get("name", att.get("filename", "fichier"))
                    fsize = att.get("size", "")
                    furl = att.get("url", att.get("download_url", ""))
                    file_info.append(f"{fname} ({fsize})" if fsize else fname)
                else:
                    file_info.append(str(att))
            if file_info:
                enhanced_message = f"{message_text}\n[Fichiers joints: {', '.join(file_info)}]"

        response = generate_atlas_response(enhanced_message, user_name, history)

        return {
            "status": "success",
            "user_message": message_text,
            "attachments": len(attachments),
            "atlas_response": response
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


# ============================================
# UNIPILE MESSAGE HANDLERS
# ============================================
def format_unipile_message_for_cliq(unipile_data: Dict) -> str:
    """Format an Unipile webhook message for posting to Zoho Cliq.

    Unipile webhook payload structure (based on their API):
    - account_type: WHATSAPP, LINKEDIN, TELEGRAM, MESSENGER
    - sender: {name, identifier, provider_id, ...}
    - message: {text, ...}
    - timestamp: ISO timestamp
    - is_sender: bool (true if we sent it)
    """
    try:
        # Get account type
        account_type = unipile_data.get("account_type", "UNKNOWN")

        # Get sender info
        sender_data = unipile_data.get("sender", {})
        if isinstance(sender_data, dict):
            sender_name = sender_data.get("name", sender_data.get("identifier", "Inconnu"))
        else:
            sender_name = str(sender_data) if sender_data else "Inconnu"

        # Get message content
        message_data = unipile_data.get("message", {})
        if isinstance(message_data, dict):
            message_text = message_data.get("text", "")
        else:
            message_text = str(message_data) if message_data else ""

        # Get timestamp
        timestamp = unipile_data.get("timestamp", "")

        # Check if we sent this message (skip if true)
        is_sender = unipile_data.get("is_sender", False)
        if is_sender:
            return None  # Skip messages we sent ourselves

        # Determine platform emoji
        platform_map = {
            "WHATSAPP": ("📱", "WhatsApp"),
            "LINKEDIN": ("💼", "LinkedIn"),
            "TELEGRAM": ("✈️", "Telegram"),
            "MESSENGER": ("💬", "Messenger"),
        }
        platform_emoji, platform_name = platform_map.get(account_type, ("📨", account_type))

        # Format for Cliq
        cliq_message = f"{platform_emoji} **Nouveau message {platform_name}**\n\n"
        cliq_message += f"**De:** {sender_name}\n"
        if message_text:
            # Truncate long messages
            display_text = message_text[:500] + "..." if len(message_text) > 500 else message_text
            cliq_message += f"**Message:** {display_text}\n"
        if timestamp:
            # Format timestamp if it's ISO format
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                timestamp_display = dt.strftime("%d/%m %H:%M")
            except:
                timestamp_display = timestamp
            cliq_message += f"**Recu:** {timestamp_display}\n"

        return cliq_message

    except Exception as e:
        return f"📨 Nouveau message recu (erreur formatage: {str(e)})"


def handle_unipile_webhook(payload: Dict) -> Dict:
    """Handle incoming Unipile webhook (WhatsApp/LinkedIn/Messenger messages).

    Unipile sends the message data directly in the payload, not under 'data' key.
    The webhook was configured with 'message_received' event.
    """
    try:
        # Log incoming payload for debugging
        account_type = payload.get("account_type", "UNKNOWN")
        webhook_name = payload.get("webhook_name", "")

        # Check if this is a message we sent ourselves
        is_sender = payload.get("is_sender", False)
        if is_sender:
            return {
                "status": "ignored",
                "reason": "Message sent by us (is_sender=true)"
            }

        # Format message for Cliq
        cliq_message = format_unipile_message_for_cliq(payload)

        if cliq_message is None:
            return {
                "status": "ignored",
                "reason": "Message filtered out (sent by us)"
            }

        # Post to Atlas channel in Zoho Cliq
        post_result = post_to_cliq_channel(cliq_message, ATLAS_CHANNEL_NAME)

        return {
            "status": "success",
            "account_type": account_type,
            "forwarded_to": f"Zoho Cliq #{ATLAS_CHANNEL_NAME}",
            "cliq_result": str(post_result)[:200]
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "payload_keys": list(payload.keys()) if payload else []
        }


def get_unipile_messages(account_id: str, limit: int = 10) -> List[Dict]:
    """Fetch recent messages from Unipile for a specific account."""
    try:
        url = f"{UNIPILE_API_URL}/api/v1/messages"
        params = {
            "account_id": account_id,
            "limit": limit
        }
        headers = {
            "X-API-KEY": UNIPILE_API_KEY,
            "accept": "application/json"
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        return []

    except Exception as e:
        return []


def tool_read_whatsapp_messages(limit: int = 10) -> str:
    """Read recent WhatsApp messages via Unipile."""
    messages = get_unipile_messages(UNIPILE_WHATSAPP_ACCOUNT_ID, limit)

    if not messages:
        return "Aucun message WhatsApp recent trouve."

    output = f"=== MESSAGES WHATSAPP ({len(messages)} recents) ===\n\n"

    for i, msg in enumerate(messages[:limit], 1):
        sender = msg.get("sender_name", msg.get("from", "Inconnu"))
        text = msg.get("text", msg.get("body", ""))[:100]
        timestamp = msg.get("timestamp", msg.get("date", ""))

        output += f"{i}. **{sender}**\n"
        output += f"   {text}{'...' if len(msg.get('text', '')) > 100 else ''}\n"
        if timestamp:
            output += f"   _{timestamp}_\n"
        output += "\n"

    return output


def tool_read_linkedin_messages(limit: int = 10) -> str:
    """Read recent LinkedIn messages via Unipile."""
    messages = get_unipile_messages(UNIPILE_LINKEDIN_ACCOUNT_ID, limit)

    if not messages:
        return "Aucun message LinkedIn recent trouve."

    output = f"=== MESSAGES LINKEDIN ({len(messages)} recents) ===\n\n"

    for i, msg in enumerate(messages[:limit], 1):
        sender = msg.get("sender_name", msg.get("from", "Inconnu"))
        text = msg.get("text", msg.get("body", ""))[:100]
        timestamp = msg.get("timestamp", msg.get("date", ""))

        output += f"{i}. **{sender}**\n"
        output += f"   {text}{'...' if len(msg.get('text', '')) > 100 else ''}\n"
        if timestamp:
            output += f"   _{timestamp}_\n"
        output += "\n"

    return output


# ============================================
# UNIPILE SEND MESSAGE FUNCTIONS
# ============================================
UNIPILE_TELEGRAM_ACCOUNT_ID = "q2q8Td-bRLK2CVEQst3Mzw"


def unipile_get_chats(account_id: str, limit: int = 20) -> List[Dict]:
    """Get list of chats for an account."""
    try:
        url = f"{UNIPILE_API_URL}/api/v1/chats"
        params = {"account_id": account_id, "limit": limit}
        headers = {"X-API-KEY": UNIPILE_API_KEY, "accept": "application/json"}
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return response.json().get("items", [])
        return []
    except:
        return []


def unipile_send_message(chat_id: str, text: str) -> Dict:
    """Send a message to a specific chat."""
    try:
        url = f"{UNIPILE_API_URL}/api/v1/chats/{chat_id}/messages"
        headers = {
            "X-API-KEY": UNIPILE_API_KEY,
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        response = requests.post(url, headers=headers, json={"text": text}, timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def unipile_find_chat_by_name(account_id: str, search_name: str) -> Dict:
    """Find a chat by contact name or identifier."""
    chats = unipile_get_chats(account_id, limit=50)
    search_lower = search_name.lower()

    for chat in chats:
        chat_name = (chat.get("name") or "").lower()
        attendee_id = (chat.get("attendee_public_identifier") or "").lower()

        if search_lower in chat_name or search_lower in attendee_id:
            return chat

    return None


def tool_send_whatsapp_message(recipient: str, message: str) -> str:
    """Send a WhatsApp message via Unipile."""
    chat = unipile_find_chat_by_name(UNIPILE_WHATSAPP_ACCOUNT_ID, recipient)

    if not chat:
        return f"Contact '{recipient}' non trouve dans WhatsApp. Essayez avec le numero de telephone."

    result = unipile_send_message(chat["id"], message)

    if "message_id" in result:
        return f"Message WhatsApp envoye a {recipient}!"
    return f"Erreur envoi WhatsApp: {result}"


def tool_send_linkedin_message(recipient: str, message: str) -> str:
    """Send a LinkedIn message via Unipile."""
    chat = unipile_find_chat_by_name(UNIPILE_LINKEDIN_ACCOUNT_ID, recipient)

    if not chat:
        return f"Contact '{recipient}' non trouve dans LinkedIn."

    result = unipile_send_message(chat["id"], message)

    if "message_id" in result:
        return f"Message LinkedIn envoye a {recipient}!"
    return f"Erreur envoi LinkedIn: {result}"


def tool_send_telegram_message(recipient: str, message: str) -> str:
    """Send a Telegram message via Unipile."""
    chat = unipile_find_chat_by_name(UNIPILE_TELEGRAM_ACCOUNT_ID, recipient)

    if not chat:
        return f"Contact '{recipient}' non trouve dans Telegram."

    result = unipile_send_message(chat["id"], message)

    if "message_id" in result:
        return f"Message Telegram envoye a {recipient}!"
    return f"Erreur envoi Telegram: {result}"


def tool_list_whatsapp_contacts() -> str:
    """List available WhatsApp contacts/chats."""
    chats = unipile_get_chats(UNIPILE_WHATSAPP_ACCOUNT_ID, limit=20)

    if not chats:
        return "Aucun contact WhatsApp trouve."

    output = "=== CONTACTS WHATSAPP ===\n\n"
    for i, chat in enumerate(chats[:20], 1):
        name = chat.get("name") or chat.get("attendee_public_identifier", "Inconnu")
        output += f"{i}. {name}\n"
    return output


def tool_list_linkedin_contacts() -> str:
    """List available LinkedIn contacts/chats."""
    chats = unipile_get_chats(UNIPILE_LINKEDIN_ACCOUNT_ID, limit=20)

    if not chats:
        return "Aucun contact LinkedIn trouve."

    output = "=== CONTACTS LINKEDIN ===\n\n"
    for i, chat in enumerate(chats[:20], 1):
        name = chat.get("name") or "Inconnu"
        output += f"{i}. {name}\n"
    return output


def tool_list_telegram_contacts() -> str:
    """List available Telegram contacts/chats."""
    chats = unipile_get_chats(UNIPILE_TELEGRAM_ACCOUNT_ID, limit=20)

    if not chats:
        return "Aucun contact Telegram trouve."

    output = "=== CONTACTS TELEGRAM ===\n\n"
    for i, chat in enumerate(chats[:20], 1):
        name = chat.get("name") or chat.get("attendee_public_identifier", "Inconnu")
        output += f"{i}. {name}\n"
    return output


# ============================================
# MODAL WEBHOOK
# ============================================
try:
    import modal

    app = modal.App("atlas-cliq-webhook")

    image = modal.Image.debian_slim().pip_install(
        "anthropic",
        "requests",
        "fastapi"
    )

    @app.function(
        image=image,
        secrets=[modal.Secret.from_name("atlas-secrets")]
    )
    @modal.fastapi_endpoint(method="POST")
    def atlas_webhook(payload: Dict) -> Dict:
        """Webhook endpoint for Cliq messages."""
        return handle_cliq_message(payload)

    @app.function(
        image=image,
        secrets=[modal.Secret.from_name("atlas-secrets")]
    )
    @modal.fastapi_endpoint(method="GET")
    def health_check() -> Dict:
        """Health check endpoint with Unipile status."""
        # Check Unipile connection
        unipile_status = {"status": "unknown"}
        try:
            url = f"{UNIPILE_API_URL}/api/v1/accounts"
            headers = {"X-API-KEY": UNIPILE_API_KEY, "accept": "application/json"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                accounts = data.get("items", [])
                unipile_status = {
                    "status": "connected",
                    "accounts": [{"type": acc.get("type"), "name": acc.get("name")} for acc in accounts]
                }
        except:
            unipile_status = {"status": "error"}

        return {
            "status": "ok",
            "service": "Atlas Cliq Webhook v8.2 + Unipile + Facebook + WorkDrive + Notion",
            "timestamp": datetime.now(TIMEZONE).isoformat(),
            "tools_available": list(TOOLS_CONFIG.keys()) + ["workdrive", "notion_enhanced"],
            "integrations": ["Zoho Cliq", "WhatsApp", "LinkedIn", "Telegram", "Facebook Messenger", "WorkDrive", "Notion"],
            "unipile": unipile_status
        }

    @app.function(
        image=image,
        secrets=[modal.Secret.from_name("atlas-secrets")]
    )
    @modal.fastapi_endpoint(method="POST")
    def unipile_webhook(payload: Dict) -> Dict:
        """
        Webhook endpoint for Unipile (WhatsApp/LinkedIn/Messenger messages).
        Configure this URL in Unipile webhook settings.
        """
        return handle_unipile_webhook(payload)

except ImportError:
    pass


# ============================================
# STANDALONE MODE
# ============================================
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_message = " ".join(sys.argv[1:])
        print(f"Message: {test_message}")
        print("-" * 40)
        response = generate_atlas_response(test_message, "Test")
        print(f"Atlas: {response}")
    else:
        print("Atlas Cliq Webhook v7.0")
        print("Available tools:", list(TOOLS_CONFIG.keys()))
