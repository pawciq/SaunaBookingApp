import os
import sys

path = '/home/pawciq/pernatura'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sauna_booking_app.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()