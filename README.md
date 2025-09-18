# Project_HRMS
A full-featured Human Resource Management System (HRMS) built with Django. Includes employee, attendance, leave, timesheet, resignation, holiday, job, assets, and admin modules with role-based access and SmartHR-inspired UI.



Perfect ✅ I found multiple **apps and templates** in your HRMS project. Based on the folder names and templates, I can refine the README to list each **module** and its **features**.

Here’s the **updated README.md** draft for GitHub:

---

# 🏢 HRMS (Human Resource Management System)

A **full-featured Human Resource Management System** (HRMS) built with **Django**, **Bootstrap**, and **MySQL**.
This project provides a modern, responsive, and role-based HR management platform suitable for companies to manage employees, attendance, payroll, leaves, jobs, and more.

---
## 🛠 Tech Stack
- **Backend:** Django, Django Channels, Python 
- **Frontend:** HTML, Bootstrap, SmartHR-inspired UI  
- **Database:** MySQL (configurable) / XAMPP Server
- **Realtime:** WebRTC, Redis  
- **Integrations:** Calendarific API, Google Maps (location capture)
  
## 🚀 Features by Module

# 🔐 Accounts

* Login & signup (admin and jobseeker)
* Company profile setup
* Manage company details

# 🏢 Department & Designation

* Add, edit, delete departments
* Manage designations linked to departments

# 👥 Employee

* Employee list with search & filter
* Complete profile setup
* Profile detail & update forms
* Education history (UG, PG, Diploma, PUC)

# 💼 Jobs & Jobseeker

* Admin can create, edit, and manage jobs
* Job seekers can:

  * View jobs
  * Apply for jobs
  * Track application status
  * Save jobs
  * Manage profile (combined & readonly views)

# 🕒 Attendance

* Employee attendance marking
* Admin attendance matrix
* Reports with filters

# 📅 Leave

* Apply for leave
* Approve/reject requests
* Assign leave types

# 💰 Payroll

* Salary management
* Admin timesheet integration

# 🗂️ Assets

* Add, edit, delete assets
* Filter assets by type

### 📊 Performance

* Performance review module (KPIs, scores)

# 🕑 Overtime

* Overtime request and approval workflow

# 🎟️ Tickets

* Employees can raise tickets
* Auto-generated, clickable ticket IDs
* Track status and resolution

# 📢 Notifications

* Role-based notifications across modules
* Unified dashboard

# 📦 Subscription & Packages

* Superadmin defines subscription packages (plan type, users, storage, etc.)
* Companies subscribe and manage their plans

### 🗓️ Calendar & Holidays

* Company calendar view
* Public holiday integration

---

# 🛠️ Tech Stack

* **Backend**: Django 4.2, Python 3.x
* **Frontend**: Bootstrap 5, jQuery, HTML5, CSS3
* **Database**: MySQL
* **Other**: Django ORM, Role-based Access Control

---

## ⚙️ Installation & Setup

# 1. Clone Repository

git clone https://github.com/your-username/HRMS.git
cd HRMS


# 2. Create Virtual Environment

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows


# 3. Install Dependencies

pip install -r requirements.txt


# 4. Configure Database

Update **`settings.py`** with your MySQL credentials:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hrms_db',
        'USER': 'root',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

# 5. Run Migrations

python manage.py makemigrations
python manage.py migrate


# 6. Create Superuser

python manage.py createsuperuser


# 7. Run Development Server

python manage.py runserver


Visit 👉 `http://127.0.0.1:8000`

---

## 📂 Project Structure

```
HRMS/
│── manage.py
│── requirements.txt
│── .gitignore
│
├── accounts/         # Authentication & company profiles
├── department/       # Department management
├── designation/      # Designation management
├── employee/         # Employee profiles & education
├── jobs/             # Job posting & management
├── jobseeker/        # Job seeker dashboard & applications
├── templates/        # Global templates (attendance, assets, calendar, etc.)
├── static/           # CSS, JS, images
└── HRMS/             # Core project settings (urls, wsgi, asgi)
```

---

## 👩‍💻 Usage

* **Superadmin** → Manage subscriptions, companies, packages
* **Admin** → Manage employees, jobs, payroll, performance
* **Employee** → Apply for leave, view jobs, mark attendance
* **Jobseeker** → Register, apply for jobs, track status

---


