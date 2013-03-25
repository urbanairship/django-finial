import simplejson as json

from django.conf import settings
from django.core.cache import cache

from finial import models

DEFAULT_TEMPLATE_DIRS = (
    settings.PROJECT_PATH + '/templates',
)

class TemplateOverrideMiddleware(object):
    """Override templates on a per-user basis; modify TEMPLATE_DIRS.

    Since we're using request.user for most of our logic, this
    Middleware must be placed sometime "after" Session and Authentication
    Middlwares.

    """
    @staticmethod
    def get_tmpl_override_cache_key(user):
        return 'tmpl_override:user_id:{0}'.format(user.pk)

    def process_request(self, request):
        """See if there are any overrides, apply them to TEMPLATE_DIRS.

        Here the assumption is that the model fields for:
            user, override_name, tempalte_dir, priority

        """
        settings.TEMPLATE_DIRS = DEFAULT_TEMPLATE_DIRS
        override_values = cache.get(self.get_tmpl_override_cache_key(request.user))
        overrides = None
        if override_values is not None:
            # If we have *something* set, even an empty list
            override_values = json.loads(override_values)
        else:
            overrides = models.UserTemplateOverride.objects.filter(
                user=request.user
            ).order_by('priority')
            override_values = [override.template_dir for override in overrides]

        if override_values:
            if overrides:
                # If we picked these up from the database; need to add defaults.
                override_values.append(DEFAULT_TEMPLATE_DIRS[0])

            settings.TEMPLATE_DIRS = tuple(override_values)
            # Cache whatever we've found in the database.
            cache.set(
                self.get_tmpl_override_cache_key(request.user),
                json.dumps(override_values),
                600
            )
        else:
            # Cache the negative presence of overrides.
            cache.set(self.get_tmpl_override_cache_key(request.user),'[]', 600)

        return None

    def process_response(self, request):
        # Maybe we don't need to do anything here?
        pass
