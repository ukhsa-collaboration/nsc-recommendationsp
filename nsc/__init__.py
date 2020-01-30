from __future__ import absolute_import, unicode_literals

from model_bakery import baker

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)


# A custom ArrayField was used to model the ages field on the Condition model
# so a better default widget would be available. While model bakery supports
# ArrayField it can't customized versions so we have to add a generator
# function that can be used to generate fake data. Ideally we should use the
# choices used on the model but that runs the risk of circular dependencies
# unless the choices are factored out but that makes things more obscure /
# complicated than necessary so we just use a hard-wired default value.

def generate_ages():
    return '{all}'


baker.generators.add('nsc.condition.fields.ChoiceArrayField', 'nsc.generate_ages')
