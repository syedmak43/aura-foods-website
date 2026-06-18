import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-aura-foods-secret-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'shop',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
CORS_ALLOW_ALL_ORIGINS = True
ROOT_URLCONF = 'aurafoods.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'aurafoods.wsgi.application'
DATA_ROOT = Path(os.environ.get('AURAFOODS_DATA_ROOT', BASE_DIR / 'data'))
DATA_ROOT.mkdir(parents=True, exist_ok=True)
MEDIA_ROOT = Path(os.environ.get('AURAFOODS_MEDIA_ROOT', BASE_DIR / 'static' / 'uploads'))
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(DATA_ROOT / 'aurafoods.db'),
    }
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR/'static']
MEDIA_URL = '/uploads/'
MEDIA_ROOT = BASE_DIR/'static'/'uploads'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/admin/login/'
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.AllowAny']}
