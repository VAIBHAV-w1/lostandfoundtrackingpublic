import polib, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
for lang in ['hi', 'kn']:
    po = polib.pofile(f'locale/{lang}/LC_MESSAGES/django.po')
    for e in po:
        if e.msgid in ['LostFound', 'Lost', 'Found', 'Dashboard', 'Sign In', 'Electronics', 'Wallet']:
            print(f'[{lang}] "{e.msgid}" => "{e.msgstr}"')
