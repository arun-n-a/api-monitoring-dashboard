#!/bin/bash

# DocHub Local Development Setup Script
# This script will help you set up the DocHub application locally

set -e  # Exit on any error

echo "🚀 DocHub Local Development Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    print_error "Please run this script from the DocHub project root directory"
    exit 1
fi

print_status "Starting local development setup..."

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    if [[ "$PYTHON_VERSION" == "3.12" ]]; then
        print_status "Python 3.12 is installed"
    else
        print_warning "Python $PYTHON_VERSION found. Python 3.12 is recommended."
    fi
else
    print_error "Python 3 is not installed. Please install Python 3.12 first."
    exit 1
fi

# Check if pipenv is installed
print_status "Checking pipenv..."
if ! command -v pipenv &> /dev/null; then
    print_status "Installing pipenv..."
    pip install pipenv
else
    print_status "pipenv is already installed"
fi

# Install dependencies
print_status "Installing project dependencies..."
pipenv install

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp env.example .env
    print_warning "Please edit .env file with your database and Redis settings"
else
    print_status ".env file already exists"
fi

# Check PostgreSQL
print_status "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    print_status "PostgreSQL is installed"
    
    # Check if PostgreSQL service is running
    if sudo systemctl is-active --quiet postgresql; then
        print_status "PostgreSQL service is running"
    else
        print_warning "PostgreSQL service is not running. Starting it..."
        sudo systemctl start postgresql
    fi
else
    print_error "PostgreSQL is not installed. Please install it first:"
    echo "sudo apt update && sudo apt install postgresql postgresql-contrib"
    exit 1
fi

# Check Redis
print_status "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    print_status "Redis is installed"
    
    # Check if Redis service is running
    if sudo systemctl is-active --quiet redis-server; then
        print_status "Redis service is running"
    else
        print_warning "Redis service is not running. Starting it..."
        sudo systemctl start redis-server
    fi
    
    # Test Redis connection
    if redis-cli ping &> /dev/null; then
        print_status "Redis connection test successful"
    else
        print_error "Redis connection test failed"
        exit 1
    fi
else
    print_error "Redis is not installed. Please install it first:"
    echo "sudo apt update && sudo apt install redis-server"
    exit 1
fi

# Activate virtual environment and run migrations
print_status "Setting up database..."
pipenv run alembic revision --autogenerate -m "init" || {
    print_warning "Migration creation failed. This might be normal if no changes detected."
}

pipenv run alembic upgrade head || {
    print_error "Database migration failed. Please check your database connection."
    exit 1
}

# Create admin user
print_status "Creating admin user..."
pipenv run python scripts/create_admin.py || {
    print_warning "Admin user creation failed or user already exists."
}

print_status "Setup completed successfully!"
echo ""
echo "🎉 Your DocHub application is ready for local development!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Run the application: pipenv run uvicorn app.main:app --reload"
echo "3. Access the API docs: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  pipenv shell                    # Activate virtual environment"
echo "  make run                        # Run the application"
echo "  make migrate-upgrade            # Run database migrations"
echo "  make migrate-create MSG='desc'  # Create new migration"
echo ""
echo "Happy coding! 🚀" 