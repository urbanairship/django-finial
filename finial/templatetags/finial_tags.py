from django import template
from django.conf import settings

register = template.Library()


class MediaURLNode(template.Node):

    def render(self, context):
        return context.get('X_MEDIA_URL', settings.MEDIA_URL)


class StaticURLNode(template.Node):

    def render(self, context):
        return context.get('X_STATIC_URL', settings.STATIC_URL)


def get_media_url(parser, token):
    """For older generations of Django installs (Pre 1.3)."""
    return MediaURLNode()

def get_static_url(parser, token):
    """If you're using the staticfiles app: use this.

    .. note :: we avoid conflicts with the media Template Context Processor
    by prepending 'X_' to our custom setting.

    """
    return StaticURLNode()

get_media_url = register.tag(get_media_url)
get_static_url = register.tag(get_static_url)
