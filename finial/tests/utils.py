def fake_settings(**kwargs):
    return type('FakeSettings', (object,), kwargs)()


def fake_user(**kwargs):
    return type('FakeUser', (object,), kwargs)()


class FakeRequest(object):
    """A simple request stub."""
    def __init__(self, *args, **kwargs):
        self.method = kwargs.get('method', 'GET')
        self.meta = kwargs.get('META', {'REMOTE_ADDR': '127.0.0.1'})
        self.user = fake_user(
            pk=kwargs.get('user_pk', 1),
            username=kwargs.get('user_username', 'tester'),
            email=kwargs.get('user_email', 'tester@example.com')
        )

class FakeOverrideModel(object):
    """A simple OverrideModel stub."""
    def __init__(self, *args, **kwargs):
        self.template_name = kwargs.get('template_name', 'test')
        self.template_dir = kwargs.get('template_dir', '/override')
        self.priority = kwargs.get('priority', 1)


