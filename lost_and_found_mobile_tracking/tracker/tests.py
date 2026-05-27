from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import ItemReport, UserProfile, Message
from django.urls import reverse

class BasicSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
        self.profile, _ = UserProfile.objects.get_or_create(user=self.user)

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login_flow(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302) # Redirects to home or profile

    def test_report_item_creation(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('report_item'), {
            'title': 'Test Item',
            'report_type': 'lost',
            'category': 'electronics',
            'description': 'Test Description',
            'location_name': 'Test Location',
            'contact_info': 'test@test.com'
        })
        self.assertEqual(ItemReport.objects.count(), 1)
        self.assertEqual(ItemReport.objects.first().title, 'Test Item')

    def test_messaging_flow(self):
        other_user = User.objects.create_user(username="otheruser", password="password123")
        report = ItemReport.objects.create(
            user=other_user, 
            title="Lost Phone", 
            report_type="lost", 
            category="electronics", 
            location_name="Node A"
        )
        
        self.client.login(username='testuser', password='password123')
        # Initial message
        response = self.client.post(reverse('send_message', args=[report.id]), {
            'body': 'Hello, I found it!'
        })
        self.assertEqual(Message.objects.count(), 1)
        
        # Check thread
        response = self.client.get(reverse('chat_thread', args=[report.id, other_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hello, I found it!')
