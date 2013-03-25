import mimic

from django.core.cache import cache
from mock_django import query as mock_query, models as mock_models

from finial.tests import utils
from finial import middleware
from finial import models

class MiddlewareTest(mimic.MimicTestBase):

    def setUp(self):
        super(MiddlewareTest, self).setUp()
        self.template_dirs = ('./templates',)
        self.settings = utils.fake_settings(
            TEMPLATE_DIRS=self.template_dirs,
            PROJECT_PATH='.'
        )
        middleware.settings = self.settings
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

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, self.template_dirs)

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

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, self.template_dirs)

    def test_single_override_value_cached(self):
        """Test that an override is picked up and put at top of list."""
        expected = ('/override', './templates')
        # Setting up mocks for model interactions.
        fake_override_model = mock_models.ModelMock(models.UserTemplateOverride )
        fake_override_qs = mock_query.QuerySetMock(fake_override_model, 'order_by', 'values_list')

        def fake_filter(*args, **kwargs):
            return fake_override_qs

        models.UserTemplateOverride.objects.filter = fake_filter

        # Setup fake request, and make sure there is a cached value.
        fake_request = utils.FakeRequest()
        cache.set(
            self.mw.get_tmpl_override_cache_key(fake_request.user),
            '["/override", "./templates"]',
            60
        )

        self.mimic.replay_all()

        self.mw.process_request(fake_request)
        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected)

    def test_single_override_value(self):
        """Test that an override is picked up from the database."""
        expected = ('/override', './templates')
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
            '/top_override',
            '/secondary_override',
            '/tertiary_override',
            './templates'
        )

        # Setup fake request, and make sure there is a cached value.
        fake_request = utils.FakeRequest()
        cache.set(
            self.mw.get_tmpl_override_cache_key(fake_request.user),
            ('["/top_override", "/secondary_override",'
            '"/tertiary_override", "./templates"]'),
            60
        )

        self.mimic.replay_all()

        self.mw.process_request(fake_request)

        self.assertEqual(middleware.settings.TEMPLATE_DIRS, expected)


    def test_multiple_override_values(self):
        """multiple overrides are applied in the correct order from db."""
        expected = (
            '/top_override',
            '/secondary_override',
            '/tertiary_override',
            './templates'
        )

        fake_override_model1 = utils.FakeOverrideModel(
            template_name='top',
            template_dir='/top_override',
            priority=1,
        )
        fake_override_model2 = utils.FakeOverrideModel(
            template_name='second',
            template_dir='/secondary_override',
            priority=2,
        )
        fake_override_model3 = utils.FakeOverrideModel(
            template_name='tertiary',
            template_dir='/tertiary_override',
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
