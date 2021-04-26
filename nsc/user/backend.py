from django_auth_adfs.backend import AdfsAuthCodeBackend


class UniqueSessionAdfsBackend(AdfsAuthCodeBackend):
    def authenticate(self, *args, request=None, **kwargs):
        user = super().authenticate(*args, request=request, **kwargs)

        if (
            request
            and user.is_authenticated
            and request.session.session_key != user.last_session_id
        ):
            return None

        return user
