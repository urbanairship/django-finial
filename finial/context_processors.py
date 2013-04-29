from django.conf import settings


def _build_url(prefix, override_name, delimiter='.'):
    """Deals with local vs. production url building."""
    version_num = ''
    if settings.DEBUG:
        delimiter = ''
    else:
        # The assumption is that you don't care about build versions if you're
        # not in production.
        version_num = getattr(settings, 'FINIAL_URL_VERSION_PREFIX', '')
        override_name = override_name.replace('_', '-')

    return '{0}{1}{2}{3}/'.format(
        prefix, delimiter, version_num, override_name
    )


def asset_url(request):
    """Adjust settings' *_URL variables depending on overrides."""
    override_name = getattr(request, 'active_override_name', None)
    if not override_name:
        return {}

    overrides = getattr(request, 'finial_overrides', {})
    if not overrides:
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
