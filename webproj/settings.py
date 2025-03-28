from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Debug ativo para desenvolvimento
DEBUG = True


# TODO: Não usar isto em production :)
SECRET_KEY = 'tartarugas-ninjas-sao-bue-tops'


ALLOWED_HOSTS = ['*']

# Roteador principal
ROOT_URLCONF = 'webproj.urls'

# Templates (já está ok)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # Para encontrar os templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Apps instaladas (já está ótimo)
INSTALLED_APPS = [
    'django.contrib.admin',           
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]

# ✅ MIDDLEWARE completo para permitir admin e sessões
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # ← obrigatório
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # ← obrigatório
    'django.contrib.messages.middleware.MessageMiddleware',  # ← obrigatório
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Para o admin funcionar
WSGI_APPLICATION = 'webproj.wsgi.application'

# ⚠️ Base de dados mínima (mesmo que não uses)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static"
]

# SPARQL endpoint para GraphDB
GRAPHDB_ENDPOINT = "http://graphdb:7200/repositories/Poked-X"

