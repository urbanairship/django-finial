# (c) 2012 Urban Airship and Contributors

DATABASES = {'default':{
    'NAME':'project.db',
    'ENGINE':'django.db.backends.sqlite3'
}}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

# install the bare minimum for
# testing mithril
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'south',
    'finial',
)

# point to ourselves as the root urlconf, define no patterns (see below)
ROOT_URLCONF = 'test_settings'

# set this to turn off an annoying "you're doing it wrong" message
SECRET_KEY = 'finials are distinctive'

PROJECT_PATH = '.'

# turn this file into a pseudo-urls.py.
from django.conf.urls import *

urlpatterns = patterns('')
