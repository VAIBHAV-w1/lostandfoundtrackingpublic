import os
import django
from django.utils import timezone
from datetime import date
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lost_and_found_mobile_tracking.settings')
django.setup()

from django.contrib.auth.models import User
from tracker.models import UserProfile, ItemReport

def populate():
    print("Clearing existing data (except admin)...")
    # Keep admin, delete others
    User.objects.exclude(is_superuser=True).delete()
    
    # Create dummy users
    u1, _ = User.objects.get_or_create(username='john_doe', email='john@example.com')
    u1.set_password('password123')
    u1.save()
    UserProfile.objects.get_or_create(user=u1)

    u2, _ = User.objects.get_or_create(username='jane_smith', email='jane@example.com')
    u2.set_password('password123')
    u2.save()
    UserProfile.objects.get_or_create(user=u2)

    # Dummy Items (Expanded Karnataka distribution)
    items = [
        {
            'user': u1, 'report_type': 'lost', 'category': 'electronics',
            'title': 'Samsung Galaxy S23 - Cream',
            'description': 'Lost in a rickshaw between Koramangala 4th Block and Sony World Signal.',
            'location_name': 'Koramangala, Bengaluru',
            'latitude': 12.9352, 'longitude': 77.6245,
            'item_date': date(2026, 4, 1), 'contact_info': 'Contact John at 1112223333',
            'image_filename': 'samsung.png'
        },
        {
            'user': u2, 'report_type': 'found', 'category': 'wallet',
            'title': 'Black Men\'s Wallet',
            'description': 'Found near the Indiranagar Metro Station entrance. Contains a driving license.',
            'location_name': 'Indiranagar, Bengaluru',
            'latitude': 12.9719, 'longitude': 77.6412,
            'item_date': date(2026, 4, 3), 'contact_info': 'Found by Jane. Contact via app.',
            'image_filename': 'wallet.png'
        },
        {
            'user': u1, 'report_type': 'lost', 'category': 'pet',
            'title': 'Beagle - "Lucy"',
            'description': 'Lucy went missing from HSR Layout Sector 2. Pink collar.',
            'location_name': 'HSR Layout, Bengaluru',
            'latitude': 12.9121, 'longitude': 77.6446,
            'item_date': date(2026, 4, 5), 'contact_info': 'Call 1112223333. Reward!',
            'image_filename': 'beagle.png'
        },
        {
            'user': u2, 'report_type': 'found', 'category': 'keys',
            'title': 'Royal Enfield Bike Keys',
            'description': 'Found near UB City mall parking area.',
            'location_name': 'MG Road, Bengaluru',
            'latitude': 12.9750, 'longitude': 77.5910,
            'item_date': date(2026, 4, 2), 'contact_info': 'Left with the UB City security.',
            'image_filename': 'keys.png'
        },
        {
            'user': u1, 'report_type': 'lost', 'category': 'bag',
            'title': 'Blue Backpack with Laptop',
            'description': 'Left in a BMTC Volvo bus (Route 500C).',
            'location_name': 'Whitefield, Bengaluru',
            'latitude': 12.9698, 'longitude': 77.7500,
            'item_date': date(2026, 4, 6), 'contact_info': 'Contact John at 1112223333',
            'image_filename': 'backpack.png'
        },
        {
            'user': u2, 'report_type': 'lost', 'category': 'other',
            'title': 'Gold Necklace',
            'description': 'Lost near Gokul Road during a wedding procession.',
            'location_name': 'Hubballi (Hubli)',
            'latitude': 15.3647, 'longitude': 75.1240,
            'item_date': date(2026, 4, 10), 'contact_info': 'Contact Jane.',
            'image_filename': 'necklace.png'
        },
        {
            'user': u1, 'report_type': 'found', 'category': 'electronics',
            'title': 'DSLR Camera - Canon',
            'description': 'Found at KC Circle near the bus stand.',
            'location_name': 'Dharwad',
            'latitude': 15.4589, 'longitude': 75.0078,
            'item_date': date(2026, 4, 12), 'contact_info': 'In safe custody, provide proof to claim.',
            'image_filename': 'camera.png'
        },
        {
            'user': u2, 'report_type': 'lost', 'category': 'bag',
            'title': 'Leather Briefcase',
            'description': 'Lost in the Camp Area near the market.',
            'location_name': 'Belgavi (Belgaum)',
            'latitude': 15.8497, 'longitude': 74.4977,
            'item_date': date(2026, 4, 14), 'contact_info': 'Contact 9988776655.',
            'image_filename': 'briefcase.png'
        },
        {
            'user': u1, 'report_type': 'found', 'category': 'other',
            'title': 'Modern Spectacles',
            'description': 'Found near Gadag-Betageri railway station.',
            'location_name': 'Gadag',
            'latitude': 15.4320, 'longitude': 75.6450,
            'item_date': date(2026, 4, 15), 'contact_info': 'Claim at station master office.',
            'image_filename': 'spectacles.png'
        },
        {
            'user': u2, 'report_type': 'lost', 'category': 'keys',
            'title': 'Large Key Bunch',
            'description': 'Lost in Mallekatte village near the temple.',
            'location_name': 'Mallekatte, Haveri',
            'latitude': 14.7937, 'longitude': 75.4055,
            'item_date': date(2026, 4, 16), 'contact_info': 'Contact 9900887766.',
            'image_filename': 'keybunch.png'
        }
    ]


    sample_images_dir = 'sample_images'

    for item_data in items:
        image_filename = item_data.pop('image_filename', None)
        report = ItemReport.objects.create(**item_data)
        
        if image_filename:
            image_path = os.path.join(sample_images_dir, image_filename)
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    report.photo.save(image_filename, File(f), save=True)
        
        print(f"Created item: {report.title}")

    print("Population complete.")

if __name__ == '__main__':
    populate()

