import webbrowser
import os
import time

def setup_reddit():
    print("============================================")
    print("🤖 CONFIGURATION AUTOMATIQUE REDDIT API 🤖")
    print("============================================")
    print("\nJe vais ouvrir la page des applications Reddit dans votre navigateur...")
    print("Pour continuer, vous devrez être connecté à votre compte Reddit.")
    
    time.sleep(2)
    webbrowser.open('https://www.reddit.com/prefs/apps')
    
    print("\n---------------------------------------------------------")
    print("INSTRUCTIONS (Une fois la page ouverte) :")
    print("1. Cliquez sur le bouton 'create another app' ou 'create app' (en bas)")
    print("2. Remplissez le formulaire comme suit :")
    print("   - name: Atlas Scraper")
    print("   - type: cochez la case 'script'")
    print("   - description: Atlas AI Pain Point Analysis")
    print("   - about url: (laisser vide)")
    print("   - redirect uri: http://localhost:8080")
    print("3. Cliquez sur 'create app'")
    print("---------------------------------------------------------")
    
    input("\nAppuyez sur ENTRÉE une fois que vous avez créé l'app pour continuer...")

    print("\nMaintenant, récupérons les credentials :")
    
    print("\n1. REDDIT_CLIENT_ID")
    print("   C'est la chaîne de caractères (ex: 'PfX_blah_blah') située juste SOUS le nom 'Atlas Scraper'.")
    client_id = input("   >>> Collez le CLIENT_ID ici : ").strip()

    print("\n2. REDDIT_CLIENT_SECRET")
    print("   C'est la longue chaîne à côté du champ 'secret'.")
    client_secret = input("   >>> Collez le CLIENT_SECRET ici : ").strip()

    print("\n3. REDDIT_USER_AGENT")
    print("   Quel est votre nom d'utilisateur Reddit (sans le /u/) ?")
    username = input("   >>> Votre username Reddit : ").strip()
    user_agent = f"windows:atlas_scraper:v1.0 (by /u/{username})"

    # Sauvegarde dans .env
    env_content = f"\n\n# ============================================\n# REDDIT API\n# ============================================\nREDDIT_CLIENT_ID={client_id}\nREDDIT_CLIENT_SECRET={client_secret}\nREDDIT_USER_AGENT={user_agent}\n"
    
    env_path = '.env'
    
    # Vérifie si le fichier existe
    if not os.path.exists(env_path):
        # Si .env n'existe pas, on le crée depuis .env.example s'il existe
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                base_content = f.read()
            with open(env_path, 'w') as f:
                f.write(base_content)
        else:
            open(env_path, 'w').close()

    # Ajout des credentials
    with open(env_path, 'a') as f:
        f.write(env_content)
        
    print(f"\n✅ Succès ! Les credentials ont été ajoutés à {os.path.abspath(env_path)}")
    print("Vous êtes prêt à scraper !")

if __name__ == "__main__":
    setup_reddit()
