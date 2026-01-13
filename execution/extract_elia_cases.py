#!/usr/bin/env python3
"""
Extrait le contenu des 100 cas d'utilisation du fichier DOCX vers un fichier Markdown lisible
pour faciliter la création des directives.
"""

from docx import Document
from pathlib import Path
import re

def extract_cases_to_md():
    input_path = Path("directives/elia/Propositions/ELIA_100_CAS_UTILISATION_ANTIGRAVITY.docx")
    output_path = Path("directives/elia/EXTRACTED_CASES.md")
    
    if not input_path.exists():
        print(f"[ERREUR] Le fichier {input_path} n'existe pas.")
        return

    print(f"[INFO] Lecture du document: {input_path}")
    doc = Document(input_path)
    
    content = []
    content.append("# EXTRACTION DES 100 CAS D'UTILISATION ÉLIA")
    content.append(f"Source: {input_path.name}\n")
    
    current_case = {}
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # Détection des titres de cas (souvent "CAS #X : ...")
        if re.match(r"CAS #\d+", text, re.IGNORECASE):
            content.append(f"## {text}")
        elif text.startswith("Question :") or text.startswith("Verticale :") or text.startswith("Rôle :") or text.startswith("Résultats Attendus :"):
            content.append(f"- **{text}**")
        elif text.startswith("Tâches ÉLIA") or text.startswith("Tâches Antigravity"):
             content.append(f"### {text}")
        else:
            content.append(text)
            
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(content))
        
    print(f"[SUCCÈS] Contenu extrait vers {output_path}")

if __name__ == "__main__":
    extract_cases_to_md()
