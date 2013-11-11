# (c) 2013 Urban Airship and Contributors

from finial.decorators import active_override

from django.conf.urls.defaults import url, patterns
from django.template.response import TemplateResponse

"""This URLConf is used only in the test_template_context_processor tests."""


# a Noop "view"
def fake_view(request, *args, **kwargs):
    return TemplateResponse(request, 'test_template.html')


# Notice below that we're decorating the view before it gets called.
# This way we don't have to worry about mettling with code necessarily;
# all of our override data can live in this little module.

urlpatterns = patterns('',
    url(
        r'/view1',
        active_override('test_or')('fake_view'),
        name='view1',
    ),
)
