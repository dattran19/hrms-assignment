# HRMS Assignment

A Human Resource Management System built with Django.

## Description

This project is an HRMS (Human Resource Management System) application designed to manage employee information, attendance, leave requests, and other HR-related functionalities.

## Features

- Employee Management
- Attendance Tracking
- Leave Management
- Department Management
- User Authentication & Authorization

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- virtualenv (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hrms-assignment
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   Create a `.env` file in the project root and add:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=sqlite:///db.sqlite3
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## Project Structure

```
hrms-assignment/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── [app directories]
```

## Usage

1. Access the admin panel at `http://127.0.0.1:8000/admin/`
2. Log in with your superuser credentials
3. Start managing employees, departments, and other HR data

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## Technologies Used

- **Backend Framework**: Django
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Django Authentication System
- **Frontend**: Django Templates / HTML/CSS/JavaScript

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is created for educational purposes as part of an assignment.

## Contact

For any questions or concerns, please contact the project maintainer.

## Acknowledgments

- Django Documentation
- Django Community
