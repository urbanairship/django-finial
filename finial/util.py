from django.contrib.auth.models import User
from django.db import transaction

from finial.models import UserTemplateOverride


def user_has_override(user, override_name):
    if not user.is_authenticated():
        return False
    if user.tmpl_overrides.filter(override_name=override_name).exists():
        return True
    return False


@transaction.atomic
def add_flag_to_all_users(flag, silent=False, batch_size=1000):
    users_without_override = User.objects.exclude(
        tmpl_overrides__override_name=flag
    )
    users_with_override = User.objects.filter(
        tmpl_overrides__override_name=flag
    )

    if not silent:
        response = raw_input(
            "Adding override %s to %s users "
            "(%s users already have override): (Y/N)" % (
                flag,
                users_without_override.count(),
                users_with_override.count()
            )
        )

        if response.upper() != "Y":
            raise Exception("Aborted")

    records_to_create = []
    for idx, user in enumerate(users_without_override.iterator()):
        if idx % batch_size == 0:
            print idx
            UserTemplateOverride.objects.bulk_create(records_to_create)
            records_to_create = []
        records_to_create.append(
            UserTemplateOverride(
                user=user,
                override_name=flag,
                override_dir=flag,
                priority=10,
            )
        )
    UserTemplateOverride.objects.bulk_create(records_to_create)


@transaction.atomic
def remove_flag_from_all_users(flag, silent=False):
    overrides = UserTemplateOverride.objects.filter(name=flag)

    if not silent:
        response = raw_input(
            "Removing override %s from %s users: (Y/N)" % (
                flag,
                overrides.count()
            )
        )

        if response.upper() != "Y":
            raise Exception("Aborted")

    overrides.delete()
