# LostFound — Professional Asset Recovery & Coordination Network

## Short Description
A generalized, secure, and localization-supported Lost and Found tracking platform built in Django. Allows users to report lost or found assets, pinpoint geographical coordinates on an interactive map, and securely communicate through P2P chats to coordinate recoveries.

## Features
*   **Interactive Leaflet Mapping**: Real-time geospatial tracking with dynamic, light/dark map tiles.
*   **Accurate GPS Geotracking**: Single-button high-accuracy geolocating and Nominatim reverse-geocoding into clean address labels.
*   **Automated Proximity Matching**: Smart trigonometric calculations matching reports within a 10km radius.
*   **Secure Internal Chat**: Fully isolated user-to-user messenger to coordinate verification and recovery securely.
*   **Dual Theme Options**: Elegant Obsidian dark mode and minimal Pearl light mode support.
*   **Localization & 2FA**: English, Hindi, and Kannada translation catalogs with email-delivered OTP authentication.

## Tech Stack
*   **Backend**: Python 3.11, Django 5.2
*   **Frontend**: HTML5, CSS3 (Premium Classy UI), Vanilla JavaScript, Leaflet.js
*   **Database**: SQLite (db_new.sqlite3)
*   **Localization**: Polib, GNU gettext i18n

## Project Structure
```
django-lost-and-found/
├── lost_and_found_mobile_tracking/
│   ├── locale/                 # Translation catalogs (hi, kn)
│   ├── lost_and_found_mobile_tracking/ # Inner project config
│   ├── media/                  # Uploaded item photos
│   ├── static/                 # Stylesheets (modern.css), JS scripts
│   ├── tracker/                # App models, forms, templates, views
│   ├── manage.py               # Django execution script
│   ├── setup_database.py       # Database initialization and setup script
├── requirements.txt            # Package dependencies
├── .gitignore                  # Git exclude criteria
```

## Installation
```bash
git clone https://github.com/VAIBHAV-w1/lostandfoundtrackingpublic.git

cd lostandfoundtrackingpublic/django-lost-and-found/lost_and_found_mobile_tracking

pip install -r ../requirements.txt

python manage.py runserver
```

## Screenshots
*   **Home Recovery Dashboard**: Mapped active items, metrics count cards, and activity feeds.
*   **Platform Technical Specs**: Factual operational guides and architecture diagrams.
*   **Item Detail & Coordination Messaging**: Interactive Leaflet maps, photo evidence, and live secure chat box interfaces.
*   **Accurate Geotracking Form**: Type toggles, high-accuracy geolocation triggers, and reverse Nominatim API resolving.

## Future Improvements
*   Automated AI image classification for categorical match suggestions.
*   Push notifications via secure webhooks (Telegram or WhatsApp integrations).
*   Multi-country localization bounds scaling.

## Author
Vaibhav S Wandkar
