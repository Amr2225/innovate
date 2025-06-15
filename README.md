# Innovate - Learning Management System

A comprehensive learning management system built with Django and Next.js, featuring AI-powered assessment and analytics.

## Features

- **User Management**

  - Multi-role system (Student, Teacher, Institution Admin)
  - Secure authentication and authorization
  - Profile management with avatar support

- **Course Management**

  - Course creation and management
  - Prerequisite course system
  - Course materials and curriculum
  - Student enrollment tracking

- **Assessment System**

  - AI-powered assessment generation
  - Multiple question types
  - Automated grading
  - Performance analytics

- **AI Integration**

  - Smart assessment generation
  - Performance predictions
  - Learning path recommendations

- **Analytics**
  - Student performance tracking
  - Course analytics
  - Progress monitoring
  - Custom reports

## Technical Stack

### Backend

- Django 5.0
- Django REST Framework
- PostgreSQL
- Celery for async tasks
- Redis for caching
- JWT Authentication
- OpenAI API integration

### Frontend

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Shadcn UI
- TanStack Query
- React Hook Form
- Zod validation

## Key Dependencies

### Backend

- Django 5.0
- Django REST Framework
- Celery
- Redis
- PostgreSQL
- OpenAI
- JWT
- Django CORS Headers

### Frontend

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Shadcn UI
- TanStack Query
- React Hook Form
- Zod
- Axios
- Moment.js

## Project Structure

### Backend

```
backend/
├── core/                 # Core Django settings
├── users/               # User management
├── courses/             # Course management
├── assessments/         # Assessment system
├── analytics/           # Analytics and reporting
└── utils/              # Utility functions
```

### Frontend

```
frontend/
├── app/                # Next.js app directory
├── components/         # Reusable components
├── apiService/         # API integration
├── hooks/             # Custom React hooks
├── types/             # TypeScript types
└── utils/             # Utility functions
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL
- Redis
- Git

### Backend Setup

1. Clone the repository and navigate to the backend directory:

   ```bash
   git clone https://github.com/your-username/innovate.git
   cd innovate/backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

   Configure the following variables in `.env`:

   ```env
   # Django Settings
   DEBUG=True
   SECRET_KEY=your-secret-key
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database
   DB_NAME=innovate_db
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432

   # Redis
   REDIS_URL=redis://localhost:6379

   # OpenAI
   OPENAI_API_KEY=your-openai-api-key

   # JWT
   JWT_SECRET_KEY=your-jwt-secret
   JWT_ACCESS_TOKEN_LIFETIME=5
   JWT_REFRESH_TOKEN_LIFETIME=1

   # Email
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

5. Run migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
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

3. Set up environment variables:

   ```bash
   cp .env.example .env.local
   ```

   Configure the following variables in `.env.local`:

   ```env
   # API Configuration
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   NEXT_PUBLIC_API_VERSION=v1

   # Authentication
   NEXT_PUBLIC_JWT_SECRET=your-jwt-secret

   # Feature Flags
   NEXT_PUBLIC_ENABLE_ANALYTICS=true
   NEXT_PUBLIC_ENABLE_AI_ASSESSMENTS=true
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

### Docker Deployment

#### Backend

```bash
docker build -t innovate-backend .
docker run -p 8000:8000 innovate-backend
```

#### Frontend

```bash
docker build -t innovate-frontend .
docker run -p 3000:3000 innovate-frontend
```

## API Documentation

API documentation is available at `/api/docs/` when running the backend server.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
