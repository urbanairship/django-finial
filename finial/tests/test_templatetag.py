from django.contrib.auth.models import User
from django.template import Template, Context

import mimic

from finial.models import UserTemplateOverride

class TemplateTagTests(mimic.MimicTestBase):
    def setUp(self):
        super(TemplateTagTests, self).setUp()
        self.t = Template('''
        {% load finial_flags %} 
        {% if user|has_finial_flag:"made_up" %}
        true
        {% else %}
        false
        {% endif %}
        ''')

    def tearDown(self):
        super(TemplateTagTests, self).tearDown()

    def test_returns_false_if_no_access(self):
        u = User.objects.create(username='finial-test')
        retval = self.t.render(Context({"user": u}))
        self.assertEqual('false', retval.strip())

    def _mock_post_save(self):
        fake_override_qs = self.mimic.create_mock_anything()
        fake_override_qs.order_by('priority').and_return([])

        def fake_filter(*args, **kwargs):
            return fake_override_qs

        self._orig_filter = UserTemplateOverride.objects.filter
        UserTemplateOverride.objects.filter = fake_filter
        self.mimic.replay_all()

    def _unmock_post_save(self):
        UserTemplateOverride.objects.filter = self._orig_filter

    def test_returns_true_if_has_access(self):
        u = User.objects.create(username='finial-test-also')

        o = UserTemplateOverride()
        o.user = u
        o.priority = 10
        o.override_name = 'made_up'
        o.override_dir = 'made_up_also'

        self._mock_post_save()
        o.save()
        self._unmock_post_save()

        retval = self.t.render(Context({"user": u}))

        self.assertEqual('true', retval.strip())
