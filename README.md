# FarmsteadHelper

**FarmsteadHelper** is a web platform designed for landowners, gardeners, and nature enthusiasts. It combines a wiki-like catalog of different sorts of trees, vegetables, flowers, and animals, a discussion forum, an interactive yard planner, and a yearly calendar to help users organize their homesteading life.

---
## Authors:

- **Kredle (Oleh Paliukh)**: <a href="https://www.linkedin.com/in/oleh-paliukh-8838472b5/"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRZy25qVnXim0IHxSZ9q0eQiW3E-NHXxDjuQ&s" alt="LinkedIn" width="30" height="30"></a> 
- **GreyTheCat (Nazarii Fedorchak)**: <a href="https://www.linkedin.com/in/nazariy-fedorchak-845692334/"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRZy25qVnXim0IHxSZ9q0eQiW3E-NHXxDjuQ&s" alt="LinkedIn" width="30" height="30"></a>
- **AndriiyKr (Andrii Kravchuk)**: <a href="https://www.linkedin.com/in/andrii-kravchuk-15a251360"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQRZy25qVnXim0IHxSZ9q0eQiW3E-NHXxDjuQ&s" alt="LinkedIn" width="30" height="30"></a>

---

## Tech Stack

- **Backend**: Django (Python), Django REST Framework
- **Frontend**: JavaScript, HTML5, CSS3 + Django Templates
- **Database**: PostgreSQL
- **Payments**: Stripe API
- **Deployment**: WSGI/ASGI
- **API Testing**: Postman
- **Other Tools**: reCAPTCHA, IPinfo

---

## 4-Layered Domain-Driven Design (DDD) Architecture

The project implements a strict 4-layered architecture based on DDD principles to separate business logic from technical implementation, ensuring high maintainability and stability:

- **Presentation Layer** (`api/views.py`, `forum/views.py`, etc.):
  - Handles incoming HTTP requests, initial data validation, and throttling.
  - Delegates all business operations to the Application layer.
- **Application Layer** (`farmstead_farmer/core/application`):
  - Contains Use Cases (e.g., `ProfileUseCase`, `CatalogUseCase`) that orchestrate business workflows without being tied to the database or framework specifics.
- **Domain Layer** (`farmstead_farmer/core/domain`):
  - The core of the system. Contains pure business entities, domain exceptions, and abstract repository interfaces. Completely isolated from external dependencies.
- **Infrastructure Layer** (`farmstead_farmer/core/infrastructure`):
  - Implements repository interfaces using Django ORM (`DjangoUserRepository`, `DjangoCatalogRepository`).
  - Handles external integrations (PostgreSQL, Stripe webhooks, email SMTP).

---

## Project Structure

```text
farmstead_farmer/
├── animals/                                 # Animals branch for catalog
├── api/                                     # Authentication, profiles, and core API views
│ ├── middleware.py                          # Rate limiting and API Whitelisting
│ ├── serializers.py                         # DRF serializers for I/O validation
│ └── views.py                               # Presentation layer endpoints
├── core/                                    # DDD Architecture Core
│ ├── application/                           # Use Cases (Business orchestration)
│ ├── domain/                                # Entities and Interfaces
│ └── infrastructure/                        # ORM Repositories and external services
├── calendar_/                               # Calendar section
├── catalog/                                 # Catalog section (Search and filtering)
├── farmstead_farmer/                        # Global web application settings
├── feedback/                                # Feedback form with reCAPTCHA
├── forum/                                   # Social interaction and discussions
├── interactive_map/                         # Canvas-based yard planner
├── main_page/                               # Landing page
├── plants/                                  # Flowers branch for catalog
├── trees/                                   # Trees branch for catalog
├── vegetables/                              # Vegetables branch for catalog
├── manage.py                                # Django's command-line utility
└── requirements.txt                         # Dependencies
```
---

### Database Structure
Database contains 26 tables, where most important are:

- Plants (Flowers) table:

  ![image](https://github.com/user-attachments/assets/5e2fd9a8-6863-4980-b466-5a984402d27f)
  
- Trees table, sorts table (sorts of certain tree), fertillizer, etc.

  ![image](https://github.com/user-attachments/assets/1f854cdd-d0dd-47c6-bc4c-8c9a36b4e05e)

- Vegetables table, sorts_veg table, etc.

  ![image](https://github.com/user-attachments/assets/f292e71d-b032-4d7d-acbf-4866216715a2)

- Animals table and kinds table

  ![image](https://github.com/user-attachments/assets/88f2ff02-e0f4-4415-848b-e538efb9cfee)

- Topics and comments tables (Used for Forum)

  ![image](https://github.com/user-attachments/assets/201b0b68-6284-4764-bb72-c277df973e29)

- Otp table (Used for OTP model and caching)

  ![image](https://github.com/user-attachments/assets/e44a4326-b6b7-41c1-9dc2-f2018d5410ac)

- User table, interactive_map table, notifications table and django generated tables joined to user table

  ![image](https://github.com/user-attachments/assets/1e4e0c15-1891-4fac-a69f-71bbd87914da)

---
---

## Core Features

### Catalog (Knowledge Base)
A structured, wiki-style reference system for different types of farm-related items:

- Categories: Animals, Trees, Flowers, Vegetables.
- Each entry includes images, descriptions, tips, and **deep agricultural data** (soil types, optimal temperature ranges, and biological compatibility).
- Multi-criteria smart search that ignores typos and case sensitivity.
- Users can bookmark varieties ("Add to Favorites") for quick access in their profile.
- "Can be interesting for you" section, where users can randomize sorts of different categories.
- Includes filter functionality in the recommendation section, allowing users to choose specific categories.

---

### Forum
A place for users to share experience and ask questions, backed by a strict role model:

- Discussions organized by category (Trees, Vegetables, Flowers, Animals).
- **Role-based Access**: Guests (read-only), Farmers (create/edit own content), and Moderators.
- **Secure Moderation**: To prevent abuse, administrator privileges are protected by 2FA. Moderators must request and enter an OTP from their email to temporarily unlock content-deletion capabilities.
- Users can report topics and comments if they break the rules of the platform (asynchronous reports sent to moderators).
- Users can edit their comments and topics.
- Sorting discussions by likes count and filtering by keywords, categories, or both.
- If a user's comment gets deleted, replies to that comment automatically change from "Відповідь на коментар **username**" to "Відповідь на коментар Коментар видалено".
- If a user deletes their account, the topic author changes to "Користувача видалено".
- Username changes are automatically propagated throughout the forum.

---

### Interactive Map
An intuitive, scientifically grounded homestead planner:

- Users can design their yard by:
  - Drawing areas (soil, grass, water).
  - Making rectangular-shaped areas with the dot tool.
  - Adding trees, vegetables, flowers, and structures.
  - Using Undo (CTRL+Z) and Redo (CTRL+SHIFT+Z) buttons.
- **Advanced Automated Validation**: The system automatically checks plant placement against soil types, temperature constraints, and biological compatibility (allelopathy matrix) to prevent agronomic mistakes.
- **Premium Subscription**: Integrated with Stripe API. Premium users unlock unlimited elements and advanced compatibility reports.
- Save the layout to the profile and edit it later.
- Map visibility can be toggled between public and private. If another user visits a private map, it remains hidden, while public maps open in preview mode.

---

### Calendar
A visual farming planner:

- Displays a 12-month view.
- Tasks/events are shown as colored stripes per date.
- Users can filter by crop type, season, or activity.
- Includes search functionality.

---

### User Profile & Editing
Every user has a personal dashboard:

- Displays profile picture, name, bio (max 150 characters), registration date, and last seen status.
- Lists favorite varieties and favorite discussions.
- Link to their saved interactive map.
- Users can edit their firstname, lastname, profile photo, and bio.
- Change username (once every 7 days).
- Change password or set a new email address.
- Manage privacy settings for Favorites and the Interactive map.
- **Secure Account Deletion**: Protected by behavioral analysis (reCAPTCHA) and requires email OTP confirmation.

---

### Security

To protect the platform from cyberattacks and data scraping, the following measures were implemented:

- Login and registration validations are strictly handled by Django ORM and PostgreSQL constraints, preventing SQL injections and XSS attacks.
- Integration with reCAPTCHA v3 when deleting an account, sending feedback, and authenticating (verified on both Frontend and Backend).
- **Cryptographic Webhooks**: Payment confirmations via Stripe are verified using cryptographic signatures before updating subscription records in the database.
- Added comprehensive rate limiting using DRF throttle classes:
    ```python
    class SendOTPThrottle(UserRateThrottle):
        rate = '10/minute'

    class BasicThrottle(UserRateThrottle):
        rate = '15/minute'
    
    class UpdateData(UserRateThrottle):
        rate = '50/minute'
    
    class MainAPiThrottle(UserRateThrottle):
        rate = '30/minute'
    
    class DataScrapingThrottle(UserRateThrottle):
        rate = '40/minute'
    
    class CatalogThrottle(UserRateThrottle):
        rate = '40/minute'

    class GetSortsAndDetailsThrottle(UserRateThrottle):
        rate = '30/minute'

    class ForumThrottling(UserRateThrottle):
        rate = '100/minute'
    ```
  - Applied globally in `settings.py`:
    ```python
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '5000/day',
        'anon': '100/hour',
    }
    ```
- Added `ALLOWED_PATHS` via `api.middleware.APIWhitelistMiddleware`, ensuring DDoS attacks sending fake automated requests are dropped early.
- Blocked access to users with Russian or Belarusian IP addresses using IPinfo in `api.middleware.GeoBlockMiddleware`.

#### All database data is secured by PostgreSQL and Django ORM constraints.

---

## API Documentation
*(Note: Following the DDD architecture, the Presentation layer delegates business logic to the Application layer)*

- **`api/register/`**
  - Creates a new user using `RegisterSerializer`.
  - Validates form data and checks password matches.
  - Creates an auth token for the user and returns a 201 response.
  - Can only be completed after verifying the email via OTP.
  - Throttle class: `BasicThrottle`.
- **`api/login/`**
  - Authenticates user into the platform using `LoginSerializer`.
  - Checks if user exists in the PostgreSQL database.
  - Returns the auth token and a 200 response upon success.
  - Throttle class: `BasicThrottle`.
- **`api/send-otp/`**
  - Sends an HTML context page/code to the user's email.
  - Takes user email in the body.
  - Caches OTP for 10 minutes (TTL) as `otp_{email}`.
  - Used for verifying email during registration, account deletion, or moderator privilege escalation.
  - Throttle class: `SendOTPThrottle`.
- **`api/stripe/webhook/`**
  - Listens for asynchronous payment events from Stripe.
  - Cryptographically verifies the signature using the Stripe webhook secret.
  - Updates the user's `is_premium` status via the Application layer.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/FarmsteadHelper.git
cd farmstead_farmer
```
### 2. Download all packages

```bash
pip install -r requirements.txt
```

### 3. Create the MySQL database and execute all files from Databases branch

### 4. Connect your database in `farmstead_farmer/settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'YOUR-NAME',                      # Name of your database
        'USER': 'YOUR-USER',                      # Name of your user
        'PASSWORD': 'YOURPASS',                   # Password
        'HOST': 'localhost',                      # Parameters of database
        'PORT': '3306',
    },
}
```

### 5. Make migrations

```bash
python manage.py makemigrations
```

After that

```bash
python manage.py migrate
```

### 6. Run server

```bash
python manage.py runserver
```
