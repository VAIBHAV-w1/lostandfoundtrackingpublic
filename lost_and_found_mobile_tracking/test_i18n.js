const fs = require('fs');
const jsdom = require('jsdom');
const { JSDOM } = jsdom;
const code = fs.readFileSync('c:/Users/vaibh/OneDrive/Desktop/lostandfoundtrackingpublic/django-lost-and-found/lost_and_found_mobile_tracking/static/js/i18n.js', 'utf-8');

const html = `<!DOCTYPE html>
<html>
<head>
  <title>Sign In</title>
</head>
<body>
  <div id="lang-indicator">EN</div>
  <div>Welcome back</div>
  <script>
    ${code}
    
    // Simulate DOMContentLoaded
    document.dispatchEvent(new Event('DOMContentLoaded'));
  </script>
</body>
</html>`;

const dom = new JSDOM(html, { runScripts: "dangerously" });

try {
  console.log('Before change, indicator:', dom.window.document.getElementById('lang-indicator').textContent);
  dom.window.setLanguage('hi');
  console.log('After change, indicator:', dom.window.document.getElementById('lang-indicator').textContent);
} catch (e) {
  console.error(e);
}
