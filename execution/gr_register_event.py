#!/usr/bin/env python3
"""
GR International - Inscription aux événements
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from playwright.sync_api import sync_playwright

# Infos utilisateur
USER_INFO = {
    'prenom': os.getenv('GR_PRENOM', ''),
    'nom': os.getenv('GR_NOM', ''),
    'email': os.getenv('GR_EMAIL', ''),
    'telephone': os.getenv('GR_TELEPHONE', ''),
    'compagnie': os.getenv('GR_COMPAGNIE', ''),
    'siteweb': os.getenv('GR_SITEWEB', ''),
    'ville': os.getenv('GR_VILLE', ''),
    'membre': os.getenv('GR_MEMBRE', 'true') == 'true'
}

def register_to_event(event_url: str, event_name: str = "Evenement"):
    """Inscrit l'utilisateur a un evenement GR International"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()

        # Auth via token
        member_url = os.getenv('GR_MEMBER_URL', '')
        if member_url:
            print('[AUTH] Connexion via token...')
            page.goto(member_url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            print('[OK] Connecte')

        print(f'\n{"="*50}')
        print(f'INSCRIPTION: {event_name}')
        print("="*50)

        try:
            page.goto(event_url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)

            # Cliquer sur 'Je veux participer'
            btn = page.query_selector('button:has-text("participer")')
            if not btn:
                buttons = page.query_selector_all('button, a.btn, input[type=button]')
                for b in buttons:
                    text = b.inner_text() or b.get_attribute('value') or ''
                    if 'participer' in text.lower():
                        btn = b
                        break

            if btn:
                btn.click()
                page.wait_for_timeout(3000)
                print('[OK] Formulaire ouvert')

            # Attendre que le modal soit visible
            page.wait_for_selector('form:visible, .modal:visible, [class*="modal"]:visible', timeout=5000)
            page.wait_for_timeout(1000)

            # Screenshot pour debug
            safe_name = event_name.replace(' ', '_').replace("'", '')[:20]
            page.screenshot(path=f'.tmp/modal_open_{safe_name}.png')

            # Remplir via JavaScript pour eviter les problemes de visibilite
            page.evaluate(f'''() => {{
                const inputs = document.querySelectorAll('input[type=text], input[type=email], input[type=tel]');
                const mapping = {{
                    'prenom': '{USER_INFO["prenom"]}',
                    'nom': '{USER_INFO["nom"]}',
                    'email': '{USER_INFO["email"]}',
                    'courriel': '{USER_INFO["email"]}',
                    'tel': '{USER_INFO["telephone"]}',
                    'phone': '{USER_INFO["telephone"]}',
                    'compagnie': '{USER_INFO["compagnie"]}',
                    'company': '{USER_INFO["compagnie"]}',
                    'site': '{USER_INFO["siteweb"]}',
                    'web': '{USER_INFO["siteweb"]}',
                    'ville': '{USER_INFO["ville"]}',
                    'city': '{USER_INFO["ville"]}'
                }};

                inputs.forEach(inp => {{
                    const name = (inp.name || '').toLowerCase();
                    const placeholder = (inp.placeholder || '').toLowerCase();

                    for (const [key, value] of Object.entries(mapping)) {{
                        if ((name.includes(key) || placeholder.includes(key)) && value && !inp.value) {{
                            inp.value = value;
                            inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            console.log('Filled:', key, value);
                            break;
                        }}
                    }}
                }});

                // Cocher Oui pour membre GR
                const radios = document.querySelectorAll('input[type=radio]');
                radios.forEach(r => {{
                    const label = r.nextSibling?.textContent || r.parentElement?.textContent || '';
                    if (label.toLowerCase().includes('oui')) {{
                        r.checked = true;
                        r.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }});
            }}''')

            print('[FILL] Champs remplis via JavaScript')
            page.wait_for_timeout(1000)

            # Screenshot avant envoi
            page.screenshot(path=f'.tmp/form_filled_{safe_name}.png')

            # Cliquer sur Envoyer
            submit_btn = page.query_selector('button:has-text("Envoyer"), input[value*="Envoyer"], button[type="submit"]')
            if not submit_btn:
                buttons = page.query_selector_all('button, input[type=submit]')
                for b in buttons:
                    text = (b.inner_text() or b.get_attribute('value') or '').lower()
                    if 'envoyer' in text or 'submit' in text:
                        submit_btn = b
                        break

            if submit_btn:
                submit_btn.click()
                page.wait_for_timeout(4000)
                print('[SUBMIT] Formulaire envoye')

                # Screenshot apres envoi
                page.screenshot(path=f'.tmp/form_result_{safe_name}.png')

                # Verifier le resultat
                body_text = page.inner_text('body').lower()

                if any(kw in body_text for kw in ['confirme', 'confirmed', 'succes', 'success', 'merci', 'thank', 'recu', 'inscription']):
                    print('[SUCCESS] INSCRIPTION CONFIRMEE!')
                    result = 'success'
                elif 'erreur' in body_text or 'error' in body_text:
                    print('[ERROR] Erreur lors de inscription')
                    result = 'error'
                else:
                    print('[INFO] Inscription soumise - verifier email de confirmation')
                    result = 'submitted'
            else:
                print('[WARN] Bouton Envoyer non trouve')
                result = 'no_submit'

        except Exception as e:
            print(f'[ERROR] {e}')
            page.screenshot(path=f'.tmp/error_{safe_name}.png')
            result = 'error'

        browser.close()
        return result


if __name__ == '__main__':
    # Événements à inscrire
    EVENTS = [
        {
            'name': '100% Web 1 Élite - 21 janvier 8h',
            'url': 'https://www.grinternational.ca/evenements/index.php?c=bWRISXpkY09HaHpjL1ZaTk1kNHNNRUpNM1E9PTo6NDAwYzE0MmVhZWRjMDg3Y2RkZWZmOTk1NWE0MjQ3Mjg'
        },
        {
            'name': 'Brossard 4 Élite - 22 janvier 11h30',
            'url': 'https://www.grinternational.ca/evenements/index.php?c=THQ3RlA5QjJOd2hlTjhmV0pvQnZPQ3RlS0E9PTo6YWFkOTE1M2YxYjdiOGMxZmEwZTBlMjZiMzlmZjYwOGE'
        }
    ]

    print('='*60)
    print('GR INTERNATIONAL - INSCRIPTION AUX ÉVÉNEMENTS')
    print('='*60)

    results = []
    for event in EVENTS:
        result = register_to_event(event['url'], event['name'])
        results.append({'event': event['name'], 'status': result})

    print('\n' + '='*60)
    print('RESUME DES INSCRIPTIONS')
    print('='*60)
    for r in results:
        status_icon = '[OK]' if r['status'] == 'success' else '[?]' if r['status'] == 'submitted' else '[X]'
        print(f"{status_icon} {r['event']}: {r['status']}")
