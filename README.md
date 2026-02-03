# Secure Notes API

This project was developed for the course  
**Security of Web Applications**.

The purpose of this application is to demonstrate correct implementation of core web security mechanisms such as authentication, authorization, and user data isolation.

---

## 📐 Architecture

- Framework: Flask  
- Database: SQLite  
- ORM: SQLAlchemy  
- Migrations: Flask-Migrate  
- Authentication: JWT (Access Token + Refresh Token)  
- Testing: Pytest  

Main entities:
- User  
- Note  

Layered structure:
Routes → Services → Models  

---

## 🔐 Implemented Security Features

- Password hashing (bcrypt)  
- JWT authentication with refresh tokens  
- Token expiration and rotation  
- Role-based access control  
- User data isolation (users cannot access other users’ data)  
- Input validation and safe error handling  
- HTTP security headers  
- Logging of security-related events  
- No sensitive data in logs  
- No secrets committed to the repository  

---

## ⚙️ Installation

Create a virtual environment and install dependencies:

```bash
python -m venv venv
pip install -r requirements.txt

  🗄 Database Migration

Run database migrations:

flask db upgrade

▶️ Run Application

Start the application with:

python manage.py


The application will be available at:

http://127.0.0.1:5000

🧪 Run Tests

Run all tests using:

pytest


All tests should pass successfully.

Tests include:

Authentication tests

Authorization tests

User isolation test

Integration tests for protected endpoints

⚠️ Important Notes

The .env file is not included in the repository for security reasons.

The database file is not included.

Secrets are loaded from environment variables.

This project is intended for educational purposes only.


        ## Bonus

  - GitHub Actions CI pipeline (tests run automatically on every push)
  - Dependency vulnerability scan using pip-audit



👤 Author

Muhammed Can Ozkesemen
Security of Web Applications – Lab Project

