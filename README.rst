=======================================================
PHE National Screening Committee Recommendations (Beta)
=======================================================

.. image:: https://travis-ci.org/PublicHealthEngland/nsc-recommendations.svg?branch=master
    :target: https://travis-ci.org/PublicHealthEngland/nsc-recommendations

Commenced January 2020

Product Owner: Adrian.Byrtus@phe.gov.uk

For developer information see the project documentation in ``docs``.

## 🚀 Local Development Setup

Follow these steps to get the project running locally using Docker and Yarn.

---

### 1. Clone the Repository

    git clone https://github.com/ukhsa-collaboration/nsc-recommendationsp.git

    cd nsc-recommendationsp


### 2. Install System Dependencies

    Python
    
    Docker & Docker Compose
    
    Node.js + Yarn

### 3. Frontend Setup

    yarn install

    yarn build

### 4. Docker-Based Local Environment

    cp dev-docker-compose.yml.default dev-docker-compose.yml

    docker-compose -f dev-docker-compose.yml up --build

### 5. Database Migrations

    ./manage.py makemigrations

    ./manage.py migrate


### 6. Create a Superuser

