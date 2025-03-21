# Project 1 - CSCE 608

This repository contains the implementation of a Django-based project for CSCE 608. The project includes data processing, database management, and a web application for managing legislative data.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL
- Django 5.1.7
- pip (Python package manager)

## Setup Instructions

Follow these steps to set up the project:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd project_1
```

### 2. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Configure the Database

Ensure PostgreSQL is running and create a database named `project1`. Update the database credentials in `project_1/settings.py` if necessary:

### 4. Load Initial Data

Use the `load_data.py` script to populate the database with initial data:

```bash
cd data
python load_data.py
```

### 5. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`.

## Project Structure

- `data/`: Contains scripts and CSV files for data processing.
- `project_1/`: Main Django project configuration.
- `templates/`: HTML templates for the web application.
- `utils/`: Utility scripts and modules.