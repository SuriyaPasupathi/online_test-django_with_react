# Project Overview

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   - Create a `.env` file in the backend directory with the following variables:
     ```
     DEBUG=True
     SECRET_KEY=your-secret-key
     DB_NAME=your_database_name
     DB_USER=your_database_user
     DB_PASSWORD=your_database_password
     DB_HOST=localhost
     DB_PORT=3306
     ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Run the Server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

- Use Swagger or Postman for API documentation.

## Testing

- Run tests using:
  ```bash
  python manage.py test
  ```

## Deployment

- Ensure static files are configured for production.
- Use a production-ready database setup.
