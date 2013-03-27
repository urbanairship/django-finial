from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True, name='get_media_url')
def get_media_url(context):
    """For older generations of Django installs (Pre 1.3).

    Note: we avoid conflicts with the media Template Context Processor
    by prepending 'X_' to our custom setting.

    """
    return context.get('X_MEDIA_URL', settings.MEDIA_URL)


@register.simple_tag(takes_context=True, name='get_static_url')
def get_static_url(context):
    """If you're using staticfiles app use this."""
    return context.get('X_STATIC_URL', settings.STATIC_URL)
