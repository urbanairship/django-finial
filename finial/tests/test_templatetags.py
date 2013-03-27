import mimic

from django.template import Context, Template

TEMPLATE = """
{% load finial_tags %}

{% get_media_url %}
"""

class TemplateTagTest(mimic.MimicTestBase):

    def test_get_media_url(self):
        """test that our templatetag is able to override settings.MEDIA_URL."""
        override = 'overridden.ua.com'
        context = Context({'X_MEDIA_URL': override})
        template = Template(TEMPLATE)
        rendered = template.render(context)

        self.assertTrue(override in rendered)

        rendered = template.render(Context())

        self.assertFalse(override in rendered)
