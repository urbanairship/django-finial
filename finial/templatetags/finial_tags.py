from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True, name='get_media_url')
def get_media_url(context):
    return context.get('MEDIA_URL', settings.MEDIA_URL)
