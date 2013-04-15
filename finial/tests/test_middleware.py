import mimic
import json

from django.core.cache import cache

from finial.tests import utils
from finial import middleware
from finial import models


def mock_model_to_dict(model):
    return {
        'pk': model.pk,
        'override_name': model.override_name,
        'override_dir': model.override_dir,
        'priority': model.priority
    }


class MiddlewareTest(mimic.MimicTestBase):

    def setUp(self):
        super(MiddlewareTest, self).setUp()
        self.override_template_dirs = ('./templates',)
        self.override_static_dirs= ('./static',)
        self.settings = utils.fake_settings(
            TEMPLATE_DIRS=self.override_template_dirs,
            STATICFILES_DIRS=self.override_static_dirs,
            PROJECT_PATH='.'
        )
        middleware.settings = self.settings
        middleware.model_to_dict = mock_model_to_dict
        self.mw = middleware.TemplateOverrideMiddleware()
        self.view_url = '/view1'
        cache.clear()

    def test_no_override(self):
        """Make sure that we get default TEMPLATE_DIRS."""
        fake_override_qs = self.mimic.create_mock_anything()
        fake_override_qs.order_by('priority').and_return([])

        def fake_filter(*args, **kwargs):
            return fake_override_qs

        models.UserTemplateOverride.objects.filter = fake_filter

        fake_request = utils.FakeRequest()

        self.mimic.replay_all()

        self.mw.process_request(fake_request)

        self.assertEqual(
            middleware.settings.TEMPLATE_DIRS, self.override_template_dirs
        )
        self.assertEqual(
            middleware.settings.STATICFILES_DIRS, self.override_static_dirs
        )

    def test_empty_cached_override_value(self):
        """Test that we deal with cached empty values."""
        fake_request = utils.FakeRequest()
        # Add a cached value of pks which have something.
        cache.set(
            self.mw.get_tmpl_override_cache_key(fake_request.user),
            '[]',
            60
        )

        self.mw.process_request(fake_request)

        self.assertEqual(
            middleware.settings.TEMPLATE_DIRS, self.override_template_dirs
        )
        self.assertEqual(
            middleware.settings.STATICFILES_DIRS, self.override_static_dirs
        )

    def test_single_override_value_cached(self):
        """Test that an override is picked up and put at top of list."""
        fake_overrides = [
            {
                'pk': 1,
                'override_name': 'override',
                'override_dir': '/override',
                'priority': 1
            },
        ]
        expected_templates = ('./override_template', './templates')
        expected_static = ('./static', './override_staticfiles')
        # Setup fake request, and make sure there is a cached value.
        fake_request = utils.FakeRequest()
        cache.set(
            self.mw.get_tmpl_override_cache_key(fake_request.user),
            json.dumps(fake_overrides),
            60
        )

        self.mw.process_request(fake_request)
        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected_templates)
        self.assertEqual(middleware.settings.STATICFILES_DIRS, expected_static)

    def test_single_override_value(self):
        """Test that an override is picked up from the database."""
        expected = ('./override_template', './templates')
        # Setting up mocks for model interactions.
        fake_override_model = utils.FakeOverrideModel()
        fake_override_qs = self.mimic.create_mock_anything()
        fake_override_qs.order_by('priority').and_return([
            fake_override_model,
        ])

        def fake_filter(*args, **kwargs):
            return fake_override_qs

        models.UserTemplateOverride.objects.filter = fake_filter

        # Setup fake request, and make sure there is a cached value.
        fake_request = utils.FakeRequest()

        self.mimic.replay_all()

        self.mw.process_request(fake_request)

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected)

    def test_multiple_override_values_cached(self):
        """Test that multiple overrides are applied in the correct order."""
        expected_templates = (
            './top_override_template',
            './secondary_override_template',
            './tertiary_override_template',
            './templates'
        )
        expected_static = (
            './static',
            './tertiary_override_staticfiles',
            './secondary_override_staticfiles',
            './top_override_staticfiles',
        )

        fake_overrides = [
            {
                'pk': 1,
                'override_name': 'top_override',
                'override_dir': '/top_override',
                'priority': 1,
            },
            {
                'override_name': 'secondary_override',
                'override_dir': '/secondary_override',
                'priority': 2,
            },
            {
                'override_name': 'tertiary_override',
                'override_dir': '/tertiary_override',
                'priority': 3,
            },

        ]

        # Setup fake request, and make sure there is a cached value.
        fake_request = utils.FakeRequest()
        cache.set(
            self.mw.get_tmpl_override_cache_key(fake_request.user),
            json.dumps(fake_overrides),
            60
        )

        self.mimic.replay_all()

        self.mw.process_request(fake_request)

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected_templates)
        self.assertEqual(middleware.settings.STATICFILES_DIRS, expected_static)


    def test_multiple_override_values(self):
        """multiple overrides are applied in the correct order from db."""
        expected_templates = (
            './top_override_template',
            './secondary_override_template',
            './tertiary_override_template',
            './templates'
        )
        expected_static = (
            './static',
            './tertiary_override_staticfiles',
            './secondary_override_staticfiles',
            './top_override_staticfiles',
        )

        fake_override_model1 = utils.FakeOverrideModel(
            pk=1,
            override_name='top',
            override_dir='/top_override',
            priority=1,
        )
        fake_override_model2 = utils.FakeOverrideModel(
            pk=2,
            override_name='second',
            override_dir='/secondary_override',
            priority=2,
        )
        fake_override_model3 = utils.FakeOverrideModel(
            pk=3,
            override_name='tertiary',
            override_dir='/tertiary_override',
            priority=3,
        )

        fake_override_qs = self.mimic.create_mock_anything()
        fake_override_qs.order_by('priority').and_return([
            fake_override_model1,
            fake_override_model2,
            fake_override_model3,
        ])

        def fake_filter(*args, **kwargs):
            return fake_override_qs

        models.UserTemplateOverride.objects.filter = fake_filter

        # Setup fake request, and make sure there is a cached value.
        fake_request = utils.FakeRequest()

        self.mimic.replay_all()

        self.mw.process_request(fake_request)

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected_templates)
        self.assertEqual(middleware.settings.STATICFILES_DIRS, expected_static)

    def test_override_urlconf(self):
        """Test success case for overriding a request's urlconf."""
        middleware.settings = utils.fake_settings(
            TEMPLATE_DIRS=self.override_template_dirs,
            PROJECT_PATH='.',
            FINIAL_URL_OVERRIDES={'override': 'finial.tests.finial_test_overrides'},
            ROOT_URLCONF='test_settings'
        )
        fake_request = utils.FakeRequest()
        overrides = [{
            'pk': 1,
            'override_name': 'override',
            'override_dir': '/override',
            'priority': 1,
        }]
        mid_inst = middleware.TemplateOverrideMiddleware()
        test_urlconf = mid_inst.override_urlconf(fake_request, overrides)

        expected = 'finial.tests.finial_test_overrides'

        self.assertEqual(test_urlconf, expected)

    def test_override_urlconf_asymmetric_rules(self):
        """Does override_urlconf deal with more overrides than url rules?"""
        middleware.settings = utils.fake_settings(
            TEMPLATE_DIRS=self.override_template_dirs,
            PROJECT_PATH='.',
            FINIAL_URL_OVERRIDES={'override':'finial.tests.finial_test_overrides'},
            ROOT_URLCONF='test_settings'
        )
        fake_request = utils.FakeRequest()
        # Here we make the override for which there is no override_url defined
        # first, with highest priority.
        overrides = [
            {
                'pk': 2,
                'override_name': 'not_included_in_urlconf',
                'override_dir': '/not_in_urlconf',
                'priority': 1,

            },
            {
                'pk': 1,
                'override_name': 'override',
                'override_dir': '/override',
                'priority': 2,
            },
        ]
        mid_inst = middleware.TemplateOverrideMiddleware()
        test_urlconf = mid_inst.override_urlconf(fake_request, overrides)

        expected = 'finial.tests.finial_test_overrides'

        # Even though the "first" override doesn't have a URLconf entry
        # We still find one because we try all the overrides for a user
        # until we get the first one that does have a URconf override.
        self.assertEqual(test_urlconf, expected)


    def test_unauthenticated_user_is_skipped(self):
        """Make sure we don't do any lookups for unauth'ed users."""
        template_dirs = ('./templates',)
        staticfiles_dirs = ('./static',)
        middleware.settings = utils.fake_settings(
            TEMPLATE_DIRS=template_dirs,
            STATICFILES_DIRS=staticfiles_dirs,
            PROJECT_PATH='.',
        )

        fake_request = utils.FakeRequest()
        fake_request.user = utils.fake_user(is_authenticated=lambda self: False)

        self.assertFalse(fake_request.user.is_authenticated())

        mid_inst = middleware.TemplateOverrideMiddleware()

        mid_inst.process_request(fake_request)

        # Assert that nothing has changed, our unauthenticated user is a
        # noop.
        self.assertEqual(
            middleware.settings.TEMPLATE_DIRS, template_dirs
        )

        self.assertEqual(
            middleware.settings.STATICFILES_DIRS, staticfiles_dirs
        )

