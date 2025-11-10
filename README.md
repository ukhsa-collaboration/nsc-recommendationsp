
# UK NSC Product Development Runbook

This README provides a comprehensive guide for developers working on the UK National Screening Committee (NSC) product. It combines technical insights and step-by-step instructions for local development, testing, and deployment.

---

## 📦 Project Overview

**Product Name**: NSC Recommendations (Beta)  
**Commenced**: January 2020  
**Maintainers**: level3b@ukhsa.gov.uk  
**Repository**: [GitHub - NSC Recommendations](https://github.com/ukhsa-collaboration/nsc-recommendationsp)

For detailed developer documentation, see the `docs/` directory in the repository.

---

## 🔁 Development Process

### Branching Strategy

- Work should be done on **feature** or **bugfix** branches off of `develop` with reference to the Service Now ticket id where there details of the work sit.
- Merge changes into the `develop` branch for staging.
- Once fully tested and ready for release, merge `develop` into `master` for production.

### GitHub Actions

- Automatically runs tests on commit.
- Uses `pytest` for unit testing.
- Linting tools: `black`, `flake8`, `isort`
- Test coverage: ~96%
- If this pipeline fails, you will not be able to merge changes

---

## 🚀 Local Development Setup

Follow these steps to get the project running locally using Docker and Yarn.

### 1. Clone the Repository

```bash
git clone https://github.com/ukhsa-collaboration/nsc-recommendationsp.git
cd nsc-recommendationsp
```

### 2. Install System Dependencies

Ensure the following are installed:

- Python
- Docker & Docker Compose
- Node.js + Yarn

### 3. Updating environment variables if required

In order to update any environment variables, you will need to add them to the dev-docker-compose.yml.default file.
Inside the Django application build process, there is a list of environment variables.

#### Add Docker IP for local admin access to localhost:8000/django-admin

The DJANGO_ADMIN_IP_RANGES is set to the default docker subnet (this can be found looking in docker desktop --> settings --> resources --> network). If you do not use the default docker subnet you will need to update this.

### 4. Local setup

Install the project into a virtual environment:

    python3.12 -m venv ./venv
    source ./venv/bin/activate
    pip3 install -r requirements-dev.txt

### 5. Delete data migrations
This sounds very weird and very janky (because it is!) 🤮. In order to set up your local database, you need to scrape the production website [step 8](#8-initialising-the-database--migrations). However, you cannot scrape the website and save the data to the database without running the migrations. We run into an issue when it comes to running some of the later migrations, as those migrations involve changing data. 

If you have not yet populated your database, you cannot change the data, and the migration will fail - but you cannot populate the database without running the migrations (so we're stuck in a circle). To bypass this, below is a table of migration files that need to be deleted before running the migrations, and then restored and the migrations re run. 

This is only required for Local Dev! The staging and production databases are already populated and won't have this issue. This issue only exists when the database is starting empty.

##### Migrations to delete:
 *(you will be told when to restore them - hint: It's step 9)*
- All policy migrations starting at (and including) `nsc/policy/migrations/0008_auto_20251030_1655.py`

### 6. Docker-Based Local Environment

```bash
yarn docker
```

This starts all necessary services using Docker Compose.

### 7. Frontend Setup
Ensure you run these inside your virtual environment (venv)

✅  `yarn install`

✅  `yarn build` - this will run in production mode, use this for local development as it most closely resembles production

❌ `yarn dev` - this will run in development mode - this is currently unreliable and requires fixing


### 8. Initialising the database & migrations

The first time you run UK NSC locally, there is a set of django-extensions scripts that can be used to scrape data from the
UK NSC site. 

Run the following scraper scripts

   `docker-compose -f dev-docker-compose.yml exec django python manage.py runscript generate_legacy_index`

   `docker-compose -f dev-docker-compose.yml exec django python manage.py runscript scrape_policies`
   
   `docker-compose -f dev-docker-compose.yml exec django python manage.py runscript scrape_stakeholders`

   `docker-compose -f dev-docker-compose.yml exec django python manage.py runscript scrape_latest_reviews`
   
   `docker-compose -f dev-docker-compose.yml exec django python manage.py runscript scrape_latest_review_documents`


Website: https://view-health-screening-recommendations.service.gov.uk/

#### Troubleshooting
- If the CSS disappears after running these, re-run `yarn build`
- If you run these repeatedly in quick succession the connection might time out (suspected rate limiting). This can be overcome in a couple of ways:
   - Change the site you are scraping in the first script so that you start at the page for the data you are looking at (e.g. in def_scrape_contents setting the url = `f"{SITE}/?page=5#filter-box"` would mean you scrape data from page 5 and onwards. This makes your legacy_index.json file smaller, and so you will scrape fewer pages in the later scripts)
   - Make a cup of tea and come back later ☕️

### 9. Restore data migrations and re-run the migration scripts

Restore the migrations listed [here](#migrations-to-delete) from the git history

Run:
```bash
docker exec -it nsc-recommendationsp-django-1 bash
./manage.py migrate
```


### 10. Make a frontend change via a data migration:


To create a data migration (data, not schema), we need to create an empty migration file and then manually populate it with the data that needs changing.

The command to create an empty migration is below:

`./manage.py makemigrations --empty policy/review/notify` keep the name of the folder in which you wish to create a new migration


### 11. Create a Superuser

```bash
docker exec -it nsc-recommendationsp-django-1 bash
./manage.py createsuperuser
```

Follow the prompts to set up admin credentials.

You can now use these to log into the admin portal http:localhost/8000/django-admin

### 12. Running Tests & Linting

```bash
# Run tests
pytest

# Run formatters and linters
black .
flake8 .
isort .
```

---

## 🔄 Deployment Process

### Triggering a New Build in OpenShift

1. **Log into OpenShift** via the web console using UKHSA Azure SSO.
2. **Navigate to uknscr-build**
3. Go to **Builds > Build Configs** and select the app.
4. Click **“Start Build”** to:
   - Pull latest code from GitHub
   - Run tests (if configured)
   - Build and deploy containers
5. Monitor build progress under **Builds > Builds**.
6. Go to **ArgoCD** and sync across the environments
7. Verify deployment via staging/production URLs.

### Environments

- `develop` branch deploys to staging
- `master` branch deploys to production
- New environments can be created by redeploying the OpenShift template and pointing to a feature branch.

---

## 🧱 Infrastructure Overview

- Hosted on OpenShift using standard image streams.
- Load balancing via Kemp LoadMaster.
- Public access routed through application gateway.
- Database currently hosted within OpenShift.

---

## 🔐 Access & Roles

- GitHub access managed by project admins.
- Website roles:
  - Admin role used due to login issues with content editor.
  - Evidence Review Managers may need role adjustments.

