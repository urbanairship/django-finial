from django import template
from finial.util import user_has_override

register = template.Library()

@register.filter
def has_finial_flag(user, flag):
    return user_has_override(user, flag)
