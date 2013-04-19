""" This is an example local_settings.py file meant for local development."""


PROJECT_PATH = '/path/to/django/root/'
STATIC_URL = '/static'
STATICFILES_DIRS = (
    PROJECT_PATH + '/static',
)

DEBUG = True

FINIAL_LOCAL_DIR_PREFIX = '/overrides' # This is the directory prefix from your PROJECT_PATH
FINIAL_MEDIA_URL_PREFIX = FINIAL_STATIC_URL_PREFIX = 'https://s3.amazonaws.com/com.finial.media'

if DEBUG:
    FINIAL_MEDIA_URL_PREFIX = FINIAL_STATIC_URL_PREFIX = STATIC_URL
    # Need to adjust url path to match dir path for local dev.
    STATICFILES_FINDERS = (
        'finial.finders.FinialFileSystemFinder',
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )


# Here is where we map override names to URLconf module paths:
FINIAL_URL_OVERRIDES = {
    'test_or': 'airship.finial_override_patterns'
}
