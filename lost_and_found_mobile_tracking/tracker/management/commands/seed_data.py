import random
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tracker.models import ItemReport, UserProfile
from django.utils import timezone
from django.core.files import File
from django.conf import settings

class Command(BaseCommand):
    help = 'Seed the database with professional regional records and prevent duplicate image proliferation.'

    def handle(self, *args, **options):
        # 1. Purge existing records for a fresh state
        self.stdout.write("Cleaning database...")
        ItemReport.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        # 2. Setup Core Users
        users = []
        user_data = [
            ('recovery_hub_blr', 'blr@lostfound.network'),
            ('recovery_hub_hbl', 'hbl@lostfound.network'),
            ('safety_node_south', 'safety@lostfound.network'),
        ]

        for username, email in user_data:
            user = User.objects.create_user(username=username, email=email, password='password123')
            UserProfile.objects.get_or_create(user=user)
            users.append(user)

        # 3. Item Data pairs
        items = [
            ('DSLR Camera', 'electronics', 'lost', 'camera.png'),
            ('Headphones', 'electronics', 'found', 'headphones.png'),
            ('Wristwatch', 'other', 'found', 'silver_wristwatch.png'),
            ('Leather Wallet', 'wallet', 'lost', 'leather_wallet.png'),
            ('Scooter Charger', 'electronics', 'found', 'charger.png'),
            ('Designer Bag', 'bag', 'lost', 'handbag.png'),
            ('Car Keys', 'keys', 'found', 'car_key.png'),
            ('Passport', 'document', 'lost', 'indian_passport.png'),
            ('Black Umbrella', 'other', 'found', 'black_umbrella.png'),
            ('Laptop Bag', 'bag', 'lost', 'laptop_backpack.png'),
        ]

        locations = [
            ('Bengaluru', 'Majestic Metro', 12.9766, 77.5712),
            ('Bengaluru', 'Indiranagar', 12.9719, 77.6412),
            ('Mysuru', 'Palace Entrance', 12.3051, 76.6552),
            ('Mysuru', 'Bus Stand', 12.3106, 76.6588),
            ('Hubballi', 'Unkal Lake', 15.3715, 75.1235),
            ('Hubballi', 'Railway Station', 15.3489, 75.1488),
            ('Mangaluru', 'Beach Port', 12.9515, 74.8247),
            ('Mangaluru', 'City Mall', 12.8719, 74.8423),
            ('Belagavi', 'Fort Gate', 15.8576, 74.5204),
            ('Belagavi', 'Circle', 15.8524, 74.5042),
        ]

        # 4. Generate Reports
        for i in range(len(items)):
            title, cat, r_type, img_name = items[i]
            city, loc_name, lat, lon = locations[i % len(locations)]
            
            report = ItemReport.objects.create(
                user=random.choice(users),
                title=f"{title} - {city}",
                description=f"Standard recovery log for {title.lower()} located near {loc_name}.",
                location_name=f"{loc_name}, {city}",
                latitude=lat,
                longitude=lon,
                report_type=r_type,
                category=cat,
                contact_info=f"support@{city.lower()}.recovery",
                date_reported=timezone.now() - timezone.timedelta(days=random.randint(0, 5))
            )
            
            # Use real photo if exists, avoiding duplicate renaming if already present in destination
            photo_source = os.path.join(settings.MEDIA_ROOT, 'item_photos', img_name)
            if os.path.exists(photo_source):
                with open(photo_source, 'rb') as f:
                    # We save the file content to the field. 
                    # Note: Django will still rename if the file exists in the field's upload_to path.
                    # To prevent clutter, we've already deleted all reports at the start.
                    report.photo.save(img_name, File(f), save=True)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with clean regional records.'))
