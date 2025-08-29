# Django Authentication System

user authentication service built with Django, PostgreSQL, Redis, and JWT authentication for Bill Station's fintech platform.

## 🚀 Live Demo

**Deployment URL:** [Your Railway/Render deployment link here]

**API Documentation:** [Your deployment URL]/

## 📋 Features

- **User Registration** - Create new accounts with email and full name
- **JWT Authentication** - Secure token-based authentication
- **Password Reset** - Forgot password functionality with Redis caching
- **Rate Limiting** - Protection against brute force attacks
- **PostgreSQL Integration** - Robust database management
- **Redis Caching** - Fast token storage and retrieval
- **API Documentation** - Interactive Swagger/OpenAPI docs
- **Docker Support** - Containerized development environment
- **Comprehensive Testing** - Unit tests for all endpoints

## 🛠️ Technology Stack

- **Backend:** Django 4.2, Django REST Framework
- **Database:** PostgreSQL
- **Cache:** Redis
- **Authentication:** JWT (Simple JWT)
- **Documentation:** drf-yasg (Swagger/OpenAPI)
- **Deployment:** Railway/Render
- **Containerization:** Docker & Docker Compose

## 📦 Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd auth_service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```


5. **Database setup**
   ```bash
   # Create PostgreSQL database
   createdb auth_service
   
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Docker Development

1. **Using Docker Compose**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Run migrations
   docker-compose exec web python manage.py migrate
   
   # Create superuser (optional)
   docker-compose exec web python manage.py createsuperuser
   ```

2. **Access the application**
   - API: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000

### Example Production Environment Variables

```env
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,yourdomain.com
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://default:password@host:port
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 📖 API Documentation

### Base URL
- **Local:** `http://localhost:8000/api/auth/`
- **Production:** `https://your-app.railway.app/api/auth/`

### Endpoints

#### 1. User Registration
- **URL:** `POST /api/auth/register/`
- **Description:** Register a new user account
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }
  ```
- **Response:**
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "tokens": {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
  ```

#### 2. User Login
- **URL:** `POST /api/auth/login/`
- **Description:** Authenticate user and get JWT tokens
- **Rate Limit:** 5 requests per minute per IP
- **Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Login successful",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "tokens": {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
  ```

#### 3. Forgot Password
- **URL:** `POST /api/auth/forgot-password/`
- **Description:** Request password reset token
- **Rate Limit:** 3 requests per minute per IP
- **Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Password reset token sent to your email"
  }
  ```

#### 4. Reset Password
- **URL:** `POST /api/auth/reset-password/`
- **Description:** Reset password using token
- **Body:**
  ```json
  {
    "token": "abc123def456ghi789",
    "new_password": "newsecurepassword123",
    "new_password_confirm": "newsecurepassword123"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Password reset successful"
  }
  ```

#### 5. User Profile
- **URL:** `GET /api/auth/profile/`
- **Description:** Get authenticated user profile
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "date_joined": "2024-01-15T10:30:00Z"
  }
  ```

#### 6. Logout
- **URL:** `POST /api/auth/logout/`
- **Description:** Logout user
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  {
    "message": "Logout successful"
  }
  ```

### Authentication

All protected endpoints require a JWT access token in the Authorization header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Token Expiry

- **Access Token:** 1 hour
- **Refresh Token:** 7 days
- **Password Reset Token:** 10 minutes (stored in Redis)

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test accounts.tests

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Coverage
- User registration (success, validation, duplicates)
- User login (success, invalid credentials)
- Password reset (token generation, validation)
- Redis token storage and retrieval

## 🔒 Security Features

- **JWT Authentication** - Secure token-based authentication
- **Password Validation** - Django's built-in password validators
- **Rate Limiting** - Protection against brute force attacks
- **Token Expiry** - Short-lived access tokens with refresh mechanism
- **Secure Headers** - Security middleware enabled
- **Email Enumeration Protection** - Consistent responses for forgot password

## 📝 API Usage Examples

### Using cURL

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'




## 🧪 Testing Guide

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test accounts.tests.UserRegistrationTestCase

# Run with verbose output
python manage.py test --verbosity=2

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```
