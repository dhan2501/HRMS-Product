# 🏢 DJ HRMS — Human Resource Management System


---

## 📌 Overview

**DJ HRMS** is a comprehensive Human Resource Management System designed to streamline HR operations for modern organizations. Built with Django on the backend and Tailwind CSS for a clean, responsive UI — it provides everything from employee onboarding to payroll management, all in one platform.

> 🚀 **Custom Dashboard** — No default Django admin UI. Fully custom-built interface with a professional sidebar layout.

---

## ✨ Features

### 👥 Employee Management
- Add, edit, and manage employee profiles with photo upload
- Department & Designation management with seniority levels
- Filter employees by department, status, and employment type
- Emergency contact and address management

### ⏰ Attendance Tracking
- Daily attendance marking with check-in / check-out times
- Status types: Present, Absent, Late, WFH, Half Day, Holiday
- Bulk attendance marking for entire teams
- Monthly attendance calendar view with color-coded status
- Attendance reports and summaries

### 🏖️ Leave Management
- Multiple leave types (Casual, Sick, Earned, etc.)
- Leave request submission and approval workflow
- Leave balance tracking per employee per year
- Carry-forward configuration per leave type

### 💰 Payroll
- Salary structure management (Basic, HRA, Allowances)
- Automatic gross & net salary calculation
- Monthly payslip generation with LOP (Loss of Pay)
- PF, Professional Tax, and TDS deductions

### 🤝 Recruitment
- Job opening management with vacancies and deadlines
- Candidate pipeline: Applied → Screening → Interview → Offer → Hired
- Interview scheduling with feedback and ratings
- Multi-round interview tracking

### 🔐 Roles & Permissions
- Role-based access control
- Company settings configuration
- Secure login with session management

### 🌐 REST API Ready
- Full REST API built with Django REST Framework
- Token-based authentication
- Pagination, filtering, and search on all endpoints
- CORS configured for React/mobile app integration

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, Django 5.0 |
| **REST API** | Django REST Framework |
| **Frontend** | Tailwind CSS (CDN), Vanilla JS |
| **Icons** | Font Awesome 6 |
| **Fonts** | Inter (Google Fonts) |
| **Database** | SQLite (dev) / MySQL / PostgreSQL (prod) |
| **Auth** | Django Auth + Token Auth (DRF) |
| **Media** | Pillow (image handling) |

---

## 📁 Project Structure

```
hrms_project/
│
├── hrms/                    # Project config (settings, urls)
├── employees/               # Employee, Department, Designation
├── attendance/              # Daily & Monthly Attendance
├── leaves/                  # Leave Requests & Balances
├── payroll/                 # Salary Structure & Payslips
├── recruitment/             # Jobs, Candidates, Interviews
│
├── templates/
│   ├── base.html            # Master layout with sidebar
│   ├── dashboard/           # Custom dashboard
│   ├── employees/           # Employee pages
│   ├── attendance/          # Attendance pages
│   ├── leaves/              # Leave pages
│   ├── payroll/             # Payroll pages
│   └── recruitment/         # Recruitment pages
│
├── static/                  # CSS, JS assets
├── media/                   # Uploaded files
└── manage.py
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- pip
- Git

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/dhan2501/dj-hrms.git
cd dj-hrms

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## 📦 Requirements

```txt
django>=5.0
djangorestframework
django-cors-headers
django-filter
pillow
```

Install all:
```bash
pip install -r requirements.txt
```

---

## 🌐 REST API

Base URL: `http://127.0.0.1:8000/api/v1/`

### Authentication
```bash
# Get token
POST /api/v1/auth/token/
Body: { "username": "admin", "password": "password" }

# Use token in headers
Authorization: Token <your_token>
```

### Endpoints

| Module | Endpoint | Methods |
|--------|----------|---------|
| Employees | `/api/v1/employees/` | GET, POST, PUT, DELETE |
| Departments | `/api/v1/departments/` | GET, POST, PUT, DELETE |
| Designations | `/api/v1/designations/` | GET, POST, PUT, DELETE |
| Attendance | `/api/v1/attendance/` | GET, POST, PUT |
| Leave Types | `/api/v1/leave-types/` | GET, POST |
| Leave Requests | `/api/v1/leave-requests/` | GET, POST, PUT |
| Salary Structure | `/api/v1/salary-structures/` | GET, POST, PUT |
| Payslips | `/api/v1/payslips/` | GET, POST |
| Job Openings | `/api/v1/job-openings/` | GET, POST, PUT |
| Candidates | `/api/v1/candidates/` | GET, POST, PUT |
| Interviews | `/api/v1/interviews/` | GET, POST, PUT |

### Custom Actions
```bash
# Approve leave request
POST /api/v1/leave-requests/{id}/approve/

# Reject leave request  
POST /api/v1/leave-requests/{id}/reject/
Body: { "reason": "Insufficient leave balance" }

# Employee attendance summary
GET /api/v1/employees/{id}/attendance_summary/?month=7&year=2026

# Active employees only
GET /api/v1/employees/active/
```

---

## 🗄️ Database Configuration

### SQLite (Development — Default)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### MySQL (Production)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hrms_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

```bash
pip install mysqlclient
mysql -u root -p -e "CREATE DATABASE hrms_db CHARACTER SET utf8mb4;"
```

---

## 🚀 Production Deployment

```python
# settings.py
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = ['yourdomain.com']
```

```bash
pip install gunicorn whitenoise
python manage.py collectstatic
gunicorn hrms.wsgi:application --bind 0.0.0.0:8000
```

---

## 📸 Screenshots

| Dashboard | Employee List |
|-----------|--------------|
| ![Dashboard](DJ%20HRMS.png) | *Employee management with filters* |

---

## 🗺️ Roadmap

- [x] Employee Management (CRUD)
- [x] Department & Designation Management
- [x] Daily Attendance Marking
- [x] Monthly Attendance View
- [x] REST API with DRF
- [ ] Leave Management UI
- [ ] Payroll Generation
- [ ] Recruitment Pipeline UI
- [ ] Email Notifications
- [ ] Export to Excel / PDF
- [ ] React.js Frontend (SPA)
- [ ] Docker Support
- [ ] CI/CD Pipeline

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

---

## 👨‍💻 Author

**Dhananjay Gupta**

[![GitHub](https://img.shields.io/badge/GitHub-dhan2501-181717?style=flat&logo=github)](https://github.com/dhan2501)

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

---

<div align="center">

Made with ❤️ using Django & Tailwind CSS

⭐ **Star this repo if you find it helpful!**

</div>
