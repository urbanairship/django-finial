# (c) 2013 Urban Airship and Contributors

from django.conf import settings

from finial import util


def asset_url(request):
    """Adjust settings' *_URL variables depending on overrides."""
    override_name = getattr(request, 'active_override_name', None)
    if not override_name:
        return {}

    overrides = getattr(request, 'finial_overrides', {})
    if not overrides:
        return {}

    media_url = util.build_url(
        settings.FINIAL_MEDIA_URL_PREFIX, override_name
    )
    static_url = util.build_url(
        settings.FINIAL_STATIC_URL_PREFIX, override_name
    )

    return {
        'MEDIA_URL': media_url,
        'STATIC_URL': static_url,
    }
