from django.conf import settings
from datetime import datetime

def site_context(request):
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'DEBUG': settings.DEBUG,
        'CURRENT_YEAR': datetime.now().year,
    }
