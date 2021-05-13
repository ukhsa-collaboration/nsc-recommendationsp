from django.contrib.sessions.models import Session
from django.utils.timezone import now

from django_auth_adfs.backend import AdfsAuthCodeBackend


class UniqueSessionAdfsBackend(AdfsAuthCodeBackend):
    def authenticate(self, request=None, authorization_code=None, **kwargs):
        user = super().authenticate(
            request=request, authorization_code=authorization_code, **kwargs
        )
        last_session = Session.objects.filter(
            session_key=getattr(user, "last_session_id", None)
        ).first()

        if (
            request
            and user
            and user.is_authenticated
            and last_session
            and last_session.expire_date > now()
            and request.session.session_key != last_session.session_key
        ):
            return None

        return user
