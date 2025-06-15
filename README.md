# Innovate - Learning Management System

A comprehensive Learning Management System (LMS) platform designed for universities and schools, built with Django backend and Next.js frontend.

## Features

### User Management

- Multi-role system (Institution, Teacher, Student)
- Institution registration and management
- Bulk user import via CSV
- User profile management
- Role-based access control

### Course Management

- Course creation and management
- Chapter organization
- Lecture content management
- Course enrollment system
- Course analytics and tracking

### Assessment System

- Multiple assessment types:
  - Multiple Choice Questions (MCQ)
  - Handwritten Questions
  - Dynamic MCQs
- Assessment submission tracking
- Automated grading for MCQs
- Manual grading for handwritten submissions
- Assessment analytics and reporting

### AI Integration

- AI-powered features for enhanced learning
- Integration with Hugging Face models
- PDF processing capabilities

### Analytics

- Comprehensive analytics dashboard
- Student performance tracking
- Course progress monitoring
- Assessment analytics

## Technical Stack

### Backend

- Django & Django REST Framework
- PostgreSQL Database
- Celery for async tasks
- Channels for WebSocket support
- JWT Authentication
- Redis for caching

#### Key Backend Dependencies

- djangorestframework
- django-cors-headers
- djangorestframework-simplejwt
- django-filter
- channels & channels-redis
- celery & django_celery_beat
- huggingface-hub
- PyPDF2 & pdf2image

### Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Shadcn UI Components
- TanStack Query & Table
- Socket.io for real-time features

#### Key Frontend Dependencies

- @tanstack/react-query & @tanstack/react-table
- @radix-ui/react-\* (UI components)
- recharts (Data visualization)
- zod (Schema validation)
- zustand (State management)

## Prerequisites

- Python 3.x
- Node.js 18+
- PostgreSQL
- Redis
- Docker (optional)

## Project Structure

### Backend Structure

```
├── AI/                    # AI integration components
├── analytics/            # Analytics and reporting
├── assessment/          # Assessment management
├── AssessmentSubmission/ # Assessment submission handling
├── chapter/             # Course chapter management
├── courses/             # Course management
├── DynamicMCQ/          # Dynamic MCQ functionality
├── enrollments/         # Course enrollment system
├── HandwrittenQuestion/ # Handwritten question handling
├── institution/         # Institution management
├── lecture/            # Lecture content management
├── mcqQuestion/        # MCQ question management
├── users/              # User management
└── main/               # Core application settings
```

### Frontend Structure

```
├── app/                # Next.js app directory
│   ├── (root)/        # Root layout and pages
│   ├── institution/   # Institution-specific pages
│   ├── teacher/       # Teacher-specific pages
│   └── student/       # Student-specific pages
├── components/        # Reusable UI components
├── apiService/       # API service functions
├── hooks/           # Custom React hooks
├── context/         # React context providers
├── types/           # TypeScript type definitions
├── lib/             # Utility functions
├── store/           # State management
└── public/          # Static assets
```

## Setup and Installation

### Backend Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Create a `.env` file with required configurations
   - Include database credentials, secret key, and other necessary settings
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
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables:
   - Create a `.env.local` file with required configurations
   - Include API endpoints and other necessary settings
4. Start the development server:
   ```bash
   npm run dev
   ```

### Docker Deployment

1. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

## API Documentation

The API documentation is available at `/api/schema/swagger-ui/` when running the server.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
