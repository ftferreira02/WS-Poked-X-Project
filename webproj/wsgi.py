# Um ponto de entrada para webservers compatíveis com WSGI.
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webproj.settings')

application = get_wsgi_application()
