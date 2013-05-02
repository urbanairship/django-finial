# (c) 2013 Urban Airship and Contributors

""" This is an example local_settings.py file meant for local development."""


PROJECT_PATH = '/path/to/django/root/'
STATIC_URL = '/static'
STATICFILES_DIRS = (
    PROJECT_PATH + '/static',
)

DEBUG = True

FINIAL_TEMPLATE_DIR_PREFIX = '/overrides' # This is the directory prefix from your PROJECT_PATH
FINIAL_MEDIA_URL_PREFIX = FINIAL_STATIC_URL_PREFIX = 'https://s3.amazonaws.com/com.finial.media'
# This will get tacked on in the case that your static media are pegged
# to a deployment version. It gets inserted directly before the
# override_name. The complete url will look something like this:
# https://s3.amazonaws.com/com.finial.media.deploy5-test-or/
FINIAL_URL_VERSION_PREFIX = 'deploy5-'

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
    'test_or': 'my_project.finial_override_patterns'
}
