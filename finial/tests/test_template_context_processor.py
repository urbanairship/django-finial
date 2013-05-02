# (c) 2013 Urban Airship and Contributors

import mimic

from finial import context_processors
from finial.decorators import active_override
from finial.tests import utils

def fake_view(request, *args, **kwargs):
    return 'Fake view ran! Override: {0}'.format(
        getattr(request, 'active_override_name', '')
    )

class TemplateContextProcessorTest(mimic.MimicTestBase):

    def test_active_override_decorator(self):
        """Test that the active_override decorator works as expected."""
        request = utils.FakeRequest()

        # This aims to call the decorator in the same fashion as you
        # might in the URL conf, not the
        # ``@active_override('testing_override') method.
        view_output = active_override('testing_override')(fake_view)(request)
        self.assertTrue('testing_override' in view_output)

    def test_correct_override_name(self):
        # need to pass this to the asset_url_parser context_processor
        fake_settings = utils.fake_settings(
            MEDIA_URL='not_overridden.url',
            STATIC_URL='not_overriden.url',
            FINIAL_MEDIA_URL_PREFIX='com.finial.media',
            FINIAL_STATIC_URL_PREFIX='com.finial.media',
            FINIAL_URL_OVERRIDES={
                'test_or':'finial.tests.finial_context_test_overrides'
            },
            DEBUG=False
        )

        context_processors.settings = fake_settings

        request = utils.FakeRequest()
        request.active_override_name = 'testing_override'
        request.finial_overrides = [{
            'pk': 1,
            'override_name': 'test_or',
            'override_dir': 'test_or/',
            'priority': 1,
        }]
        expected_output = {
            'STATIC_URL': 'com.finial.media.testing_override/',
            'MEDIA_URL': 'com.finial.media.testing_override/'
        }
        test_output = context_processors.asset_url(request)

        self.assertEqual(expected_output, test_output)
