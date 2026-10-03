"""
ASGI config for VitalPath Education project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vitalpath.settings')

application = get_asgi_application()
