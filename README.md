\# Student Attendance System



A \*\*Student Attendance Management System\*\* built using \*\*Python, Django, and Django REST Framework\*\*.



The system provides separate access for \*\*Admin and Teacher\*\* users. Admins can manage students, classes, teachers, and timetables, while teachers can take and manage student attendance.



\## Features



\- Role-based login (Admin and Teacher)

\- Student management

\- Class management

\- Teacher management

\- Timetable management

\- Mark and edit attendance

\- Subject-wise attendance tracking

\- Attendance filtering by class and date

\- Admin attendance dashboard

\- REST API for attendance data

\- Responsive user interface



\## Tech Stack



\- Python

\- Django

\- Django REST Framework

\- SQLite

\- HTML

\- CSS

\- JavaScript



\## How to Run



\### 1. Clone the repository



```bash

git clone https://github.com/Prajwal-shetty-27/student-attendance-system.git

cd student-attendance-system

```



\### 2. Create and activate a virtual environment



\*\*Windows:\*\*



```bash

python -m venv venv

venv\\Scripts\\activate

```



\*\*Mac/Linux:\*\*



```bash

python -m venv venv

source venv/bin/activate

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Run migrations



```bash

python manage.py migrate

```



\### 5. Create an admin user



```bash

python manage.py createsuperuser

```



\### 6. Start the development server



```bash

python manage.py runserver

```



Open:



```text

http://127.0.0.1:8000/

```



\## API Endpoint



\### Attendance API



```text

GET /teacher/api/attendance/

```



Example:



```text

http://127.0.0.1:8000/teacher/api/attendance/

```



The API returns attendance information including:



\- Student name

\- Roll number

\- Class

\- Subject

\- Date

\- Attendance status



\## Project Structure



```text

student-attendance-system/

│

├── attendance/

│   ├── migrations/

│   ├── templates/

│   ├── models.py

│   ├── views.py

│   ├── forms.py

│   ├── serializers.py

│   └── api\_views.py

│

├── config/

│   ├── settings.py

│   ├── urls.py

│   └── wsgi.py

│

├── manage.py

├── requirements.txt

└── .gitignore

```



\## Author



\*\*Prajwal\*\*

