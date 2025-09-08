import os
import re

LOCALE_DIR = os.path.join(os.getcwd(), "locale")

# Regex pour placeholders Python
placeholder_re = re.compile(r'%(\d+\$)?[sdf]')

def fix_po_file(po_file):
    with open(po_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    msgid, msgstr = "", ""
    in_msgid = False
    in_msgstr = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("msgid "):
            msgid = stripped
            in_msgid = True
            in_msgstr = False
        elif stripped.startswith("msgstr "):
            msgstr = stripped
            in_msgstr = True
            in_msgid = False

            # Corriger les \n au début
            if msgid.startswith('msgid "\n') and not msgstr.startswith('msgstr "\n'):
                line = 'msgstr "\n"\n'  # ligne vide avec \n
            elif msgstr.startswith('msgstr "\n') and not msgid.startswith('msgid "\n'):
                line = 'msgstr ""\n'

            # Corriger les placeholders
            placeholders_id = placeholder_re.findall(msgid)
            placeholders_str = placeholder_re.findall(msgstr)
            if placeholders_id != placeholders_str:
                # Copier placeholders de msgid dans msgstr
                line = re.sub(r'msgstr\s+".*"', f'msgstr "{msgid[6:-1]}"', line)

        new_lines.append(line)

    with open(po_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def main():
    for root, dirs, files in os.walk(LOCALE_DIR):
        for file in files:
            if file.endswith(".po"):
                po_path = os.path.join(root, file)
                print(f"Correction automatique: {po_path}")
                fix_po_file(po_path)

if __name__ == "__main__":
    main()
