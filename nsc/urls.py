from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView


admin.autodiscover()

urlpatterns = [
    path(r"", TemplateView.as_view(template_name="home.html"), name="home"),
    path(r"condition/", include("nsc.condition.urls", namespace="condition")),
    path(r"contact/", include("nsc.contact.urls", namespace="contact")),
    path(r"organisation/", include("nsc.organisation.urls", namespace="organisation")),
    path(r"policy/", include("nsc.policy.urls", namespace="policy")),
    path(r"admin/", TemplateView.as_view(template_name="admin.html"), name="admin"),
    path(r"admin/db/", admin.site.urls),
    path(r"health/", lambda request: HttpResponse()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [path(r"__debug__/", include(debug_toolbar.urls))]
