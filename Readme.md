# Django Post App showcase

This is a simple Django app to showcase the restful API for a blog post app. The project is using JWT for authrization/authentication and is with the support of running async tasks.

## Setup

The project is using poetry for dependency management. To install the dependencies, run the following command:

```bash
poetry install
```

After installing the dependencies, run the following command to populate the database. For the simplicity of the project, the database is using sqlite database from the django default.

```bash
poetry run python manage.py migrate
```

Run the following command to create a superuser.

```bash
poetry run python manage.py createsuperuser
```

Then run the following command to run the server.

```bash
poetry run python manage.py runserver
```

The server will be running on `http://localhost:8000/`.

## Usage

The app has a restful API for the following endpoints (defined in `django_post/urls.py`):

1. `/api/signup/` - POST for user signup, accepts email, password
2. `/api/login/` - POST for user login, accepts email, password, returns JWT token
3. `/api/token/refresh/` - POST for JWT token refresh, accepts refresh token, returns new access token
4. `/api/users/` - GET for listing users, available for superuser
5. `/api/users/<id>/` - GET, PUT, PATCH, DELETE for user detail, normal user can only access their own user detail
6. `/api/posts/` - GET, POST for listing posts, creating posts. Authenticated user can create posts
7. `/api/posts/<id>/` - GET, PUT, DELETE for post detail, authenticated user can update/delete their own posts
8. `/api/posts/<id>/` - PATCH for like/unlike post, accepts `liked`. authenticated user can like/unlike posts

The app defines the async tasks in `django_post_app/tasks.py`:
1. `enrich_user_location` - trigged after user signup, enrich the user location
2. `enrich_user_holiday_info` - trigged after `enrich_user_location` if user location is valid, enrich the user holiday info


## Testing

The app has a few tests for the endpoints. To run the tests, run the following command:

```bash
python manage.py test
```

The unit tests are defined in `django_post_app/tests_unit.py` and the api tests are defined in `django_post_app/tests_api.py`.

## Notes

The project is using `djangorestframework` and `djangorestframework_simplejwt` for the restful API and JWT authentication/authorization.
The project is also using `django-q` for async tasks.
The async tasks are using `requests` to interact with abstact apis.
For the simplicity of the project, it's using sqlite database from the django default and a cloud redis instance for the `django-q`.
