
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

### Updating environment variables

#### Admin portal vars

In order to allow access to the admin portal /django-admin/ you will need to add your IP address to the dev-docker-compose.yml.default file
Inside the Django application build process, there is a list of environment variables - one of which is DJANGO_ADMIN_IP_RANGES
Add your IP to this value.


### 3. Frontend Setup

```bash
yarn install
yarn build - this will run in production mode!
yarn dev - this will run in development mode!
```

### 4. Add Docker IP for local admin access to localhost:8000/django-admin

The DJANGO_ADMIN_IP_RANGES is set to the default docker subnet (this can be found looking in docker desktop --> settings --> resources --> network). 

### 5. Docker-Based Local Environment

```bash
cp dev-docker-compose.yml.default dev-docker-compose.yml
docker-compose -f dev-docker-compose.yml up --build
```

This starts all necessary services using Docker Compose.

### 5. Django setup

Install the project into a virtual environment::

    python3.12 -m venv ./venv
    source ./venv/bin/activate
    pip3 install -r requirements-dev.txt

### 6. Local Database Migrations & Setup

Inside the backend container (`nsc-recommendationsp-django-1`) (or using `docker exec -it nsc-recommendationsp-django-1 bash` directly from your terminal):

```bash
./manage.py makemigrations
./manage.py migrate
```
### 7. Migration for data 
`./manage.py makemigrations --empty nsc`
Update to match change
See policy migration 8 as example
#TODO: Add more details

### 7. Create a Superuser

```bash
./manage.py createsuperuser
```

Follow the prompts to set up admin credentials.

You can now use these to log into the admin portal http://8000/django-admin

### 8. Running Tests & Linting

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

