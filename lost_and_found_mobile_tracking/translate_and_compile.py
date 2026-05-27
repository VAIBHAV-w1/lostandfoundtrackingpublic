import json
import os
import polib
from deep_translator import GoogleTranslator

# Extra strings that must always be included regardless of template extraction
EXTRA_STRINGS = [
    "LostFound",
    "Lost",
    "Found",
    "Electronics",
    "Clothing",
    "Documents",
    "Accessories",
    "Pets",
    "Keys",
    "Wallet",
    "Bag",
    "Other",
    "Active",
    "Resolved",
    "Dashboard",
    "Find Items",
    "Report Item",
    "About Us",
    "Contact",
    "Sign in",
    "Sign out",
    "Get started",
    "Platform",
    "Company",
    "Support",
    "Privacy Policy",
    "Terms of Service",
    "Status: Online",
    "Version 1.0.4",
    "My Account",
    "My Reports",
    "Unread Messages",
    "Messages",
    "LostFound Assistant",
    "Done",
    "View",
    "Resolve",
    "No reports yet",
    "Report your first item",
    "No messages yet",
    "Search items\u2026",
    "Toggle Theme",
    "Username",
    "Password",
    "Forgot Password?",
    "Sign In",
    "No account?",
    "Create one free \u2192",
    "Verify Now",
    "Enter Code",
    "OTP Verified!",
    "Case Info",
    "Safety tip:",
    "Always meet in public, well-lit locations for handovers.",
    "Start the conversation",
    "Introduce yourself and explain how you can help.",
    "Type a message\u2026",
    "View Report",
    "Re:",
    "Precision:",
    "Lost",
    "Found",
    "View \u2192",
    "No recent activity yet",
    "Submit Report",
    "Location",
    "Description",
    "Category",
    "Date",
    "Photo",
    "Photo & Contact",
    "Incident Date",
    "When was the item lost/found?",
    "Report an Item",
    "About",
    "New Report",
    "+ New",
]

def build_po_and_compile(lang_code, lang_name, strings):
    locale_dir = os.path.join(os.getcwd(), 'locale', lang_code, 'LC_MESSAGES')
    os.makedirs(locale_dir, exist_ok=True)
    
    po_file = polib.POFile()
    po_file.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': '',
        'POT-Creation-Date': '2023-01-01 12:00+0000',
        'PO-Revision-Date': '2023-01-01 12:00+0000',
        'Last-Translator': 'Auto',
        'Language-Team': f'{lang_name}',
        'Language': lang_code,
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }

    translator = GoogleTranslator(source='en', target=lang_code)
    
    batch = []
    entry_map = []  # (index_in_po_file, batch_index)
    
    for s in strings:
        if not s.strip():
            entry = polib.POEntry(msgid=s, msgstr=s)
            po_file.append(entry)
        else:
            entry = polib.POEntry(msgid=s, msgstr=s)
            idx = len(po_file)
            po_file.append(entry)
            batch.append(s)
            entry_map.append(idx)

    chunk_size = 50
    for i in range(0, len(batch), chunk_size):
        chunk = batch[i:i+chunk_size]
        print(f"[{lang_code}] Translating {i}..{i+len(chunk)}/{len(batch)}...")
        try:
            translations = translator.translate_batch(chunk)
            for j, t in enumerate(translations):
                if t:
                    t = t.replace('% (', '%(').replace(') s', ')s').replace(') d', ')d')
                    po_file[entry_map[i+j]].msgstr = t
        except Exception as e:
            print(f"[{lang_code}] Error: {e}")

    po_path = os.path.join(locale_dir, 'django.po')
    mo_path = os.path.join(locale_dir, 'django.mo')
    po_file.save(po_path)
    po_file.save_as_mofile(mo_path)
    print(f"[{lang_code}] Done! {len(batch)} strings translated.")

def main():
    with open('extracted_strings.json', 'r', encoding='utf-8') as f:
        strings = json.load(f)
    
    # Merge extra strings, deduplicate
    all_strings = list(dict.fromkeys(strings + EXTRA_STRINGS))
    print(f"Total {len(all_strings)} unique strings to translate.")
    
    build_po_and_compile('hi', 'Hindi', all_strings)
    build_po_and_compile('kn', 'Kannada', all_strings)

if __name__ == "__main__":
    main()
