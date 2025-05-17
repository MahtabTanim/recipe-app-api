# recipe-app-api

recipe app api
19 API ENdpoints
User Authentication
Admin Interface
Browsable API Using Swagger
django test suite

To Build :
docker compose build
Linting :
Dokcer compose run --rm app sh-c "flake8"
run :
docker compose up

Github Actions for Unit test and Linting:
Trigger : Push
Django Test Suite
Postgres database with Docker

Custom django command that waits the app until the database is loaded:
python manage.py wait_for_db

nginx for reverse proxy

deploy on aws

You have to login using your userid to access the swagger UI page
for browser :
You can either Use sessionauthentication which is default to django
or You can use tokenauth
for API clients :
You can authenticate using tokenauthentication by this URl
Alternatively to test just using token , you can use the /api/user/logout endpoint to logout from the session and use just the token authentication
