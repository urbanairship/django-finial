# (c) 2013 Urban Airship and Contributors

from django.contrib.auth.models import User
from django.db import models

from finial import signals


class UserTemplateOverride(models.Model):
    """One to many relationship of template overrides per user.

    Note: a user should never have more than one override with
    the same priority. Doing so could lead to inconsistent behavior.
           **Enforce this in form.clean().**

    An example of good data (in dict format):

    {
        user: user1, priority: 1,
        override_name: 'Some override', override_dir: '.'
    }
    {
        user: user1, priority: 2,
        override_name: 'Some other override', override_dir: '.'
    }

    """
    user = models.ForeignKey(User, related_name='tmpl_overrides')
    override_name = models.CharField(max_length=255)
    override_dir = models.CharField(max_length=255)
    priority = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return u'{0}; User: {1}; Priority: {2}'.format(
            self.override_name,
            self.user,
            self.priority
        )


models.signals.post_save.connect(
    signals.update_user_override_cache,
    sender=UserTemplateOverride
)
models.signals.post_delete.connect(
    signals.update_user_override_cache,
    sender=UserTemplateOverride
)
