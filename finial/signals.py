# (c) 2013 Urban Airship and Contributors

import simplejson as json

from django.core.cache import cache
from django.forms.models import model_to_dict


def update_user_override_cache(sender, instance, *args, **kwargs):
    """If an override is updated: make the cache reflect that post-save."""
    from finial import models as finial_models
    from finial.middleware import TemplateOverrideMiddleware as mw
    overrides = finial_models.UserTemplateOverride.objects.filter(
        user=instance.user
    ).order_by('priority')
    override_values = [model_to_dict(override) for override in overrides]
    if override_values:
        cache.set(
            mw.get_tmpl_override_cache_key(instance.user),
            json.dumps(override_values),
            600
        )
    else:
        cache.set(
            mw.get_tmpl_override_cache_key(instance.user),
            '[]',
            600
        )
