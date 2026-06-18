import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aurafoods.settings')

import django
from django.core.wsgi import get_wsgi_application

django.setup()
application = get_wsgi_application()
