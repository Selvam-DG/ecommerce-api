# E-Commerce API Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive, production-ready REST API for e-commerce operations built with Django REST Framework and PostgreSQL. This project demonstrates complete software development lifecycle (SDLC) practices from planning through deployment.

---

##  Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

##  Overview

This E-Commerce API provides a complete backend solution for modern e-commerce platforms. Built following agile methodologies and industry best practices, it serves as both a functional application and a comprehensive learning project demonstrating professional software development processes.

### Project Goals
-  Build a production-grade e-commerce API
-  Document complete SDLC from conception to deployment
-  Implement industry-standard development practices
-  Create a scalable, maintainable codebase
-  Develop a portfolio-ready project

### Current Status
**Phase:** Development  
**Version:** 0.1.0 (MVP in progress)  
**Sprint:** Sprint X of 7  
**Completion:** XX% of MVP features

---

##  Features

### Core Functionality

####  User Management
- User registration with email verification
- JWT-based authentication
- Role-based access control (Customer, Vendor, Admin)
- Profile management
- Password reset functionality
- Social authentication (planned)

####  Product Catalog
- Complete CRUD operations for products
- Category and tag hierarchies
- Advanced search and filtering
- Product image management
- Inventory tracking
- Stock alerts
- Variants support (planned)

####  Shopping Cart
- Add/update/remove cart items
- Persistent cart for authenticated users
- Session-based cart for guest users
- Real-time price calculations
- Discount and coupon support
- Stock validation

#### Order Management
- Streamlined checkout process
- Order creation and validation
- Order status tracking workflow
- Order history and details
- Address management
- Shipping options
- Order cancellation and returns

####  Payment Processing
- Stripe integration
- PayPal integration (planned)
- Secure payment processing
- Webhook handling for confirmations
- Refund processing
- Payment history and receipts

####  Reviews & Ratings
- Product reviews and ratings
- Review moderation system
- Helpful/report functionality
- Verified purchase badges
- Response system for vendors

####  Admin Dashboard
- Comprehensive analytics
- User management
- Product approval workflow
- Order management
- Sales reports
- System monitoring

---

## Tech Stack

### Backend
- **Framework:** Django 5.0+
- **API:** Django REST Framework 3.14+
- **Database:** PostgreSQL 15+
- **Authentication:** djangorestframework-simplejwt
- **Task Queue:** Celery (planned)
- **Caching:** Redis (planned)

### DevOps & Tools
- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions
- **Containerization:** Docker + Docker Compose
- **API Docs:** drf-spectacular (Swagger/OpenAPI)
- **Testing:** pytest, pytest-django, factory_boy
- **Code Quality:** black, flake8, pylint, isort, pre-commit

### Third-Party Integrations
- **Payment:** Stripe API
- **Email:** SendGrid / Django SMTP
- **Storage:** AWS S3 / Local storage
- **Monitoring:** Sentry (planned)

---

##  Project Structure

```
ecommerce-api/
│
├── docs/                          # All project documentation
│   ├── 01-planning/              # Proposal, requirements, analysis
│   ├── 02-design/                # Architecture, API design, database
│   ├── 03-development/           # Setup guides, coding standards
│   ├── 04-sprint-planning/       # Backlogs, sprint docs
│   ├── 05-testing/               # Test plans, test cases
│   ├── 06-deployment/            # Deployment guides
│   └── 07-api-documentation/     # API reference docs
│
├── src/                          # Source code
│   ├── config/                   # Project configuration
│   │   ├── settings/             # Environment-specific settings
│   │   ├── urls.py               # Root URL configuration
│   │   └── wsgi.py               # WSGI configuration
│   │
│   ├── apps/                     # Django applications
│   │   ├── users/                # User management
│   │   ├── products/             # Product catalog
│   │   ├── cart/                 # Shopping cart
│   │   ├── orders/               # Order management
│   │   ├── payments/             # Payment processing
│   │   ├── reviews/              # Reviews and ratings
│   │   └── core/                 # Shared utilities
│   │
│   ├── tests/                    # Test files
│   │   ├── unit/                 # Unit tests
│   │   ├── integration/          # Integration tests
│   │   └── e2e/                  # End-to-end tests
│   │
│   └── manage.py                 # Django management script
│
├── .github/                      # GitHub specific files
│   ├── workflows/                # CI/CD pipelines
│   ├── ISSUE_TEMPLATE/           # Issue templates
│   └── PULL_REQUEST_TEMPLATE.md  # PR template
│
├── docker/                       # Docker configuration
│   ├── Dockerfile                # Application container
│   ├── docker-compose.yml        # Multi-container setup
│   └── postgres/                 # PostgreSQL setup
│
├── scripts/                      # Utility scripts
│   ├── setup.sh                  # Initial setup script
│   ├── test.sh                   # Testing script
│   └── deploy.sh                 # Deployment script
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── .pre-commit-config.yaml       # Pre-commit hooks
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── pytest.ini                    # Pytest configuration
├── setup.cfg                     # Tool configurations
├── README.md                     # This file
├── LICENSE                       # MIT License
├── CONTRIBUTING.md               # Contribution guidelines
└── CHANGELOG.md                  # Version history
```

---

## Getting Started

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 15 or higher
- Git
- pip and virtualenv
- (Optional) Docker and Docker Compose

### Installation

#### Option 1: Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/Selvam-DG/ecommerce-api.git
cd ecommerce-api
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

4. **Set up environment variables**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Set database credentials, secret key, etc.
```

5. **Set up PostgreSQL database**
```bash
# Create database
createdb ecommerce_db

# Or using psql
psql -U postgres
CREATE DATABASE ecommerce_db;
```

6. **Run migrations**
```bash
python src/manage.py migrate
```

7. **Create superuser**
```bash
python src/manage.py createsuperuser
```

8. **Load sample data (optional)**
```bash
python src/manage.py loaddata sample_data
```

9. **Run development server**
```bash
python src/manage.py runserver
```

The API will be available at `http://localhost:8000/`

#### Option 2: Docker Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ecommerce-api.git
cd ecommerce-api
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env as needed
```

3. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

4. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

5. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

The API will be available at `http://localhost:8000/`

---

## Documentation

### Project Documentation
All project documentation is organized in the `/docs` folder:

- **[Project Proposal](docs/01-planning/project-proposal.md)** - Project overview and goals
- **[Requirements Document](docs/01-planning/requirements.md)** - Detailed requirements (coming soon)
- **[System Architecture](docs/02-design/system-architecture.md)** - Architecture design (coming soon)
- **[API Design](docs/02-design/api-design.md)** - API specifications (coming soon)
- **[Database Schema](docs/02-design/database-design.md)** - Database design (coming soon)
- **[Setup Guide](docs/03-development/setup-guide.md)** - Development setup (coming soon)
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

### API Documentation
- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

### Development Documentation
- [Coding Standards](docs/03-development/coding-standards.md) (coming soon)
- [Git Workflow](docs/03-development/git-workflow.md) (coming soon)
- [Testing Guide](docs/05-testing/test-strategy.md) (coming soon)

---

##  Development

### Development Workflow

1. **Create a new branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Follow coding standards
   - Write tests for new features
   - Update documentation

3. **Run tests**
```bash
pytest
```

4. **Run linting and formatting**
```bash
black .
flake8 .
isort .
```

5. **Commit your changes**
```bash
git add .
git commit -m "feat: add your feature description"
```

6. **Push to your branch**
```bash
git push origin feature/your-feature-name
```

7. **Create a Pull Request**

### Commit Message Convention
We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Build process or auxiliary tool changes

### Code Style
- Follow PEP 8
- Use type hints where applicable
- Maximum line length: 88 characters (Black default)
- Use meaningful variable and function names
- Add docstrings for classes and functions

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_users.py

# Run tests with specific marker
pytest -m "unit"
```

### Test Categories
- **Unit Tests:** Test individual functions and methods
- **Integration Tests:** Test API endpoints and workflows
- **E2E Tests:** Test complete user scenarios

### Coverage Goals
- Minimum: 80% overall coverage
- Target: 90% coverage
- Critical paths: 100% coverage

---

## Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure allowed hosts
- [ ] Set up environment variables
- [ ] Configure PostgreSQL
- [ ] Set up static file serving
- [ ] Configure CORS settings
- [ ] Set up SSL/HTTPS
- [ ] Configure email backend
- [ ] Set up error tracking (Sentry)
- [ ] Run security checks
- [ ] Set up monitoring

### Deployment Platforms
- [Heroku Deployment Guide](docs/06-deployment/heroku.md) (coming soon)
- [DigitalOcean Deployment Guide](docs/06-deployment/digitalocean.md) (coming soon)
- [AWS Deployment Guide](docs/06-deployment/aws.md) (coming soon)

---

## API Documentation

### Authentication
```bash
# Register a new user
POST /api/v1/auth/register/

# Login
POST /api/v1/auth/login/

# Refresh token
POST /api/v1/auth/token/refresh/
```

### Products
```bash
# List all products
GET /api/v1/products/

# Get product detail
GET /api/v1/products/{id}/

# Create product (admin/vendor)
POST /api/v1/products/

# Update product
PUT /api/v1/products/{id}/

# Delete product
DELETE /api/v1/products/{id}/
```

For complete API documentation, visit the [Swagger UI](http://localhost:8000/api/docs/) when running the server.

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### How to Contribute
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

### Areas for Contribution
- Bug fixes
- New features
- Documentation improvements
- Test coverage
- Performance optimizations

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

##  Contact

**Selvam-DG**  
- GitHub: [@Selvam-DG](https://github.com/Selvam-DG)
- Email: dasariselvam321@gmail.com
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/selvamdasari55)

**Project Link:** [https://github.com/Selvam-DG/ecommerce-api](https://github.com/yourusername/ecommerce-api)

---

## Acknowledgments

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Real Python](https://realpython.com/)
- Open source community

---

##  Project Status

### Current Sprint: Sprint X
**Start Date:** [Date]  
**End Date:** [Date]  

**Sprint Goals:**
- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

**Progress:** XX/YY story points completed

### Roadmap
- [x] Phase 1: Planning & Documentation
- [ ] Phase 2: User Management (In Progress)
- [ ] Phase 3: Product Catalog
- [ ] Phase 4: Shopping Cart
- [ ] Phase 5: Order Management
- [ ] Phase 6: Payment Integration
- [ ] Phase 7: Reviews & Admin Features
- [ ] Phase 8: Testing & Deployment

---

##  Related Repositories

- [Frontend Application](https://github.com/yourusername/ecommerce-frontend) (coming soon)
- [Mobile App](https://github.com/yourusername/ecommerce-mobile) (planned)

---

<div align="center">

**[⬆ Back to Top](#-e-commerce-api-platform)**

Made  by Selvam-DG

</div>