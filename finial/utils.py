# (c) 2013 Urban Airship and Contributors

"""Utility methods for Finial."""

import os

from django.conf import settings


def get_tmpl_override_cache_key(user):
    """Creates cache key for storing per user override data."""
    return 'tmpl_override:user_id:{0}'.format(user.pk)


def get_override_manifest_cache_key(override):
    """Creates a cache key for storing the file manifest for an override."""
    return 'tmpl_override:override_name:{0}'.format(override)


def get_static_override_files(path):
    """Takes the path, returns dict of file to override relationships.
    :param path: string, should be the path to static overrides root.
        e.g. '/project/path/static/overrides/'
    :returns:
        {
            'override1': ['override1/dir/subdir/file.js'],
            'override2': ['override2/dir/file2.js'],
        }

    .. warning :: Don't run this often; only during deployments, or
        in local development.

    """
    overrides = {}
    for override_dir in os.listdir(path):
        for dirname, _, filenames in os.walk(os.path.join(path, override_dir)):
            for filename in filenames:
                overrides.setdefault(override_dir, []).append(
                    os.path.join(dirname, filename).replace(path, '')
                )

    return overrides


def build_url(prefix, override_name, delimiter='.'):
    """Deals with local vs. production url building.

    Should build something like:
        For production:
        'https://s3.aws.com/com.finial.media.deploy-5-override1/'
        For development:
        /overrides/override1/

    Optionally, if a special FINIAL_URL_PREFIX is set, we postpend
    to ``prefix``.

    """
    version = ''
    url_prefix = getattr(settings, 'FINIAL_URL_PREFIX', '')
    if settings.DEBUG:
        delimiter = ''
    else:
        # The assumption is that you don't care about build versions if you're
        # not in production.
        version = getattr(settings, 'FINIAL_URL_VERSION_PREFIX', '')

    return '{prefix}{url_prefix}{delimiter}{version}{override_name}/'.format(
        **{
            'prefix': prefix,
            'url_prefix': url_prefix,
            'delimiter': delimiter,
            'version': version,
            'override_name': override_name
        }
    )

