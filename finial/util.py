

def user_has_override(user, override_name):
    if not user.is_authenticated():
        return False
    if user.tmpl_overrides.filter(override_name=override_name).exists():
        return True
    return False
