# from pathlib import Path
# import os
# import anthropic
# from dotenv import load_dotenv

# BASE_DIR = Path(__file__).resolve().parent.parent

# load_dotenv(BASE_DIR / '.env')

# ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
# print("DEBUG LOADED KEY:", repr(ANTHROPIC_API_KEY))  # temporary debug line

from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-hrms-secret-key-change-in-production-2024'
DEBUG = True   # ⚠️ Local/multi-device testing ke liye True rakho. Production (Railway) pe deploy karte waqt False kar dena.

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'hrms-product-production.up.railway.app']

if DEBUG:
    # Let phones/tablets on the same WiFi reach the dev server via its LAN IP
    # (e.g. http://192.168.1.5:8000) so cross-device testing works.
    ALLOWED_HOSTS += ['*']

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ⚠️ Secure cookies only work over HTTPS. If these are True while testing
# locally over plain HTTP (e.g. from a phone on the same WiFi hitting your
# machine's LAN IP like http://192.168.x.x:8000), the browser will refuse
# to store/send the session & CSRF cookies — every POST request (sending a
# chat message, approving leave, etc.) then silently fails. In production
# behind HTTPS, this should be True.
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'corsheaders',
    # Local apps
    'employees',
    'attendance',
    'leaves',
    'payroll',
    'recruitment',
    'messaging',
    'events', 
    'wellness',
    'helpcenter', 
    'tenants', 
    'expenses',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'employees.middleware.UpdateLastSeenMiddleware',
]

ROOT_URLCONF = 'hrms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'hrms.context_processors.notifications',
                'hrms.context_processors.unread_messages',
                'hrms.context_processors.team_requests',
                'hrms.context_processors.current_employee',
                'hrms.context_processors.site_settings',
                'hrms.context_processors.team_notifications', 
            ],
        },
    },
]

WSGI_APPLICATION = 'hrms.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise serves static files directly from the WSGI app (needed because
# gunicorn on Railway doesn't auto-serve static files the way `runserver` does).
# WHITENOISE_USE_FINDERS = True lets it serve straight from STATICFILES_DIRS
# in dev too, so you don't need to run collectstatic locally — same code path
# works on your machine and on Railway.
WHITENOISE_USE_FINDERS = DEBUG
WHITENOISE_AUTOREFRESH = DEBUG

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG else
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/employee-login/'
LOGIN_REDIRECT_URL = '/portal/'
LOGOUT_REDIRECT_URL = '/employee-login/'

# Employee portal redirect alag handle hoga views mein

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = [
    "https://hrms-product-production.up.railway.app",
]



# ── Email (used for Birthday wishes, and future notification emails) ───────────
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'HRMS <noreply@company.com>')


# # from pathlib import Path
# # import os
# # import anthropic
# # from dotenv import load_dotenv

# # BASE_DIR = Path(__file__).resolve().parent.parent

# # load_dotenv(BASE_DIR / '.env')

# # ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
# # print("DEBUG LOADED KEY:", repr(ANTHROPIC_API_KEY))  # temporary debug line

# from pathlib import Path
# import os
# from dotenv import load_dotenv

# BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(BASE_DIR / '.env')

# GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# BASE_DIR = Path(__file__).resolve().parent.parent
# SECRET_KEY = 'django-insecure-hrms-secret-key-change-in-production-2024'
# DEBUG = True   # ⚠️ Local/multi-device testing ke liye True rakho. Production (Railway) pe deploy karte waqt False kar dena.

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'hrms-product-production.up.railway.app']

# if DEBUG:
#     # Let phones/tablets on the same WiFi reach the dev server via its LAN IP
#     # (e.g. http://192.168.1.5:8000) so cross-device testing works.
#     ALLOWED_HOSTS += ['*']

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # ⚠️ Secure cookies only work over HTTPS. If these are True while testing
# # locally over plain HTTP (e.g. from a phone on the same WiFi hitting your
# # machine's LAN IP like http://192.168.x.x:8000), the browser will refuse
# # to store/send the session & CSRF cookies — every POST request (sending a
# # chat message, approving leave, etc.) then silently fails. In production
# # behind HTTPS, this should be True.
# CSRF_COOKIE_SECURE = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG

# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     # Third party
#     'rest_framework',
#     'django_filters',
#     'rest_framework.authtoken',
#     'corsheaders',
#     # Local apps
#     'employees',
#     'attendance',
#     'leaves',
#     'payroll',
#     'recruitment',
#     'messaging',
#     'events', 
#     'wellness',
#     'helpcenter', 
#     'tenants', 
#     'expenses',
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'employees.middleware.UpdateLastSeenMiddleware',
# ]

# ROOT_URLCONF = 'hrms.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [BASE_DIR / 'templates'],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#                 'hrms.context_processors.notifications',
#                 'hrms.context_processors.unread_messages',
#                 'hrms.context_processors.team_requests',
#                 'hrms.context_processors.current_employee',
#                 'hrms.context_processors.site_settings',
#                 'hrms.context_processors.team_notifications', 
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'hrms.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# ]

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'Asia/Kolkata'
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = '/static/'
# STATICFILES_DIRS = [BASE_DIR / 'static']
# STATIC_ROOT = BASE_DIR / 'staticfiles'

# # WhiteNoise serves static files directly from the WSGI app (needed because
# # gunicorn on Railway doesn't auto-serve static files the way `runserver` does).
# # WHITENOISE_USE_FINDERS = True lets it serve straight from STATICFILES_DIRS
# # in dev too, so you don't need to run collectstatic locally — same code path
# # works on your machine and on Railway.
# WHITENOISE_USE_FINDERS = DEBUG
# WHITENOISE_AUTOREFRESH = DEBUG

# STORAGES = {
#     "default": {
#         "BACKEND": "django.core.files.storage.FileSystemStorage",
#     },
#     "staticfiles": {
#         "BACKEND": (
#             "django.contrib.staticfiles.storage.StaticFilesStorage"
#             if DEBUG else
#             "whitenoise.storage.CompressedManifestStaticFilesStorage"
#         ),
#     },
# }

# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# LOGIN_URL = '/employee-login/'
# LOGIN_REDIRECT_URL = '/portal/'
# LOGOUT_REDIRECT_URL = '/employee-login/'

# # Employee portal redirect alag handle hoga views mein

# # REST Framework
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.TokenAuthentication',
#         'rest_framework.authentication.SessionAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 20,
# }

# # CORS
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]
# CORS_ALLOW_CREDENTIALS = True


# CSRF_TRUSTED_ORIGINS = [
#     "https://hrms-product-production.up.railway.app",
# ]



# # ── Email (used for Birthday wishes, and future notification emails) ───────────
# EMAIL_BACKEND = os.environ.get(
#     'EMAIL_BACKEND',
#     'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
# )
# EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'HRMS <noreply@company.com>')