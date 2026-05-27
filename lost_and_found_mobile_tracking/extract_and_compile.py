import os
import re
import polib

def extract_strings(directory):
    strings = set()
    
    # Regex patterns
    trans_re = re.compile(r'{%\s*trans\s+["\'](.*?)["\']\s*%}')
    blocktrans_re = re.compile(r'{%\s*blocktrans.*?%}(.*?){%\s*endblocktrans\s*%}', re.DOTALL)
    gettext_re = re.compile(r'_\(["\'](.*?)["\']\)')
    gettext_lazy_re = re.compile(r'gettext_lazy\(["\'](.*?)["\']\)')
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html') or file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract {% trans %}
                    for match in trans_re.findall(content):
                        strings.add(match)
                        
                    # Extract {% blocktrans %}
                    for match in blocktrans_re.findall(content):
                        # Clean up blocktrans content (remove variables and newlines)
                        # Actually blocktrans keeps variables like {{ var }}, which in PO become %(var)s usually.
                        # But Django extraction is complex. We'll just take the exact string or close to it.
                        clean = match.strip()
                        if clean:
                            # basic replacement of {{ var }} to %(var)s for gettext
                            clean = re.sub(r'{{\s*(.*?)\s*}}', r'%(\1)s', clean)
                            strings.add(clean)
                            
                    # Extract _("")
                    for match in gettext_re.findall(content):
                        strings.add(match)
                        
                    # Extract gettext_lazy("")
                    for match in gettext_lazy_re.findall(content):
                        strings.add(match)
                        
    return list(strings)

def main():
    base_dir = r"c:\Users\vaibh\OneDrive\Desktop\lostandfoundtrackingpublic\django-lost-and-found\lost_and_found_mobile_tracking"
    locale_dir = os.path.join(base_dir, "locale")
    
    strings = extract_strings(base_dir)
    print(f"Extracted {len(strings)} unique strings.")
    
    # We will save the extracted strings to a json file to be translated by the LLM
    import json
    with open("extracted_strings.json", "w", encoding="utf-8") as f:
        json.dump(strings, f, indent=2, ensure_ascii=False)
        
if __name__ == "__main__":
    main()
