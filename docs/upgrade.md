Upgrade Summary Document
🔧 Overview
This document outlines the major upgrade of this project:
- Python: 3.6 → 3.12.2
- Django: 3.2 → 5.0.3
- Node.js: 12.14.1 → 20.19.0
🐍 Python Upgrade
From: Python 3.6 To: Python 3.12

- Created a new virtual environment.
- Updated requirements-dev.in and recompiled requirements.txt using pip-compile.

Package Version Changes:
Package	Old Version	New Version	Type of Change
black	21.4b2	24.2.0	Major 🔺
pytest	6.2.3	8.3.5	Major 🔺
django	3.2.13	5.0.3	Major 🔺
pip-tools	—	6.4.0	Major 🔺
🌐 Django Upgrade
From: Django 3.2.13 To: Django 5.0.3
  Node Upgrade
Webpack config file was updated
Packages Updated (Major Changes):
Package	Old Version	New Version	Change
accessible-autocomplete	2.0.3	3.0.1	Major ✅
govuk-frontend	3.5.0	5.10.0	Major ✅
js-cookie	2.2.1	3.0.5	Major ✅
moment	2.29.1	2.30.1	Minor ✅
Webpack-related Major Version Updates

Package	Old Version	New Version	Change
image-webpack-loader	6.0.0	8.0.1	Major → ✅
resolve-url-loader	3.1.0	5.0.0	Major → ✅
source-map-loader	0.2.4	5.0.0	Major → ✅
svg-url-loader	3.0.3	8.0.0	Major → ✅
url-loader	3.0.0	4.1.1	Major → ✅
🔄 Database & ORM
Replaced deprecated models.NullBooleanField with models.BooleanField(null=True) to ensure compatibility with Django 5.0.
- NullBooleanField was removed in Django 4.0.
- Behavior remains the same: field can still hold True, False, or None
🛠 Tools Used
- npm audit and pip audit
- black (Code formatter)
- flake8 (Linter and style checker)
🐳 Docker Updates
- Python image updated in deploy/Dockerfile from centos/python-36-centos7 to python:3.12-slim
- Health check added in dev-docker/django/run.sh so Django waits for Postgres to be up first
- Python and node version updated in dev-docker and deploy/docker
- Frontend warnings with regards to govuk-frontend library update were fixed
  - Using /dist to the path
  - Making use of @use instead of @import in frontend scss files
  - Manually copy assets to public folder
  - Updated some html to use new classes where required
  Refer: https://frontend.design-system.service.gov.uk/import-font-and-images-assets/#if-you-have-your-own-folder-structure

Testing Summary
- ✅ All pytests pass after Django and platform upgrades.
- ✅ Admin interface and custom management commands verified.
📦 Yarn Upgrade
From: Yarn classic 1.21.1 To: Yarn berry 4.9.1
Refer: https://yarnpkg.com/migration/guide
☁️ OpenShift YML Updates
Node, Python and Postgres image was updated to 20, 3.12.2, and 13 respectively
📁GitHub Actions Workflow
- Python, node and Postgres version image updated in .github/workflows/ci.yml
- Postgres version was updated from 10.8 to 13
