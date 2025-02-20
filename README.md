# Django Backend Project

This is the backend service built with Django REST Framework.

## Prerequisites

- Python 3.8 or higher
- MySQL
- Virtual Environment

## Setup Instructions

### 1. Clone the Repository
bash
git clone <repository-url>
cd backend


### 2. Create and Activate Virtual Environment

bash
Windows
python -m venv myenv
myenv\Scripts\activate
Linux/Mac
python3 -m venv myenv
source myenv/bin/activate

### 3. Install Dependencies
bash
pip install -r requirements.txt


### 4. Environment Variables
Create a `.env` file in the backend directory with the following variables:


### 4. Environment Variables
Create a `.env` file in the backend directory with the following variables:

env
DEBUG=True
SECRET_KEY=your-secret-key
DB_ENGINE=django.db.backends.mysql
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306

### 5. Database Setup
bash
Create migrations
python manage.py makemigrations
Apply migrations
python manage.py migrate
Create superuser (Optional)
python manage.py createsuperuser

### 6. Run Development Server
bash
python manage.py runserver
