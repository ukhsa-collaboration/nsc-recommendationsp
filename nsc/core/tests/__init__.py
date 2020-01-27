from model_bakery import baker


def generate_ages():
    return '{all}'


baker.generators.add('nsc.core.fields.ChoiceArrayField', 'nsc.core.tests.generate_ages')
