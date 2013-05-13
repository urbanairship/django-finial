# (c) 2013 Urban Airship and Contributors

from django.conf.urls.defaults import url, patterns

# a Noop "view"
override_view = lambda *args, **kwargs: None


urlpatterns = patterns('',
    url(
        r'/view1',
        'override_view',
        name='view1',
    ),
)
