class Authenticator(object):

    def get_credentials(self, view):
        raise NotImplementedError()

    def authenticate(self, view):
        raise NotImplementedError()


class ModelAuthenticatorMixin(object):

    def __init__(self, model, lookup_field):
        self.model = model
        self.lookup_field = lookup_field

    async def authenticate(self, view):
        credentials = self.get_credentials(view)

        if not credentials:
            return None

        get_kwargs = {self.lookup_field: credentials}

        try:
            return await self.model.objects.get(**get_kwargs)
        except self.model.DoesNotExist:
            return None


class CookieAuthenticator(ModelAuthenticatorMixin, Authenticator):

    def __init__(self, *args, cookie_name='user', **kwargs):
        super().__init__(*args, **kwargs)
        self.cookie_name = cookie_name

    def get_credentials(self, view):
        try:
            return view.get_secure_cookie(self.cookie_name).decode()
        except AttributeError:
            return None


class HeaderAuthenticator(ModelAuthenticatorMixin, Authenticator):

    def __init__(self, *args, header_name='Authorization', **kwargs):
        super().__init__(*args, **kwargs)
        self.header_name = header_name

    def get_credentials(self, view):
        return view.request.headers.get(self.header_name, '').strip()
