# Restaurant Kitchen Service

A simple Django website for managing a restaurant kitchen.

## Features

- cooks, dishes and dish types management
- ingredients as an optional feature
- login and logout
- search and pagination
- assigning cooks to dishes

## Database diagram

![Database diagram](docs/database-schema.svg)

## How to run

```bash
git clone https://github.com/askawa/restaurant-kitchen-service.git
cd restaurant-kitchen-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser.

## Tests

```bash
python manage.py test
```

Project screenshots are available in [`docs/screenshots`](docs/screenshots).
