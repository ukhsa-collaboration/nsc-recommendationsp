from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView
import logging
logger = logging.getLogger(__name__)

from nsc.review.views import ReviewDashboardView


admin.autodiscover()


urlpatterns = [
    path(
        r"cookies", TemplateView.as_view(template_name="cookies.html"), name="cookies"
    ),
    path(
        r"feedback",
        TemplateView.as_view(template_name="feedback.html"),
        name="feedback",
    ),
    path(r"admin/", ReviewDashboardView.as_view(), name="dashboard"),
    path(r'admin-logout/', LogoutView.as_view(next_page='/admin/login/'), name='admin_logout'),
    path(r"contact/", include("nsc.contact.urls", namespace="contact")),
    path(r"document/", include("nsc.document.urls", namespace="document")),
    path(r"stakeholder/", include("nsc.stakeholder.urls", namespace="stakeholder")),
    path(r"policy/", include("nsc.policy.urls", namespace="policy")),
    path(r"review/", include("nsc.review.urls", namespace="review")),
    path(r"subscribe/", include("nsc.subscription.urls", namespace="subscription")),
    path("helpdesk/", include("nsc.support.urls", namespace="support")),
    path(r"_health/", lambda request: HttpResponse()),
    path("_notify/", include("nsc.notify.urls", namespace="notify")),
    path(r"django-admin/", admin.site.urls),
    path(r"", include("nsc.condition.urls", namespace="condition")),
]

if settings.AUTH_USE_ACTIVE_DIRECTORY:
    logger.info("Using Active Directory authentication URLs.")
    urlpatterns += [
        path("accounts/", include("django_auth_adfs.urls")),
    ]
else:
    logger.info("Using default Django login view.")
    urlpatterns += [
        path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [path(r"__debug__/", include(debug_toolbar.urls))]
