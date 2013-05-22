# (c) 2013 Urban Airship and Contributors

import simplejson as json

from django.conf import settings
from django.core.cache import cache
from django.forms.models import model_to_dict

from finial import models
from finial import util

# Cache the original values from settings here for resetting per
# request.
DEFAULT_TEMPLATE_DIRS = settings.TEMPLATE_DIRS
DEFAULT_STATICFILES_DIRS = settings.STATICFILES_DIRS


class TemplateOverrideMiddleware(object):
    """Override templates on a per-user basis; modify TEMPLATE_DIRS.

    Since we're using request.user for most of our logic, this
    Middleware must be placed sometime "after" Session and Authentication
    Middlwares.

    """
    def override_urlconf(self, request, overrides):
        """If there are overrides, we make a custom urlconf.

        :param request: a django HttpRequest instance.
        :param overrides: a list of dicts, representing override models.
        :return: urlconf instance, new urlconf with overrides first.

        .. note:: this function also modifies request.urlconf!

        """
        url_overrides = getattr(settings, 'FINIAL_URL_OVERRIDES', None)
        if url_overrides:
            for override in overrides:
                if override['override_name'] in url_overrides:
                    # return the override url_conf with the
                    # highest priority for this user.
                    request.urlconf =  url_overrides[override['override_name']]
                    return request.urlconf

    def override_settings_dirs(self, overrides):
        """Give overrides priority in settings.TEMPLATE_DIRS."""
        # Assumes PROJECT_PATH refers to the root of the django project.
        prefix = getattr(settings, 'PROJECT_PATH', '')
        override_prefix = getattr(settings, 'FINIAL_TEMPLATE_DIR_PREFIX', '')
        if prefix and override_prefix:
            prefix = '{0}/{1}'.format(prefix, override_prefix)

        for override_type in ('template', 'staticfiles'):
            override_dirs= [
                '{0}_{1}'.format(
                    prefix + override['override_dir'],
                    override_type
                ) for override in overrides
            ]
            override_dirs.extend(getattr(
                settings,
                '{0}_DIRS'.format(override_type.upper()),
                []
            ))

            if not override_dirs:
                continue

            # Set {TEMPLATE_DIRS, STATIC_DIRS} with override values.
            setattr(
                settings,
                '{0}_DIRS'.format(override_type.upper()),
                tuple(override_dirs)
            )

    def process_request(self, request):
        """See if there are any overrides, apply them to TEMPLATE_DIRS.

        :param request: a django HttpRequest instance.

        Here the assumption is that the model fields for:
            user, override_name, tempalte_dir, priority

        """
        settings.TEMPLATE_DIRS = DEFAULT_TEMPLATE_DIRS
        settings.STATICFILES_DIRS = DEFAULT_STATICFILES_DIRS
        # We check for authentication after we reset settings.TEMPLATE_DIRS
        # This we we don't get any contamination
        if not request.user.is_authenticated():
            # We can only reason about authenticated user sessions.
            return None

        override_values = cache.get(util.get_tmpl_override_cache_key(request.user))
        overrides = None
        if override_values is not None:
            # If we have *something* set, even an empty list
            override_values = json.loads(override_values)
        else:
            # Fetch from SQL
            overrides = models.UserTemplateOverride.objects.filter(
                user=request.user
            ).order_by('priority')
            override_values = [model_to_dict(override) for override in overrides]

        if override_values:
            # Reset URLConf for specific views
            self.override_urlconf(request, override_values)
            self.override_settings_dirs(override_values)
            # staple the override_values dictionary to the request
            request.finial_overrides = override_values

            # Cache whatever we've found in the database.
            cache.set(
                util.get_tmpl_override_cache_key(request.user),
                json.dumps(override_values),
                600
            )
        else:
            # Cache the negative presence of overrides.
            cache.set(util.get_tmpl_override_cache_key(request.user),'[]', 600)

        return None
