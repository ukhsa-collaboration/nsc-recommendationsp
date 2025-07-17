from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect


def custom_admin_logout(request):
    logout(request)
    tenant_id = settings.ACTIVE_DIRECTORY_TENANT_ID
    redirect_uri = request.build_absolute_uri("/")  # or your preferred URL
    azure_logout_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/logout"  # noqa
        f"?post_logout_redirect_uri={redirect_uri}"
    )
    return redirect(azure_logout_url)
