# (c) 2013 Urban Airship and Contributors

from functools import wraps

def active_override(override_name):
    """Sets request.active_override_name to whatever the override."""
    def decorate(fn):
        @wraps(fn)
        def wrap(request, *args, **kwargs):
            request.active_override_name = override_name
            return fn(request, *args, **kwargs)

        return wrap
    return decorate


