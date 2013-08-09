# (c) 2013 Urban Airship and Contributors
from functools import wraps

from finial.util import user_has_override

from django.http import HttpResponseNotFound


def require_finial_override(override_name, alternate=HttpResponseNotFound):
    def decorate(fn):
        @wraps(fn)
        def wrap(request, *args, **kwargs):
            if not user_has_override(request.user, override_name):
                if isinstance(alternate, type):
                    response = alternate()
                else:
                    response = alternate
                return response
            return fn(request, *args, **kwargs)
        return wrap
    return decorate


def active_override(override_name):
    """Sets request.active_override_name to whatever the override."""
    def decorate(fn):
        @wraps(fn)
        def wrap(request, *args, **kwargs):
            request.active_override_name = override_name
            return fn(request, *args, **kwargs)

        return wrap
    return decorate


