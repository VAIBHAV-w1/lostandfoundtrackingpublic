import os, re, json

def extract_strings(directory):
    strings = set()
    trans_re = re.compile(r'{%\s*trans\s+[\"\'](.*?)[\"\']\s*%}')
    blocktrans_re = re.compile(r'{%\s*blocktrans.*?%}(.*?){%\s*endblocktrans\s*%}', re.DOTALL)
    gettext_re = re.compile(r'_\([\"\'](.*?)[\"\']\)')
    gettext_lazy_re = re.compile(r'gettext_lazy\([\"\'](.*?)[\"\']\)')
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html') or file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for match in trans_re.findall(content): strings.add(match)
                    for match in blocktrans_re.findall(content):
                        clean = match.strip()
                        if clean:
                            clean = re.sub(r'{{\s*(.*?)\s*}}', r'%(\1)s', clean)
                            strings.add(clean)
                    for match in gettext_re.findall(content): strings.add(match)
                    for match in gettext_lazy_re.findall(content): strings.add(match)
    return list(strings)

s = extract_strings(r'c:/Users/vaibh/OneDrive/Desktop/lostandfoundtrackingpublic/django-lost-and-found/lost_and_found_mobile_tracking/tracker')
with open('extracted_strings.json', 'w', encoding='utf-8') as f: 
    json.dump(s, f, indent=2, ensure_ascii=False)
print(f'Extracted {len(s)} strings.')
