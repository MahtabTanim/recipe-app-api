# 🧾 Recipe App API

A Django REST Framework–based backend for managing recipes, ingredients, and tags with user authentication.

---

## 🚀 Features

- ✅ 19 API Endpoints
- 🔐 User Authentication (Session + Token)
- 🛠️ Admin Interface
- 📄 Interactive API Documentation via Swagger UI
- 🔍 Django Test Suite
- 🐘 PostgreSQL database (via Docker)
- 🌐 NGINX reverse proxy
- 📦 Dockerized development and deployment
- 🧪 GitHub Actions for testing and linting
- ☁️ Deployable to AWS

---

## ⚙️ Setup

### ⚙️ Environment Variables

To run the project with Docker, you must create your own `.env` file.

A sample `.env` file is provided in the repository. You can copy it using:

```bash
cp .env.sample .env
```

### 🧱 Build the App

```bash
docker compose build
```

### 🚀 Run the App

```bash
docker compose up
```

### 👤 Create Superuser

After the app is running, in a new terminal run:

```bash
docker compose run --rm app sh -c "python manage.py createsuperuser"
```

### ✅ Linting

```bash
docker compose run --rm app sh -c "flake8"
```

### 🐘 Wait for DB (custom Django management command)

```bash
python manage.py wait_for_db
```

---

## 🔐 Authentication

### Accessing Swagger UI

You must be **logged in** to access Swagger at `/api/docs`.

- **Browser**:

  - Use **Session Authentication** (default in Django)
  - Or use a **Token** via Swagger’s Authorize button

- **API Clients (e.g., Postman)**:

  - Use **Token Authentication** by requesting a token from:

    ```
    POST /api/user/token/
    ```

  - To test token-only behavior, logout of the session with:

    ```
    POST /api/user/logout/
    ```

---

## 📚 API Endpoints

### 📘 Schema

- `GET /api/schema` — Returns the OpenAPI schema.

---

### 👤 User

- `POST /api/user/create/` — Create a new user (username is the email)
- `GET /api/user/me/` — Get current user details
- `PATCH /api/user/me/` — Update current user details
- `POST /api/user/token/` — Get token for valid user
- `POST /api/user/logout/` — Logout current session

---

### 🧂 Ingredients

- `GET /api/recipe/ingredient/` — List ingredients created by the user
  **Filters**: `assigned_only=true`
- `PUT/PATCH /api/recipe/ingredient/{id}/` — Edit an ingredient
- `DELETE /api/recipe/ingredient/{id}/` — Delete an ingredient

---

### 🍲 Recipes

- `GET /api/recipe/recipe/` — List recipes created by the user
  **Filters**: `ingredients`, `tags`
- `POST /api/recipe/recipe/` — Create a new recipe
- `GET /api/recipe/recipe/{id}/` — Get details of a specific recipe
- `PATCH /api/recipe/recipe/{id}/` — Edit a recipe
- `DELETE /api/recipe/recipe/{id}/` — Delete a recipe
- `POST /api/recipe/recipe/{id}/upload-image/` — Upload an image for a recipe

---

### 🏷️ Tags

- `GET /api/recipe/tag/` — List tags created by the user
  **Filters**: `assigned_only=true`
- `GET /api/recipe/tag/{id}/` — Get details of a tag
- `PUT/PATCH /api/recipe/tag/{id}/` — Edit a tag
- `DELETE /api/recipe/tag/{id}/` — Delete a tag

---

## 🧪 Testing & CI

- ✅ All endpoints are covered by tests (60+ total)
- Tests and linting run on **every push** via **GitHub Actions**
- Uses:
  - Django test suite
  - PostgreSQL (via Docker)
  - `flake8` for linting

---

## 🌐 Deployment

- Reverse proxy via **NGINX**
- Ready for deployment to **AWS**
