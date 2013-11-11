# (c) 2013 Urban Airship and Contributors

import importlib
import json
import types

import mimic

from django.core.cache import cache
from django.conf.urls import include, patterns, url

from finial import middleware
from finial import models
from finial.tests import utils


class MiddlewareTest(mimic.MimicTestBase):

    def setUp(self):
        super(MiddlewareTest, self).setUp()
        self.override_template_dirs = ('./templates',)
        self.override_static_dirs= ('./static',)
        self.settings = utils.fake_settings(
            TEMPLATE_DIRS=self.override_template_dirs,
            STATICFILES_DIRS=self.override_static_dirs,
            PROJECT_PATH='.',
        )
        middleware.settings = self.settings
        middleware.model_to_dict = utils.mock_model_to_dict
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
        expected_static = ('./override_staticfiles', './static')
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
            './top_override_staticfiles',
            './secondary_override_staticfiles',
            './tertiary_override_staticfiles',
            './static',
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
            './top_override_staticfiles',
            './secondary_override_staticfiles',
            './tertiary_override_staticfiles',
            './static',
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

    def _import_fake_urlconf(self, path):
        urlconf_mod = types.ModuleType('UnittestingUrlConf', 'For testing.')
        urlconf_mod.urlpatterns = patterns(
            '', url('', path, name='{0}_name'.format(path))
        )

        return urlconf_mod

    def test_override_urlconf(self):
        """Test success case for overriding a request's urlconf."""
        paths = ['path.number1', 'path.number2']
        middleware.settings = utils.fake_settings(
            TEMPLATE_DIRS=self.override_template_dirs,
            PROJECT_PATH='.',
            FINIAL_URL_OVERRIDES={
                'override': paths[0],
                'override2': paths[1]
            },
            ROOT_URLCONF='test_settings'
        )
        fake_request = utils.FakeRequest()
        overrides = [{
            'pk': 1,
            'override_name': 'override',
            'override_dir': '/override',
            'priority': 1,
        },
        {
            'pk': 2,
            'override_name': 'override2',
            'override_dir': '/override2',
            'priority': 2,
        }]

        self.mimic.stub_out_with_mock(importlib, 'import_module')

        for path in paths:
            importlib.import_module(path).and_return(
                self._import_fake_urlconf(path)
            )

        self.mimic.replay_all()

        mid_inst = middleware.TemplateOverrideMiddleware()
        test_urlconf = mid_inst.override_urlconf(fake_request, overrides)

        expected = patterns(
            '',
            url('', paths[0], name='{0}_name'.format(paths[0])),
            url('', paths[1], name='{0}_name'.format(paths[1])),
            url('', include('test_settings'))
        )


        self.assertEqual(len(test_urlconf.urlpatterns), len(expected))
        for i in range(len(test_urlconf.urlpatterns) -1):
            self.assertEqual(
                test_urlconf.urlpatterns[i].name, expected[i].name
            )
            self.assertEqual(
                test_urlconf.urlpatterns[i].regex.pattern,
                expected[i].regex.pattern
            )

        self.assertEqual(
            test_urlconf.urlpatterns[-1].urlconf_name,
            expected[-1].urlconf_name
        )

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

