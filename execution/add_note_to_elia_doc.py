#!/usr/bin/env python3
"""
Ajoute une note explicative sur l'infrastructure Antigravity
au début du document des 100 cas d'utilisation ELIA.
"""

from docx import Document
from pathlib import Path
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_intro_note():
    file_path = Path("directives/elia/Propositions/ELIA_100_CAS_UTILISATION_ANTIGRAVITY.docx")
    
    print(f"[INFO] Ouverture du document: {file_path}")
    doc = Document(file_path)
    
    # Créer un nouveau contenu à insérer au début
    # On insère au début en insérant un paragraphe avant le premier
    
    note_title = "NOTE IMPORTANTE SUR L'INFRASTRUCTURE 2026 (ANTIGRAVITY)"
    note_text = (
        "Ce document a été mis à jour pour refléter la migration vers l'infrastructure 'Antigravity'. "
        "Contrairement à l'ancienne architecture 'Manus', Antigravity offre :\n\n"
        "1. Une autonomie réelle : ELIA ne fait pas que répondre, elle agit directement dans les systèmes.\n"
        "2. Accès 'Full Zoho One' : Plus de limites d'API, ELIA voit et interagit avec TOUT Zoho comme un humain.\n"
        "3. Sécurité accrue : Exécution locale sécurisée des données sensibles.\n"
        "4. Mémoire unifiée : Notion sert de cerveau central unique pour toutes les procédures (SOPs).\n\n"
        "Les 100 cas ci-dessous bénéficient tous de cette augmentation de capacité, rendant l'exécution plus rapide et plus fiable."
    )
    
    # Insérer avant le premier paragraphe
    p = doc.paragraphs[0]
    
    # Insérer le titre
    title_run = p.insert_paragraph_before(note_title).runs[0]
    title_run.bold = True
    title_run.font.size = 160000 # ~12pt (valeur arbitraire docx)
    
    # Insérer le texte
    text_p = p.insert_paragraph_before(note_text)
    
    # Insérer un séparateur
    p.insert_paragraph_before("-" * 50)
    
    print(f"[INFO] Sauvegarde du document avec la note ajoutée.")
    doc.save(file_path)
    
    print(f"\n[SUCCÈS] Note ajoutée au début du fichier: {file_path}")

if __name__ == "__main__":
    add_intro_note()
