from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

class UserProfile(models.Model):
    """Extended user profile data representing optional contact tracking."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('User'))
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Address'))
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name=_('Profile Picture'))
    
    def __str__(self) -> str:
        if self.user and self.user.username:
            return f"{self.user.username}'s Profile"
        return "Unknown Profile"

class ItemReport(models.Model):
    """Central model tracking natively logged generic Lost and Found reports."""
    
    class ReportType(models.TextChoices):
        LOST = 'lost', _('Lost')
        FOUND = 'found', _('Found')
        
    class CategoryType(models.TextChoices):
        ELECTRONICS = 'electronics', _('Electronics / Mobile')
        WALLET = 'wallet', _('Wallet / Purse')
        KEYS = 'keys', _('Keys')
        PET = 'pet', _('Pet')
        BAG = 'bag', _('Bag / Luggage')
        DOCUMENT = 'document', _('Important Document')
        OTHER = 'other', _('Other')

    class StatusType(models.TextChoices):
        ACTIVE = 'active', _('Active')
        RESOLVED = 'resolved', _('Resolved')

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('User'))
    report_type = models.CharField(max_length=10, choices=ReportType.choices, verbose_name=_('Report Type'))
    category = models.CharField(max_length=20, choices=CategoryType.choices, verbose_name=_('Category'))
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    
    location_name = models.CharField(max_length=255, verbose_name=_('Location Name'))
    latitude = models.FloatField(null=True, blank=True, verbose_name=_('Latitude'))
    longitude = models.FloatField(null=True, blank=True, verbose_name=_('Longitude'))
    accuracy = models.FloatField(null=True, blank=True, help_text=_("Location accuracy in meters"), verbose_name=_('Accuracy'))
    
    date_reported = models.DateTimeField(auto_now_add=True, verbose_name=_('Date Reported'))
    item_date = models.DateField(help_text=_("When was the item lost/found?"), null=True, blank=True, verbose_name=_('Item Date'))
    
    status = models.CharField(max_length=10, choices=StatusType.choices, default=StatusType.ACTIVE, verbose_name=_('Status'))
    contact_info = models.TextField(help_text=_("How can people contact you? (Email/Phone)"), verbose_name=_('Contact Info'))
    photo = models.ImageField(upload_to='item_photos/', null=True, blank=True, verbose_name=_('Photo'))

    def __str__(self) -> str:
        report_display = self.get_report_type_display() if self.report_type else "Unknown"
        return f"[{report_display}] {self.title or 'Unnamed Item'}"

    @property
    def is_resolved(self):
        return self.status == self.StatusType.RESOLVED

class Message(models.Model):
    """Internal user-to-user secure messaging system handling item claims."""
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE, verbose_name=_('Sender'))
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE, verbose_name=_('Recipient'))
    item = models.ForeignKey(ItemReport, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Item'))
    body = models.TextField(verbose_name=_('Body'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Timestamp'))
    read = models.BooleanField(default=False, verbose_name=_('Read'))

    def __str__(self) -> str:
        sender_name = getattr(self.sender, 'username', 'Unknown Sender')
        recipient_name = getattr(self.recipient, 'username', 'Unknown Recipient')
        return f"Message from {sender_name} to {recipient_name}"

class EmailOTP(models.Model):
    """Unified OTP management for Signup, Login, and Password Reset flows."""
    class OTPType(models.TextChoices):
        SIGNUP = 'signup', _('Signup Verification')
        LOGIN = 'login', _('Login 2FA')
        PASSWORD_RESET = 'password_reset', _('Password Reset')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTPType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        # OTP is valid for 5 minutes and limited to 5 attempts
        return not self.is_used and timezone.now() < self.created_at + timedelta(minutes=5) and self.attempts < 5

    def __str__(self):
        return f"{self.otp_type} for {self.user.username}"
