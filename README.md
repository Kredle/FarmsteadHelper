# FarmsteadHelper

**FarmsteadHelper** is a web platform designed for landowners, gardeners and nature enthusiasts. It combines a wiki-like catalog of different sorts of trees, vegetables, flowers and animals, a discussion forum, an interactive yard planner, and a yearly calendar to help users organize their homesteading life.

---

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript (Django Templates)
- **Database**: MySQL
- **Deployment**: WSGI/ASGI
- **API Testing**: Postman
- **Other Tools**: reCAPTCHA, IPinfo

---

## Project Structure

```markdown
farmstead_farmer/
├── animals/                                 # Animals branch for catalog
│ ├── templates/                             # Templates
|  └── animals/
|    ├── animal_detail.html                  # Details of a certain type of animal
|    ├── animal_sorts_list.html              # List of different kinds of certain animal
|    └── animal_list.html                    # List of different types pof animals (parent Animals)
|  ├── models.py                             # Models of data
|  ├── urls.py                               # Urls of APIs
|  └── views.py                              # APIs
├── api/                                     # Authentication and profiles
│ ├── static/                                # Photos for site and JS, CSS code 
│   ├── api/                                 # Styles for pages and JS code for registration and login pages
│   ├── main_page/                           # Photos for site
│   └── profile/                             # Styles for profiles
│ ├── templates/
│   ├── api/
│     ├── confirm-register.html              # Page for confirming registration by entering OTP
│     ├── login.html                         # Login form
│     ├── mainpage.html                      # Main page
│     ├── new_password.html                  # Form for entering new password
│     ├── register.html                      # Registration form
│     └── reset_password.html                # Form for requesting a password reset
│   └── profiles/                            # Profile pages
│     ├── edit_profile.html                  # Setting of profile
│     └── view_profile.html                  # Profile preview
│ ├── templatetags/                          # Template Tags for custom filters and tags used in Django templates
│   └── my_filters.py                        # Custom filter for obtaining objects that match category
│ ├── models.py                              # Models of user and OTP
│ ├── forms.py                               # Form for resetting the password
│ ├── middleware.py                          # APIWhitelistMiddleware that allows only ALLOWED_PATHS to prevent Ddos attacs
│ ├── serializers.py                         # Regestrations and login serializers
│ ├── urls.py                                # Setting urls of APIs
│ └── views.py                               # Profiles and Authentication APIs with trottle_classes to limit rates
├── calendar_/                               # Calendar section
│ ├── templates/
│   └── calendar.html                        # Calendar page
│ ├── models.py                              # Models of dates intervals
│ ├── urls.py                                # Setting urls of APIs
│ └── views.py                               # Getting all sorts of category and getting date intervals for sort APIs
├── catalog/                                 # Catalog section (Covers main catalog page)
│ ├── templates/
│   └── catalog/
│     └── catalog.html                      # Catalog page
│ ├── models.py                             # Tree, Animals, Vegetables, Flowers models + vertions for search bar
│ ├── urls.py                               # Setting urls of APIs
│ └── views.py                              # Search, Generating random sorts and filtrating sorts APIs
├── farmstead_farmer/                       # Setting of web application
│ ├── middleware.py                         # Processing responses and connect them to their error pages
│ ├── urls.py                               # Connecting urls from all apps
│ ├── settings.py                           # Config of web application
│ └── wsgi.py                               # WSGI config
├── feedback/                               # Feedback form 
│ ├── templates/
│   └── feedback/
│     └── feedback_form.html                # Feedback form with reCAPTCHA
│ ├── forms.py                              # Feedback form
│ ├── urls.py                               # Setting url for sending feedback API
│ └── views.py                              # Sending feedback API (Using trottle_class to limit rates and reCAPTCHA verification)
├── forum/                                  # Forum section
| ├── static/                               # Styles and photos for forum pages
│ ├── templates/
│   ├── create_discussion.html              # Create discussin page
│   ├── edit_topic.html                     # Edit topic page
│   ├── forumpage.html                      # Main forum page
│   └── topic_detail.html                   # Topic detaid page, where users can communicate with each other
│ ├── forms.py                              # Discussion Form
│ ├── models.py                             # Topic, Comment, User Models
│ ├── urls.py                               # Setting urls of APIs
│ └── views.py                              # Forum APIs
├── interactive_map/                        # Interactive map sections
│ ├── templates/ 
│   ├── map_canvas.html                     # Page, where users can plot their own land by using a variety of tools
│   └── map_overview.html                   # Page, designed to introduce users to interactive map functionality
│ ├── models.py                             # Map model 
│ ├── urls.py                               # Setting urls of APIs
│ └── views.py                              # Saving, Updating, Checking if user has map and getting map APIs
├── main_page/                              # Main page of site
│ ├── urls.py                               # Setting main page view url 
│ └── views.py                              # Main page view
├── media/                                  # Folder for keeping users' avatars
├── plants/                                 # Plants branch for catalog
│ ├── templates/
|  └── plants/
|    ├── plant_detail.html                  # Page that shows details of certain sort of flower
|    └── plant_list.html                    # Page that shows all sorts of flowers
|  ├── models.py                            # Flower model
|  ├── urls.py                              # Setting urls of APIs
|  ├── views.py                             # Pages views
├── templates/                              # Templates of error pages
│ ├── 400.html                              # Page for 400 response
│ ├── 403.html                              # Page for 403 response
│ ├── 404.html                              # Page for 404 response
│ └── 500.html                              # Page for 500 response
├── trees/                                  # Trees branch for catalog
│ ├── templates/
|  └── trees/ 
|    ├── sort_detail.html                   # Details of certain sort of tree
|    ├── sorts_list.html                    # List of sorts of parent tree
|    └── trees_main_list.html               # List of different types of trees (parents trees)
|  ├── models.py                            # Models of Tree, Sort, Fertilizer, Planting, etc.
|  ├── urls.py                              # Setting urls of views
|  ├── views.py                             # Tree views
├── vegetables/                             # Vegetables branch for catalog
│ ├── templates/
|  └── vegetables/
|    ├── sort_detail.html                   # Details of certain sort of vegetable
|    ├── sort_list.html                     # List of sorts of parent vegetable
|    └── vegetable_list.html                # List of different types of vegetables (parents vegetables)
|  ├── models.py                            # Models of Vegetable, SortVeg, FertilizerVeg, DiseasesVeg.
|  ├── urls.py                              # Setting urls of views
|  ├── views.py                             # Views of vegetables branch
├── asgi.py                                 # ASGI Config
├── wsgi,oy                                 # WSGI Config
├── manage.py                               # Django's command-line utility
└── requirements.txt                        # Dependencies
```
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

## Core Features

### Catalog
A wiki-style reference system for different types of farm-related items:

- Categories: Animals, Trees, Flowers, Vegetables
- Each entry includes images, descriptions, tips, and more
- Users can bookmark varieties ("Add to Favorites") for quick access in their profile
- "Can be intresting for you" section, where users can randomize sorts of different categories
- Includes filter functionality in "Can be intresting for you" section, where users can choose what categories they want to see

---

### Forum
A place for users to share experience and ask questions:

- Discussions organized by category (Trees, Vegetables, Flowers, Animals)
- Users can create threads, reply to topics, and reply to replies
- Favorite discussions can be saved to user profiles
- Users can report topics and comments if they break the rules of the platform (Report will be sent to moderators)
- Moderators can delete topics and comments
- Users can edit their comments and topics
- Sorting discussions by likes count
- Users can filter discussions by keywords, categories or both
- If users' comments get deleted, replies to that comments change "Відповідь на коментар **username**" to "Відповідь на коментар Коментар видалено"
- If user deletes his account, then topic author changes to "Користувача видалено"
- If user changes his name, it automaticaly changes in forum

---

### Interactive Map
An intuitive homestead planner:

- Users can design their yard by:
  - Drawing areas (soil, grass, water)
  - Making rectangular-shaped areas with dot tool
  - Adding trees, vegetables, flowers, and structures
  - Undo (CTRL+Z) and redo (CTRL+SHIFT+Z) buttons 
- Save the layout to their profile and edit later
- If other user visits user's saved map, map sets into preview mode
- Map visibility can be made public or private

---

### Calendar
A visual farming planner:

- Displays a 12-month view
- Tasks/events shown as colored stripes per date
- Users can filter by crop type, season, or activity
- Includes search functionality

---

### User Profile
Every user has a personal dashboard:

- Displays profile picture, name, bio, registration date, last seen
- Lists favorite varieties and favorite discussions
- Link to their saved interactive map

---

### Profile Editing

Users can:
- Edit firstname and lastname, profile photo, and bio (max 150 characters)
- Change username (once every 7 days)
- Change password
- View current email
- Set a new email address
- Delete their account
- Manage privacy settings for:
  - Favorites
  - Interactive map

---


### Security

To protect the platform from cyberattacks were added next things:
- Login and registration verifications by Django ORM (Saves from SQL injections)
- Integration with reCAPTCHA when deleting account, sending feedback and authenticating (Checking on FrontEnd and BackEnd)
- Added rate limiting:
  - By creating trottle classes and using trottle_class decorator
  - By adding DEFAULT_TROTTLE_CLASSES to settings.py
- Added ALLOWED_PATHS, so that DDOS attacks that are sending fake requests wouldn't work
- Blocked access to users with russian or belarusian IP by using IPinfo

#### All database data is secured by Django ORM


---


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
