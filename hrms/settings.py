# # # from pathlib import Path
# # # import os
# # # import anthropic

# # # BASE_DIR = Path(__file__).resolve().parent.parent
# # # SECRET_KEY = 'django-insecure-hrms-secret-key-change-in-production-2024'
# # # DEBUG = False

# # # ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'hrms-product-production.up.railway.app']
# # # # DEBUG = True
# # # # ALLOWED_HOSTS = ['*']
# # # # ALLOWED_HOSTS = [
# # # #     "hrms-product-production.up.railway.app",
# # # #     "localhost",
# # # #     "127.0.0.1",
# # # # ]




   
# # #     # print("Username: djsuperadmin")

# # #     # print("Password: Admindj@2026")

# # # SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # # CSRF_COOKIE_SECURE = True
# # # SESSION_COOKIE_SECURE = True

# # # INSTALLED_APPS = [
# # #     'django.contrib.admin',
# # #     'django.contrib.auth',
# # #     'django.contrib.contenttypes',
# # #     'django.contrib.sessions',
# # #     'django.contrib.messages',
# # #     'django.contrib.staticfiles',
# # #     # Third party
# # #     'rest_framework',
# # #     'django_filters',
# # #     'rest_framework.authtoken',
# # #     'corsheaders',
# # #     # Local apps
# # #     'employees',
# # #     'attendance',
# # #     'leaves',
# # #     'payroll',
# # #     'recruitment',
# # #     'messaging',
# # # ]

# # # MIDDLEWARE = [
# # #     'django.middleware.security.SecurityMiddleware',
# # #     'django.contrib.sessions.middleware.SessionMiddleware',
# # #     'corsheaders.middleware.CorsMiddleware',
# # #     'django.middleware.common.CommonMiddleware',
# # #     'django.middleware.csrf.CsrfViewMiddleware',
# # #     'django.contrib.auth.middleware.AuthenticationMiddleware',
# # #     'django.contrib.messages.middleware.MessageMiddleware',
# # #     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# # # ]

# # # ROOT_URLCONF = 'hrms.urls'

# # # TEMPLATES = [
# # #     {
# # #         'BACKEND': 'django.template.backends.django.DjangoTemplates',
# # #         'DIRS': [BASE_DIR / 'templates'],
# # #         'APP_DIRS': True,
# # #         'OPTIONS': {
# # #             'context_processors': [
# # #                 'django.template.context_processors.debug',
# # #                 'django.template.context_processors.request',
# # #                 'django.contrib.auth.context_processors.auth',
# # #                 'django.contrib.messages.context_processors.messages',
# # #                 'hrms.context_processors.notifications', 
# # #             ],
# # #         },
# # #     },
# # # ]

# # # WSGI_APPLICATION = 'hrms.wsgi.application'

# # # DATABASES = {
# # #     'default': {
# # #         'ENGINE': 'django.db.backends.sqlite3',
# # #         'NAME': BASE_DIR / 'db.sqlite3',
# # #     }
# # # }

# # # AUTH_PASSWORD_VALIDATORS = [
# # #     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
# # #     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
# # #     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
# # #     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# # # ]

# # # LANGUAGE_CODE = 'en-us'
# # # TIME_ZONE = 'Asia/Kolkata'
# # # USE_I18N = True
# # # USE_TZ = True

# # # STATIC_URL = '/static/'
# # # STATICFILES_DIRS = [BASE_DIR / 'static']
# # # STATIC_ROOT = BASE_DIR / 'staticfiles'

# # # MEDIA_URL = '/media/'
# # # MEDIA_ROOT = BASE_DIR / 'media'

# # # DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # # # LOGIN_URL = '/auth/login/'
# # # # LOGIN_REDIRECT_URL = '/dashboard/'
# # # # LOGOUT_REDIRECT_URL = '/auth/login/'

# # # # HR Admin
# # # # LOGIN_URL          = '/admin-login/'
# # # # LOGIN_REDIRECT_URL = '/dashboard/'
# # # # LOGOUT_REDIRECT_URL = '/admin-login/'


# # # LOGIN_URL = '/employee-login/'
# # # LOGIN_REDIRECT_URL = '/portal/'
# # # LOGOUT_REDIRECT_URL = '/employee-login/'



# # # # Employee portal redirect alag handle hoga views mein

# # # # REST Framework
# # # REST_FRAMEWORK = {
# # #     'DEFAULT_AUTHENTICATION_CLASSES': [
# # #         'rest_framework.authentication.TokenAuthentication',
# # #         'rest_framework.authentication.SessionAuthentication',
# # #     ],
# # #     'DEFAULT_PERMISSION_CLASSES': [
# # #         'rest_framework.permissions.IsAuthenticated',
# # #     ],
# # #     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
# # #     'PAGE_SIZE': 20,
# # # }

# # # # CORS
# # # CORS_ALLOWED_ORIGINS = [
# # #     "http://localhost:3000",
# # #     "http://127.0.0.1:3000",
# # # ]
# # # CORS_ALLOW_CREDENTIALS = True


# # # CSRF_TRUSTED_ORIGINS = [
# # #     "https://hrms-product-production.up.railway.app",
# # # ]


# # from pathlib import Path
# # import os
# # import anthropic

# # BASE_DIR = Path(__file__).resolve().parent.parent
# # SECRET_KEY = 'django-insecure-hrms-secret-key-change-in-production-2024'
# # DEBUG = False

# # ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'hrms-product-production.up.railway.app']
# # # DEBUG = True
# # # ALLOWED_HOSTS = ['*']
# # # ALLOWED_HOSTS = [
# # #     "hrms-product-production.up.railway.app",
# # #     "localhost",
# # #     "127.0.0.1",
# # # ]




   
# #     # print("Username: djsuperadmin")

# #     # print("Password: Admindj@2026")

# # SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # CSRF_COOKIE_SECURE = True
# # SESSION_COOKIE_SECURE = True

# # INSTALLED_APPS = [
# #     'django.contrib.admin',
# #     'django.contrib.auth',
# #     'django.contrib.contenttypes',
# #     'django.contrib.sessions',
# #     'django.contrib.messages',
# #     'django.contrib.staticfiles',
# #     # Third party
# #     'rest_framework',
# #     'django_filters',
# #     'rest_framework.authtoken',
# #     'corsheaders',
# #     # Local apps
# #     'employees',
# #     'attendance',
# #     'leaves',
# #     'payroll',
# #     'recruitment',
# #     'messaging',
# # ]

# # MIDDLEWARE = [
# #     'django.middleware.security.SecurityMiddleware',
# #     'django.contrib.sessions.middleware.SessionMiddleware',
# #     'corsheaders.middleware.CorsMiddleware',
# #     'django.middleware.common.CommonMiddleware',
# #     'django.middleware.csrf.CsrfViewMiddleware',
# #     'django.contrib.auth.middleware.AuthenticationMiddleware',
# #     'django.contrib.messages.middleware.MessageMiddleware',
# #     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# # ]

# # ROOT_URLCONF = 'hrms.urls'

# # TEMPLATES = [
# #     {
# #         'BACKEND': 'django.template.backends.django.DjangoTemplates',
# #         'DIRS': [BASE_DIR / 'templates'],
# #         'APP_DIRS': True,
# #         'OPTIONS': {
# #             'context_processors': [
# #                 'django.template.context_processors.debug',
# #                 'django.template.context_processors.request',
# #                 'django.contrib.auth.context_processors.auth',
# #                 'django.contrib.messages.context_processors.messages',
# #                 'hrms.context_processors.notifications',
# #                 'hrms.context_processors.unread_messages',
# #             ],
# #         },
# #     },
# # ]

# # WSGI_APPLICATION = 'hrms.wsgi.application'

# # DATABASES = {
# #     'default': {
# #         'ENGINE': 'django.db.backends.sqlite3',
# #         'NAME': BASE_DIR / 'db.sqlite3',
# #     }
# # }

# # AUTH_PASSWORD_VALIDATORS = [
# #     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
# #     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
# #     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
# #     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# # ]

# # LANGUAGE_CODE = 'en-us'
# # TIME_ZONE = 'Asia/Kolkata'
# # USE_I18N = True
# # USE_TZ = True

# # STATIC_URL = '/static/'
# # STATICFILES_DIRS = [BASE_DIR / 'static']
# # STATIC_ROOT = BASE_DIR / 'staticfiles'

# # MEDIA_URL = '/media/'
# # MEDIA_ROOT = BASE_DIR / 'media'

# # DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # # LOGIN_URL = '/auth/login/'
# # # LOGIN_REDIRECT_URL = '/dashboard/'
# # # LOGOUT_REDIRECT_URL = '/auth/login/'

# # # HR Admin
# # # LOGIN_URL          = '/admin-login/'
# # # LOGIN_REDIRECT_URL = '/dashboard/'
# # # LOGOUT_REDIRECT_URL = '/admin-login/'


# # LOGIN_URL = '/employee-login/'
# # LOGIN_REDIRECT_URL = '/portal/'
# # LOGOUT_REDIRECT_URL = '/employee-login/'

# # DEBUG = True

# # # Employee portal redirect alag handle hoga views mein

# # # REST Framework
# # REST_FRAMEWORK = {
# #     'DEFAULT_AUTHENTICATION_CLASSES': [
# #         'rest_framework.authentication.TokenAuthentication',
# #         'rest_framework.authentication.SessionAuthentication',
# #     ],
# #     'DEFAULT_PERMISSION_CLASSES': [
# #         'rest_framework.permissions.IsAuthenticated',
# #     ],
# #     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
# #     'PAGE_SIZE': 20,
# # }

# # # CORS
# # CORS_ALLOWED_ORIGINS = [
# #     "http://localhost:3000",
# #     "http://127.0.0.1:3000",
# # ]
# # CORS_ALLOW_CREDENTIALS = True


# # CSRF_TRUSTED_ORIGINS = [
# #     "https://hrms-product-production.up.railway.app",
# # ]

# from pathlib import Path
# import os
# import anthropic

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
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# # from pathlib import Path
# # import os
# # import anthropic

# # BASE_DIR = Path(__file__).resolve().parent.parent
# # SECRET_KEY = 'django-insecure-hrms-secret-key-change-in-production-2024'
# # DEBUG = False

# # ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'hrms-product-production.up.railway.app']
# # # DEBUG = True
# # # ALLOWED_HOSTS = ['*']
# # # ALLOWED_HOSTS = [
# # #     "hrms-product-production.up.railway.app",
# # #     "localhost",
# # #     "127.0.0.1",
# # # ]




   
# #     # print("Username: djsuperadmin")

# #     # print("Password: Admindj@2026")

# # SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# # CSRF_COOKIE_SECURE = True
# # SESSION_COOKIE_SECURE = True

# # INSTALLED_APPS = [
# #     'django.contrib.admin',
# #     'django.contrib.auth',
# #     'django.contrib.contenttypes',
# #     'django.contrib.sessions',
# #     'django.contrib.messages',
# #     'django.contrib.staticfiles',
# #     # Third party
# #     'rest_framework',
# #     'django_filters',
# #     'rest_framework.authtoken',
# #     'corsheaders',
# #     # Local apps
# #     'employees',
# #     'attendance',
# #     'leaves',
# #     'payroll',
# #     'recruitment',
# #     'messaging',
# # ]

# # MIDDLEWARE = [
# #     'django.middleware.security.SecurityMiddleware',
# #     'django.contrib.sessions.middleware.SessionMiddleware',
# #     'corsheaders.middleware.CorsMiddleware',
# #     'django.middleware.common.CommonMiddleware',
# #     'django.middleware.csrf.CsrfViewMiddleware',
# #     'django.contrib.auth.middleware.AuthenticationMiddleware',
# #     'django.contrib.messages.middleware.MessageMiddleware',
# #     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# # ]

# # ROOT_URLCONF = 'hrms.urls'

# # TEMPLATES = [
# #     {
# #         'BACKEND': 'django.template.backends.django.DjangoTemplates',
# #         'DIRS': [BASE_DIR / 'templates'],
# #         'APP_DIRS': True,
# #         'OPTIONS': {
# #             'context_processors': [
# #                 'django.template.context_processors.debug',
# #                 'django.template.context_processors.request',
# #                 'django.contrib.auth.context_processors.auth',
# #                 'django.contrib.messages.context_processors.messages',
# #                 'hrms.context_processors.notifications', 
# #             ],
# #         },
# #     },
# # ]

# # WSGI_APPLICATION = 'hrms.wsgi.application'

# # DATABASES = {
# #     'default': {
# #         'ENGINE': 'django.db.backends.sqlite3',
# #         'NAME': BASE_DIR / 'db.sqlite3',
# #     }
# # }

# # AUTH_PASSWORD_VALIDATORS = [
# #     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
# #     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
# #     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
# #     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
# # ]

# # LANGUAGE_CODE = 'en-us'
# # TIME_ZONE = 'Asia/Kolkata'
# # USE_I18N = True
# # USE_TZ = True

# # STATIC_URL = '/static/'
# # STATICFILES_DIRS = [BASE_DIR / 'static']
# # STATIC_ROOT = BASE_DIR / 'staticfiles'

# # MEDIA_URL = '/media/'
# # MEDIA_ROOT = BASE_DIR / 'media'

# # DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # # LOGIN_URL = '/auth/login/'
# # # LOGIN_REDIRECT_URL = '/dashboard/'
# # # LOGOUT_REDIRECT_URL = '/auth/login/'

# # # HR Admin
# # # LOGIN_URL          = '/admin-login/'
# # # LOGIN_REDIRECT_URL = '/dashboard/'
# # # LOGOUT_REDIRECT_URL = '/admin-login/'


# # LOGIN_URL = '/employee-login/'
# # LOGIN_REDIRECT_URL = '/portal/'
# # LOGOUT_REDIRECT_URL = '/employee-login/'



# # # Employee portal redirect alag handle hoga views mein

# # # REST Framework
# # REST_FRAMEWORK = {
# #     'DEFAULT_AUTHENTICATION_CLASSES': [
# #         'rest_framework.authentication.TokenAuthentication',
# #         'rest_framework.authentication.SessionAuthentication',
# #     ],
# #     'DEFAULT_PERMISSION_CLASSES': [
# #         'rest_framework.permissions.IsAuthenticated',
# #     ],
# #     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
# #     'PAGE_SIZE': 20,
# # }

# # # CORS
# # CORS_ALLOWED_ORIGINS = [
# #     "http://localhost:3000",
# #     "http://127.0.0.1:3000",
# # ]
# # CORS_ALLOW_CREDENTIALS = True


# # CSRF_TRUSTED_ORIGINS = [
# #     "https://hrms-product-production.up.railway.app",
# # ]


# from pathlib import Path
# import os
# import anthropic

# BASE_DIR = Path(__file__).resolve().parent.parent
# SECRET_KEY = 'django-insecure-hrms-secret-key-change-in-production-2024'
# DEBUG = False

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'hrms-product-production.up.railway.app']
# # DEBUG = True
# # ALLOWED_HOSTS = ['*']
# # ALLOWED_HOSTS = [
# #     "hrms-product-production.up.railway.app",
# #     "localhost",
# #     "127.0.0.1",
# # ]




   
#     # print("Username: djsuperadmin")

#     # print("Password: Admindj@2026")

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

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
# ]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # LOGIN_URL = '/auth/login/'
# # LOGIN_REDIRECT_URL = '/dashboard/'
# # LOGOUT_REDIRECT_URL = '/auth/login/'

# # HR Admin
# # LOGIN_URL          = '/admin-login/'
# # LOGIN_REDIRECT_URL = '/dashboard/'
# # LOGOUT_REDIRECT_URL = '/admin-login/'


# LOGIN_URL = '/employee-login/'
# LOGIN_REDIRECT_URL = '/portal/'
# LOGOUT_REDIRECT_URL = '/employee-login/'

# DEBUG = True

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

from pathlib import Path
import os
import anthropic

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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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