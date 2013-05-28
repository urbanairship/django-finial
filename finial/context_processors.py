# (c) 2013 Urban Airship and Contributors
import json

from django.conf import settings
from django.core.cache import cache

from finial import middleware


def _build_url(prefix, override_name, delimiter='.'):
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


def asset_url(request):
    """Adjust settings' *_URL variables depending on overrides."""
    override_name = getattr(request, 'active_override_name', None)
    if not override_name:
        return {}

    overrides = getattr(request, 'finial_overrides', {})
    if not overrides or not request.user.is_authenticated():
        return {}

    media_url = _build_url(
        settings.FINIAL_MEDIA_URL_PREFIX, override_name
    )
    static_url = _build_url(
        settings.FINIAL_STATIC_URL_PREFIX, override_name
    )

    return {
        'MEDIA_URL': media_url,
        'STATIC_URL': static_url,
    }


def override_names(request):
    """Return a list of override names for javascript to discover.

    Sets the template variable 'FINIAL_POINTS' to a json list
    of the names of your overrides.

    """
    if not getattr(request, 'user') or not request.user.is_authenticated():
        return {}

    # Cache should be primed by middleware already.
    cached_values = cache.get(
        middleware.TemplateOverrideMiddleware.get_tmpl_override_cache_key(
            request.user
        )
    )

    if cached_values:
        override_dict = json.loads(cached_values)

        return { 'FINIAL_POINTS': json.dumps(
            [override['override_name'] for override in override_dict]
        )}

    return {}
