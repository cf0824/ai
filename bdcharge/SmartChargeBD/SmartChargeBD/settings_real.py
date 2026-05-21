from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'charge_db'),
        'USER': os.environ.get('MYSQL_USER', 'root'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
        'HOST': os.environ.get('MYSQL_HOST', 'mysql'),
        'PORT': '23307',
        'OPTIONS': { 'init_command': 'SET default_storage_engine=INNODB,character_set_connection=utf8mb4,collation_connection=utf8_unicode_ci;' }
    }
}