import os
import re

# Chemin vers le dossier locale de ton projet
LOCALE_DIR = os.path.join(os.getcwd(), "locale")

# Regex pour détecter les placeholders Python (%s, %d, %f)
placeholder_re = re.compile(r'%(\d+\$)?[sdf]')

def check_po_file(po_file):
    with open(po_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    msgid, msgstr = "", ""
    line_num = 0
    errors = []

    for idx, line in enumerate(lines):
        line_num = idx + 1
        line = line.strip()

        if line.startswith("msgid "):
            msgid = line
        elif line.startswith("msgstr "):
            msgstr = line

            # Vérifier les \n
            if msgid.startswith('msgid "\n') != msgstr.startswith('msgstr "\n'):
                errors.append((line_num, "Incohérence \\n entre msgid et msgstr"))

            # Vérifier les placeholders
            placeholders_id = placeholder_re.findall(msgid)
            placeholders_str = placeholder_re.findall(msgstr)
            if placeholders_id != placeholders_str:
                errors.append((line_num, f"Placeholders différents: {placeholders_id} vs {placeholders_str}"))

    return errors
def main():
    found = False
    for root, dirs, files in os.walk(LOCALE_DIR):
        for file in files:
            if file.endswith(".po"):
                found = True
                po_path = os.path.join(root, file)
                print(f"Trouvé: {po_path}")
    if not found:
        print("Aucun fichier .po trouvé ! Vérifie le chemin.")

if __name__ == "__main__":
    main()
