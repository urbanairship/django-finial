from django.conf.urls.defaults import url, patterns

# a Noop "view"
override_view = lambda *args, **kwargs: None

override_urlpatterns = {
    'override': patterns('',
            url(r'/view1', 'override_view', name='view1'),
        ),
}
