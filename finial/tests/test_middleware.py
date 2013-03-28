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
        self.override_dirs = ('./templates',)
        self.settings = utils.fake_settings(
            TEMPLATE_DIRS=self.override_dirs,
            PROJECT_PATH='.'
        )
        middleware.settings = self.settings
        middleware.model_to_dict = mock_model_to_dict
        self.mw = middleware.TemplateOverrideMiddleware()
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

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, self.override_dirs)

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

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, self.override_dirs)

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
        expected = ('/override_template', './templates')
        # Setup fake request, and make sure there is a cached value.
        fake_request = utils.FakeRequest()
        cache.set(
            self.mw.get_tmpl_override_cache_key(fake_request.user),
            json.dumps(fake_overrides),
            60
        )

        self.mw.process_request(fake_request)
        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected)

    def test_single_override_value(self):
        """Test that an override is picked up from the database."""
        expected = ('/override_template', './templates')
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
        expected = (
            '/top_override_template',
            '/secondary_override_template',
            '/tertiary_override_template',
            './templates'
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

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected)


    def test_multiple_override_values(self):
        """multiple overrides are applied in the correct order from db."""
        expected = (
            '/top_override_template',
            '/secondary_override_template',
            '/tertiary_override_template',
            './templates'
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

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected)

    def test_override_urlconf(self):
        """Test success case for overriding a request's urlconf."""
        view_url = '/view1'
        middleware.settings = utils.fake_settings(
            TEMPLATE_DIRS=self.override_dirs,
            PROJECT_PATH='.',
            FINIAL_URL_OVERRIDES='finial.tests.finial_test_overrides',
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

        self.assertEqual(len(test_urlconf), 2)
        self.assertEqual(test_urlconf[0].resolve(view_url).func, 'override_view')
        self.assertEqual(test_urlconf[1].resolve(view_url).func, 'default_fake_view')

