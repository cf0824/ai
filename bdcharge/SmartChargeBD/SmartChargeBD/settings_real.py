from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'smart_charge',
        'USER': 'root',
        'PASSWORD': 'Smartcharge_2021',
        'HOST': '127.0.0.1',
        'PORT': '23307',
        'OPTIONS': {
            'init_command': 'SET default_storage_engine=INNODB,character_set_connection=utf8mb4,collation_connection=utf8_unicode_ci;'}
    }
}