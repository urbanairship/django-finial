from django.contrib.auth.models import User
from django.db import models


class UserTemplateOverride(models.Model):
    """One to many relationship of template overrides per user.

    Note: a user should never have more than one override with
    the same priority. Doing so could lead to inconsistent behavior.
           **Enforce this in form.clean().**

    An example of good data:

    user: 'user1', priority: 1, override_name; 'Some override'
    user: 'user1', priority: 2, override_name; 'Some other override'
    user: 'user2', priority: 1, override_name; 'Some override'

    """
    user = models.ForeignKey(User, related_name='tmpl_overrides')
    override_name = models.CharField(max_length=255)
    override_dir = models.CharField(max_length=255)
    priority = models.PositiveSmallIntegerField(default=1)
