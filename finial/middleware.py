import simplejson as json

from django.conf import settings
from django.core.cache import cache

from finial import models

DEFAULT_TEMPLATE_DIRS = (
    settings.PROJECT_PATH + '/templates',
)

class TemplateOverrideMiddlware(object):
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

        TODO: move the caching logic into the model class.

        """
        override_pks = cache.get(self.get_tmpl_override_cache_key(request.user))
        if override_pks is not None:
            # If we have *something* set, even an empty list
            override_pks = json.loads(override_pks)
            if len(override_pks) is not 0:
                # If the thing we have set is *not* and empty list
                # i.e. we have some override_pks cached.
                overrides = models.UserTemplateOverride.objects.filter(
                    pk__in=override_pks
                ).order_by('priority')

                template_dirs = [override.template_dir for override in overrides]
                template_dirs.append(DEFAULT_TEMPLATE_DIRS[0])
                settings.TEMPLATE_DIRS = tuple(template_dirs)
        else:
            settings.TEMPLATE_DIRS = DEFAULT_TEMPLATE_DIRS

        return None

    def process_response(self, request):
        # Maybe we don't need to do anything here?
        pass
