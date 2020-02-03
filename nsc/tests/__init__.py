import random

from model_bakery import baker


# A custom ArrayField was used to model the ages field on the Condition model
# so a better default widget would be available. While model bakery supports
# ArrayField it can't customized versions so we have to add a generator
# function that can be used to generate fake data. Ideally we should use the
# choices used on the model but that runs the risk of circular dependencies
# unless the choices are factored out but that makes things more obscure /
# complicated than necessary so we just use a random selection from a list
# of hard-wired values.

all_ages = ["{antenatal}", "{newborn}", "{child}", "{adult}", "{all}"]


def generate_ages():
    return random.choice(all_ages)


baker.generators.add("nsc.condition.fields.ChoiceArrayField", "nsc.tests.generate_ages")
