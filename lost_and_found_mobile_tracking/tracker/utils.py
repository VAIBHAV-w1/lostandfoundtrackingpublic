import math
import logging
import threading
from typing import Optional
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def calculate_distance(lat1: Optional[float], lon1: Optional[float], lat2: Optional[float], lon2: Optional[float]) -> float:
    """Calculates the geographic distance between two coordinates in kilometers."""
    if None in [lat1, lon1, lat2, lon2]:
        return 999999.0
    try:
        R = 6371.0
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    except Exception as exc:
        logger.error(f"Error calculating distance: {exc}")
        return 999999.0

def send_email_async(subject: str, message: str, recipient_email: str, html_message: str = None):
    """Spawns a background thread to send an email notification."""
    threading.Thread(target=_send_email_thread, args=(subject, message, recipient_email, html_message), daemon=True).start()

def _send_email_thread(subject: str, message: str, recipient_email: str, html_message: str = None):
    """Internal SMTP dispatch with detailed logging."""
    try:
        sent_count = send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
            html_message=html_message
        )
        if sent_count:
            logger.info(f"Email sent successfully to {recipient_email} (Subject: {subject})")
        else:
            logger.warning(f"Email appeared to send but sent_count was 0 for {recipient_email}")
    except Exception as e:
        logger.error(f"CRITICAL: SMTP Email failure for {recipient_email}: {str(e)}")
        # In development, print to console as well for immediate visibility
        if settings.DEBUG:
            print(f"\n[EMAIL DEBUG ERROR] To: {recipient_email}\nSubject: {subject}\nError: {e}\n")
