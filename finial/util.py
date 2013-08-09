from finial.models import UserTemplateOverride


def user_has_override(user, override_name):
    if not user.is_authenticated():
        return False
    if UserTemplateOverride.objects.filter(
        user=user,
        override_name=override_name
    ).exists():
        return True
    return False
