"""
WSGI config for VitalPath Education project.
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vitalpath.settings')

application = get_wsgi_application()
app = application

# Auto-initialize database on Vercel serverless cold-start if required
try:
    from django.core.management import call_command
    from django.db import connection
    tables = connection.introspection.table_names()
    if 'products_product' not in tables:
        call_command('migrate', interactive=False)
        call_command('seed_demo')
except Exception as e:
    import logging
    logging.getLogger('vitalpath').warning(f"Serverless initialization note: {e}")
