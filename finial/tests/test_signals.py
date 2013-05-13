# (c) 2013 Urban Airship and Contributors

import mimic
import json

from django.core.cache import cache

from finial import middleware
from finial import models
from finial import signals
from finial.tests import utils


class SignalsTest(mimic.MimicTestBase):

    def test_update_user_override_cache(self):
        """Does our signal update cache as we expect?"""
        fake_user = utils.fake_user(pk=1, username='tester')
        fake_override_model = utils.FakeOverrideModel()
        fake_override_model.user = fake_user
        fake_override_qs = self.mimic.create_mock_anything()
        fake_override_qs.order_by('priority').and_return(
            [fake_override_model]
        )

        def fake_filter(*args, **kwargs):
            return fake_override_qs

        models.UserTemplateOverride.objects.filter = fake_filter
        signals.model_to_dict = utils.mock_model_to_dict

        cache_key = middleware.TemplateOverrideMiddleware.get_tmpl_override_cache_key(
            fake_user
        )

        self.mimic.replay_all()

        cache.set(cache_key, '[]', 600)

        # Verify that we have a negative override cache value
        self.assertEqual(cache.get(cache_key), '[]')

        signals.update_user_override_cache(
            models.UserTemplateOverride,
            fake_override_model
        )
        expected = json.dumps([utils.mock_model_to_dict(fake_override_model)])

        # Verify that our cache key matches what we "pull" from db.
        self.assertEqual(cache.get(cache_key), expected)

    def test_deleting_from_cache(self):
        """We have a cached value, but what happens when we delete?"""
        fake_user = utils.fake_user(pk=1, username='tester')
        fake_override_model = utils.FakeOverrideModel()
        fake_override_model.user = fake_user
        fake_override_qs = self.mimic.create_mock_anything()
        # Because we're simulating a delete
        fake_override_qs.order_by('priority').and_return(
            []
        )
        def fake_filter(*args, **kwargs):
            return fake_override_qs

        models.UserTemplateOverride.objects.filter = fake_filter
        signals.model_to_dict = utils.mock_model_to_dict

        cache_key = middleware.TemplateOverrideMiddleware.get_tmpl_override_cache_key(
            fake_user
        )

        self.mimic.replay_all()

        cache.set(
            cache_key,
            ('[{"override_dir": "/override", "pk": 1,'
            '"priority": 1, "override_name": "test"}]'),
            600,
        )

        signals.update_user_override_cache(
            models.UserTemplateOverride,
            fake_override_model
        )
        expected = '[]'

        self.assertEqual(cache.get(cache_key), expected)
