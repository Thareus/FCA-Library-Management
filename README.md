# Library Management System

## Project Overview
A comprehensive Library Management System built with Django (backend) and React (frontend) that allows users to manage books, track borrowing history, and generate reports. The system features user authentication, book management, and automated notifications.

## Key Features
- User authentication and authorization
- Book catalog with search and filtering
- Book borrowing and return system
- Automated notifications for due dates
- Reporting and analytics
- RESTful API for integration

## Technology Stack
- **Backend**: Django 5.2.3, Django REST Framework
- **Frontend**: React, TypeScript, Vite
- **Database**: PostgreSQL (production), SQLite (development)
- **Task Queue**: Celery with Redis
- **Containerization**: Docker

## Prerequisites
- Python 3.10+
- Node.js 16+
- Docker and Docker Compose (optional)
- Redis (for task queue)

## Setup Instructions

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Thareus/FCA-Library-Management
   cd financial_conduct_authority/library
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   # source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Typical environment variables have been included in the docker-compose.yml file:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   REDIS_URL=redis://localhost:6379/0
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. The `.env` file has been included in the frontend directory:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

### Docker Setup

### Prerequisites
- Docker Engine 20.10.0 or later
- Docker Compose 2.0.0 or later

### Available Services
- **backend**: Django application
- **frontend**: React development server
- **redis**: Redis cache and message broker
- **db**: PostgreSQL database (production)

### Building and Running with Docker

1. **Build all services**:
   ```bash
   docker-compose build
   ```

2. **Start all services in detached mode**:
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

4. **Create a superuser (admin)**:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **View running containers**:
   ```bash
   docker-compose ps
   ```

6. **View logs for a specific service**:
   ```bash
   # View backend logs
   docker-compose logs -f backend
   
   # View frontend logs
   docker-compose logs -f frontend
   ```

7. **Stop all services**:
   ```bash
   docker-compose down
   ```

### Development Mode
For development with hot-reloading:

1. **Start services in development mode**:
   ```bash
   # Set Django to development mode
   export DJANGO_DEBUG=True
   
   # Start services
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
   ```

2. **Run tests**:
   ```bash
   docker-compose exec backend python manage.py test
   ```

### Production Deployment
For production, use the production compose file:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Environment Variables
Key environment variables can be set in `.env` file in the project root:

```
# Django
DJANGO_DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=library
POSTGRES_USER=library_user
POSTGRES_PASSWORD=library_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
```

### Volumes
- Database data is persisted in `postgres_data` volume
- Redis data is persisted in `redis_data` volume
- Frontend node_modules are cached in `node_modules` volume

## Running the Application
1. Start the backend server:
   ```bash
   cd library
   python manage.py runserver
   ```

2. In a new terminal, start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Access the application at `http://localhost:5173`
4. Access the Django admin at `http://localhost:8000/admin/`

## Testing
Run the test suite with:
```bash
python manage.py test
```

## Project Structure
```
financial_conduct_authority/
├── library/                  # Django project
│   ├── books/                # Books app
│   ├── users/                # Custom user model and auth
│   ├── manage.py
│   └── requirements.txt
├── frontend/                 # React frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── docker/                   # Docker configuration
    ├── backend/
    └── frontend/
```

## Configuration
- Backend settings: `library/library/settings.py`
- Frontend environment: `frontend/.env`
- Database configuration: `DATABASE_URL` may be adjusted in `.env`