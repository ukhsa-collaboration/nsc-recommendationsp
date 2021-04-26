from django_auth_adfs.backend import AdfsAuthCodeBackend


class UniqueSessionAdfsBackend(AdfsAuthCodeBackend):
    def authenticate(self, request=None, authorization_code=None, **kwargs):
        user = super().authenticate(request=request, authorization_code=authorization_code, **kwargs)

        if (
            request
            and user.is_authenticated
            and user.last_session_id
            and request.session.session_key != user.last_session_id
        ):
            return None

        return user
