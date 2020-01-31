from django import apps
from django.core.exceptions import ValidationError


def get_apps():
    return apps.apps.get_app_configs()


def get_project_apps(name):
    return [app for app in get_apps() if app.name.startswith(name)]


def get_model(name):
    return apps.apps.get_model(name)


def get_models():
    models = []
    for app in get_apps():
        models.extend(get_app_models(app))
    return models


def get_fields():
    fields = []
    for model in get_models():
        fields.extend(get_model_fields(model))
    return fields


def get_field(model_name, field_name):
    fields = get_model_fields(get_model(model_name))
    return [field for field in fields if field.name == field_name][0]


def get_app_models(app):
    return list(app.get_models())


def get_model_fields(model):
    return model._meta.get_fields()  # noqa


def is_pk(field):
    return hasattr(field, 'primary_key') and field.primary_key is True


def is_fk(field):
    return field.is_relation and \
        not field.many_to_many and field.many_to_one and \
        not field.one_to_many and not field.one_to_one


def is_reverse_fk(field):
    return field.is_relation and \
        not field.many_to_many and not field.many_to_one and \
        field.one_to_many and not field.one_to_one


def is_one_to_one(field):
    return field.is_relation and \
        not field.many_to_many and not field.many_to_one and \
        not field.one_to_many and field.one_to_one


def is_text_field(field):
    name = field.__class__.__name__
    return name == 'TextField' or name == 'CharField'


def is_allowed(field, value):
    try:
        for validator in field.validators:
            validator(value)
    except ValidationError:
        return False
    else:
        return True


def is_fetched(obj, relation_name):
    return relation_name in getattr(obj, '_state').fields_cache


def all_subclasses(cls):
    return set(cls.__subclasses__()).union([
        s for c in cls.__subclasses__() for s in all_subclasses(c)])
