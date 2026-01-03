
import os
import sys
from dotenv import load_dotenv

# Add the current directory to sys.path to ensure we can import zoho_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from zoho_client import ZohoClient

def verify_zoho_books():
    """Vérifie la connexion à Zoho Books et liste les factures récentes."""
    print("--- Vérification de l'intégration Zoho Books ---")
    
    try:
        # Initialisation du client (charge les vars d'env automatiquement)
        client = ZohoClient()
        print("1. Initialisation du client ZohoClient: OK")
        
        # Test de récupération de token (force le refresh si nécessaire)
        token = client.access_token
        print(f"2. Authentification (Access Token): OK (Token partiel: {token[:10]}...)")
        
        # Test Lister les factures
        print("\n3. Tentative de listage des factures (paires)...")
        invoices = client.books_list_invoices()
        
        print(f"   Succès ! {len(invoices)} factures trouvées.")
        
        if invoices:
            print("\n   Détails des 3 dernières factures :")
            for inv in invoices[:3]:
                print(f"   - Facture #{inv.get('invoice_number')} | Client: {inv.get('customer_name')} | Montant: {inv.get('total')} {inv.get('currency_code')} | Statut: {inv.get('status')}")
        else:
            print("   Aucune facture trouvée pour le moment.")
            
        return True

    except Exception as e:
        print(f"\nERREUR CRITIQUE lors de la vérification : {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    load_dotenv()
    success = verify_zoho_books()
    if success:
        print("\n--- VÉRIFICATION RÉUSSIE ---")
    else:
        print("\n--- ÉCHEC DE LA VÉRIFICATION ---")
