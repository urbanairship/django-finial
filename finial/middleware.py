import simplejson as json

from django.conf import settings
from django.conf.urls.defaults import include, patterns, url
from django.core.cache import cache
from django.forms.models import model_to_dict

from finial import models

DEFAULT_TEMPLATE_DIRS = (
    settings.PROJECT_PATH + '/templates',
)
DEFAULT_STATIC_DIRS = (
    settings.PROJECT_PATH + '/static',
)


def get_module_by_path(path):
    mod = __import__(path)
    for sub in path.split('.')[1:]:
        mod = getattr(mod, sub)
    return mod


class TemplateOverrideMiddleware(object):
    """Override templates on a per-user basis; modify TEMPLATE_DIRS.

    Since we're using request.user for most of our logic, this
    Middleware must be placed sometime "after" Session and Authentication
    Middlwares.

    """
    @staticmethod
    def get_tmpl_override_cache_key(user):
        return 'tmpl_override:user_id:{0}'.format(user.pk)

    def override_urlconf(self, request, overrides):
        """If there are overrides, we make a custom urlconf.

        :param request: a django HttpRequest instance.
        :param overrides: a list of dicts, representing override models.
        :return: urlconf instance, new urlconf with overrides first.

        .. note:: this function also modifies request.urlconf!

        """
        url_override_cls = getattr(settings, 'FINIAL_URL_OVERRIDES', None)
        if not url_override_cls:
            return

        url_override_inst = get_module_by_path(url_override_cls)
        args = []
        # These should be in priority order, higher priority at the top.
        for override in overrides:
            url_pattern = url_override_inst.override_urlpatterns.get(
                override['override_name']
            )
            if not url_pattern:
                continue

            args.append(url(
                r'^', include(url_pattern, namespace=override['override_name'])
            ))

        # At the very end, we should include the original ROOT_URLCONF
        args.append(url(r'^', include(getattr(
            get_module_by_path(settings.ROOT_URLCONF), 'urlpatterns'
        ))))

        request.urlconf = patterns('', *args)

        return request.urlconf

    def override_settings_dirs(self, overrides):
        """Give overrides priority in settings.TEMPLATE_DIRS."""
        for override_type in ('template', 'staticfiles'):
            override_dirs= [
                '{0}_{1}'.format(
                    override['override_dir'],
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

            if override_type == 'staticfiles':
                # Because staticfiles uses the 'last' instance found,
                # *not* the first as templates do.
                override_dirs.reverse()

            # Set {TEMPLATE_DIRS, STATIC_DIRS} with override values.
            setattr(
                settings,
                '{0}_DIRS'.format(override_type.upper()),
                tuple(override_dirs)
            )

    def process_request(self, request, response):
        """See if there are any overrides, apply them to TEMPLATE_DIRS.

        :param request: a django HttpRequest instance.

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
            # Fetch from SQL
            overrides = models.UserTemplateOverride.objects.filter(
                user=request.user
            ).order_by('priority')
            override_values = [model_to_dict(override) for override in overrides]

        if override_values:
            # Reset URLConf for specific views
            self.override_urlconf(request, override_values)
            self.override_settings_dirs(override_values)

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
