Make a frontend change via a data migration:

To create a data migration (data, not schema), we need to create an empty migration file and then manually populate it with the data that needs changing.

The command to create an empty migration is below:

`./manage.py makemigrations --empty nsc`

See policy migration 8 as example (this migration updated a title and slug for a page)

The Django documentation, with an example, can be found here: https://docs.djangoproject.com/en/5.2/ref/migration-operations/#runpython