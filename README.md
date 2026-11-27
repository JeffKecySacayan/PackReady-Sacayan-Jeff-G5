# PackReady

A web-based packing checklist and trip preparation system for travelers.
Built with Django (full stack, Django templates) and PostgreSQL on Supabase.

**Student:** Sacayan, Jeff Kecy · **Section:** G5 · **Course:** CSIT327 Information Management 2

## Core feature: Packing Lists (Project Development 2)

Travelers plan trips and build packing lists for them. They add items to a list,
mark each item as packed, and see their packing progress at a glance.

- **Trips:** create, view, edit and delete trips (destination, trip type, dates)
- **Packing lists:** create, view, edit and delete lists, optionally linked to a trip
- **List items:** add, edit, remove and mark items as packed, with a progress bar
- **Admin overview:** admins see all packing lists, read-only, on their dashboard

### Roles

| Role | Access |
|---|---|
| Traveler | Full CRUD on their own trips, lists and items |
| Admin | Read-only view of all packing lists, user management through Django admin |

### Standard features (Project Development 1)

Registration with validation, login/logout, role-based dashboards, and a profile page
with photo upload. Passwords are hashed with Django's built-in authentication.

## Tech stack

- Python and Django
- PostgreSQL (Supabase)
- Bootstrap 5 for the Django templates

## Setup

1. Clone the repository and open the folder.
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your Supabase database credentials and a Django secret key.
5. Apply the migrations (this also seeds the default trip types and categories):
   ```
   python manage.py migrate
   ```
6. Create an admin account:
   ```
   python manage.py createsuperuser
   ```
7. Run the server and open http://127.0.0.1:8000/:
   ```
   python manage.py runserver
   ```

## Branching

`main` holds stable code only. Work happens on `feature/*` branches, which are merged
into `develop` through pull requests, and `develop` is merged into `main` for each increment.