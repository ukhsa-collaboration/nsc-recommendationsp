from django.db.models import Model
from django.test import RequestFactory
from django.urls import reverse

from nsc.utils.models import all_subclasses


def get_add_url(model):
    meta = getattr(model, "_meta")
    return reverse("admin:%s_%s_add" % (meta.app_label, meta.model_name))


def get_change_url(instance):
    meta = getattr(instance, "_meta")
    return reverse(
        "admin:%s_%s_change" % (meta.app_label, meta.model_name), args=(instance.pk,)
    )


def get_delete_url(instance):
    meta = getattr(instance, "_meta")
    return reverse(
        "admin:%s_%s_delete" % (meta.app_label, meta.model_name), args=(instance.pk,)
    )


def get_changelist_url(model):
    meta = getattr(model, "_meta")
    return reverse("admin:%s_%s_changelist" % (meta.app_label, meta.model_name))


def get_models(site):
    return [model for model in all_subclasses(Model) if site.is_registered(model)]


def get_add_models(site, user):
    results = []
    registry = getattr(site, "_registry")
    for model in get_models(site):
        request = RequestFactory().get(get_add_url(model))
        request.user = user
        if registry[model].has_add_permission(request):
            results.append(model)
    return results


def get_change_models(site, user):
    results = []
    registry = getattr(site, "_registry")
    for model in get_models(site):
        request = RequestFactory().get(get_add_url(model))
        request.user = user
        if registry[model].has_change_permission(request):
            results.append(model)
    return results


def get_delete_models(site, user):
    results = []
    registry = getattr(site, "_registry")
    for model in get_models(site):
        request = RequestFactory().get(get_delete_url(model))
        request.user = user
        if registry[model].has_delete_permission(request):
            results.append(model)
    return results
