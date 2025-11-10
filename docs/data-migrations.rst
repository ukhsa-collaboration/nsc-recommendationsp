Running a migration
===================
To run database migrations, follow the steps in the main readme

============================================
Make a frontend change via a data migration:
============================================

To create a data migration (data, not schema), we need to create an empty migration file and then manually populate it with the data that needs changing.

The command to create an empty migration is below:

`./manage.py makemigrations --empty policy/review/notify` keep the name of the folder in which you wish to create a new migration

See policy migration 8 as example (this migration updated a title and slug for a page)
The Django documentation, with an example, can be found here: https://docs.djangoproject.com/en/5.2/ref/migration-operations/#runpython

=======================
Re-running a migration
=======================
If you need to re-run a migration, go to the migrations table, and delete the migration you need to re-run (as well as an subsequent migrations). Then re-run the migration commands. 

