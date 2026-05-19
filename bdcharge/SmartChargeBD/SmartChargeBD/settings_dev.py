from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smart_charge',
        'USER': 'root',
        'PASSWORD': 'Pinma_2023',
        'HOST': '119.27.169.45',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET default_storage_engine=INNODB,character_set_connection=utf8mb4,collation_connection=utf8_unicode_ci;'}
    }
}

ALLOWED_HOSTS = ['*']