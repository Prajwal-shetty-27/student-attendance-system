from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import (
    Student,
    ClassRoom,
    Timetable,
    Attendance
)

from .forms import (
    StudentForm,
    ClassRoomForm
)


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return login_redirect(request)

    error = None

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('login_redirect')

        else:

            error = 'Invalid username or password.'

    return render(
        request,
        'attendance/login.html',
        {
            'error': error
        }
    )


# =========================================================
# LOGIN REDIRECT
# =========================================================

@login_required
def login_redirect(request):

    if request.user.is_staff:

        return redirect('admin_dashboard')

    return redirect('teacher_home')


# =========================================================
# LOGOUT
# =========================================================

@login_required
def logout_view(request):

    logout(request)

    return redirect('login')


# =========================================================
# TEACHER HOME
# =========================================================

@login_required
def teacher_home(request):

    teacher_timetables = Timetable.objects.filter(
        teacher=request.user
    )

    class_ids = teacher_timetables.values_list(
        'classroom_id',
        flat=True
    )

    classes = ClassRoom.objects.filter(
        id__in=class_ids
    ).distinct().order_by(
        'name'
    )

    return render(
        request,
        'attendance/teacher_home.html',
        {
            'classes': classes
        }
    )
# =========================================================
# SUBJECT-WISE ATTENDANCE
# =========================================================

@login_required
def subject_attendance(request):

    # Only Admin can access
    if not request.user.is_staff:
        return render(
            request,
            'attendance/access_denied.html'
        )

    classrooms = ClassRoom.objects.all().order_by(
        'name'
    )

    selected_class = request.GET.get(
        'class_id',
        ''
    )

    selected_date = request.GET.get(
        'date',
        ''
    )

    attendance_records = Attendance.objects.select_related(
        'student',
        'timetable',
        'timetable__classroom'
    ).all()

    if selected_class:
        attendance_records = attendance_records.filter(
            timetable__classroom_id=selected_class
        )

    if selected_date:
        attendance_records = attendance_records.filter(
            date=selected_date
        )

    # =====================================================
    # SUBJECT-WISE ATTENDANCE
    # =====================================================

    subject_data = {}

    for record in attendance_records:

        subject = record.timetable.subject

        if subject not in subject_data:
            subject_data[subject] = {
                'total': 0,
                'present': 0,
                'absent': 0,
            }

        subject_data[subject]['total'] += 1

        if record.status == 'Present':
            subject_data[subject]['present'] += 1

        elif record.status == 'Absent':
            subject_data[subject]['absent'] += 1

    # Calculate percentage
    for subject in subject_data:

        total = subject_data[subject]['total']
        present = subject_data[subject]['present']

        if total > 0:
            subject_data[subject]['percentage'] = round(
                (present / total) * 100,
                1
            )
        else:
            subject_data[subject]['percentage'] = 0

    # Convert dictionary to list
    subject_summary = []

    for subject, data in subject_data.items():

        subject_summary.append({
            'subject': subject,
            'total': data['total'],
            'present': data['present'],
            'absent': data['absent'],
            'percentage': data['percentage'],
        })

    # Sort subjects alphabetically
    subject_summary.sort(
        key=lambda item: item['subject']
    )

    return render(
        request,
        'attendance/subject_attendance.html',
        {
            'classrooms': classrooms,
            'selected_class': selected_class,
            'selected_date': selected_date,
            'subject_summary': subject_summary,
        }
    )


# =========================================================
# TEACHER TIMETABLE
# =========================================================

@login_required
def timetable_view(request, class_id):

    classroom = get_object_or_404(
        ClassRoom,
        id=class_id
    )

    timetables = Timetable.objects.filter(
        classroom=classroom,
        teacher=request.user
    ).order_by(
        'day',
        'start_time'
    )

    return render(
        request,
        'attendance/timetable.html',
        {
            'classroom': classroom,
            'timetables': timetables
        }
    )


# =========================================================
# TAKE ATTENDANCE
# =========================================================

@login_required
def take_attendance(request, timetable_id):

    timetable = get_object_or_404(
        Timetable,
        id=timetable_id
    )

    if timetable.teacher != request.user:

        return render(
            request,
            'attendance/access_denied.html'
        )

    students = Student.objects.filter(
        classroom=timetable.classroom
    ).order_by(
        'roll_number'
    )

    today = timezone.localdate()

    if request.method == 'POST':

        # Check that every student has been marked.
        for student in students:

            status = request.POST.get(
                f'student_{student.id}'
            )

            if status not in ['Present', 'Absent']:

                # Preserve the selected values when showing the warning.
                for current_student in students:

                    current_status = request.POST.get(
                        f'student_{current_student.id}'
                    )

                    current_student.current_status = current_status

                return render(
                    request,
                    'attendance/take_attendance.html',
                    {
                        'timetable': timetable,
                        'classroom': timetable.classroom,
                        'students': students,
                        'error': (
                            'Please mark Present or Absent '
                            'for every student.'
                        )
                    }
                )

        # Save attendance.
        for student in students:

            status = request.POST.get(
                f'student_{student.id}'
            )

            Attendance.objects.update_or_create(
                student=student,
                timetable=timetable,
                date=today,
                defaults={
                    'status': status
                }
            )

        # Return to the selected class timetable.
        return redirect(
            'timetable',
            class_id=timetable.classroom.id
        )

    # Load today's saved attendance when opening the page.
    for student in students:

        existing_attendance = Attendance.objects.filter(
            student=student,
            timetable=timetable,
            date=today
        ).first()

        if existing_attendance:

            student.current_status = existing_attendance.status

        else:

            student.current_status = None

    return render(
        request,
        'attendance/take_attendance.html',
        {
            'timetable': timetable,
            'classroom': timetable.classroom,
            'students': students
        }
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@login_required
def admin_dashboard(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    attendance_records = Attendance.objects.select_related(
        'student',
        'timetable',
        'timetable__classroom'
    ).order_by(
        '-date'
    )

    # Class filter

    class_id = request.GET.get('class_id')

    if class_id:

        attendance_records = attendance_records.filter(
            timetable__classroom_id=class_id
        )

    # Date filter

    date = request.GET.get('date')

    if date:

        attendance_records = attendance_records.filter(
            date=date
        )

    total_records = attendance_records.count()

    present_count = attendance_records.filter(
        status='Present'
    ).count()

    absent_count = attendance_records.filter(
        status='Absent'
    ).count()

    if total_records > 0:

        attendance_percentage = round(
            (present_count / total_records) * 100,
            1
        )

    else:

        attendance_percentage = 0

    classrooms = ClassRoom.objects.all().order_by(
        'name'
    )

    return render(
        request,
        'attendance/admin_dashboard.html',
        {
            'attendance_records': attendance_records,
            'classrooms': classrooms,
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'attendance_percentage': attendance_percentage,
            'selected_class': class_id,
            'selected_date': date
        }
    )


# =========================================================
# STUDENTS
# =========================================================

@login_required
def students(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    student_list = Student.objects.select_related(
        'classroom'
    ).order_by(
        'classroom__name',
        'roll_number'
    )

    return render(
        request,
        'attendance/students.html',
        {
            'students': student_list
        }
    )


# =========================================================
# ADD STUDENT
# =========================================================

@login_required
def add_student(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    if request.method == 'POST':

        form = StudentForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                'students'
            )

    else:

        form = StudentForm()

    return render(
        request,
        'attendance/add_student.html',
        {
            'form': form
        }
    )


# =========================================================
# EDIT STUDENT
# =========================================================

@login_required
def edit_student(request, student_id):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    student = get_object_or_404(
        Student,
        id=student_id
    )

    if request.method == 'POST':

        form = StudentForm(
            request.POST,
            instance=student
        )

        if form.is_valid():

            form.save()

            return redirect(
                'students'
            )

    else:

        form = StudentForm(
            instance=student
        )

    return render(
        request,
        'attendance/edit_student.html',
        {
            'form': form,
            'student': student
        }
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@login_required
def delete_student(request, student_id):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    student = get_object_or_404(
        Student,
        id=student_id
    )

    student.delete()

    return redirect(
        'students'
    )


# =========================================================
# CLASSES
# =========================================================

@login_required
def classes(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    class_list = ClassRoom.objects.all().order_by(
        'name'
    )

    return render(
        request,
        'attendance/classes.html',
        {
            'classes': class_list
        }
    )


# =========================================================
# ADD CLASS
# =========================================================

@login_required
def add_class(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    if request.method == 'POST':

        form = ClassRoomForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                'classes'
            )

    else:

        form = ClassRoomForm()

    return render(
        request,
        'attendance/add_class.html',
        {
            'form': form
        }
    )


# =========================================================
# EDIT CLASS
# =========================================================

@login_required
def edit_class(request, class_id):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    classroom = get_object_or_404(
        ClassRoom,
        id=class_id
    )

    if request.method == 'POST':

        form = ClassRoomForm(
            request.POST,
            instance=classroom
        )

        if form.is_valid():

            form.save()

            return redirect(
                'classes'
            )

    else:

        form = ClassRoomForm(
            instance=classroom
        )

    return render(
        request,
        'attendance/edit_class.html',
        {
            'form': form,
            'classroom': classroom
        }
    )


# =========================================================
# DELETE CLASS
# =========================================================

@login_required
def delete_class(request, class_id):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    classroom = get_object_or_404(
        ClassRoom,
        id=class_id
    )

    classroom.delete()

    return redirect(
        'classes'
    )


# =========================================================
# TEACHERS
# =========================================================

@login_required
def teachers(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    teacher_list = User.objects.filter(
        is_staff=False
    ).order_by(
        'username'
    )

    return render(
        request,
        'attendance/teachers.html',
        {
            'teachers': teacher_list
        }
    )


# =========================================================
# ADD TEACHER
# =========================================================

@login_required
def add_teacher(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'attendance/add_teacher.html',
                {
                    'error': 'Username already exists.'
                }
            )

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect(
            'teachers'
        )

    return render(
        request,
        'attendance/add_teacher.html'
    )


# =========================================================
# EDIT TEACHER
# =========================================================

@login_required
def edit_teacher(request, teacher_id):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    teacher = get_object_or_404(
        User,
        id=teacher_id,
        is_staff=False
    )

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        existing_teacher = User.objects.filter(
            username=username
        ).exclude(
            id=teacher.id
        ).exists()

        if existing_teacher:

            return render(
                request,
                'attendance/edit_teacher.html',
                {
                    'teacher': teacher,
                    'error': 'Username already exists.'
                }
            )

        teacher.username = username

        if password:

            teacher.set_password(
                password
            )

        teacher.save()

        return redirect(
            'teachers'
        )

    return render(
        request,
        'attendance/edit_teacher.html',
        {
            'teacher': teacher
        }
    )


# =========================================================
# DELETE TEACHER
# =========================================================

@login_required
def delete_teacher(request, teacher_id):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    teacher = get_object_or_404(
        User,
        id=teacher_id,
        is_staff=False
    )

    teacher.delete()

    return redirect(
        'teachers'
    )


# =========================================================
# TIMETABLES
# =========================================================

@login_required
def timetables(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    timetable_list = Timetable.objects.select_related(
        'classroom',
        'teacher'
    ).order_by(
        'day',
        'start_time'
    )

    return render(
        request,
        'attendance/timetables.html',
        {
            'timetables': timetable_list
        }
    )


# =========================================================
# ADD TIMETABLE
# =========================================================

@login_required
def add_timetable(request):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    classrooms = ClassRoom.objects.all().order_by(
        'name'
    )

    teachers = User.objects.filter(
        is_staff=False
    ).order_by(
        'username'
    )

    if request.method == 'POST':

        classroom_id = request.POST.get(
            'classroom'
        )

        teacher_id = request.POST.get(
            'teacher'
        )

        subject = request.POST.get(
            'subject'
        )

        day = request.POST.get(
            'day'
        )

        start_time = request.POST.get(
            'start_time'
        )

        end_time = request.POST.get(
            'end_time'
        )

        # -------------------------------------------------
        # TIME VALIDATION
        # -------------------------------------------------

        if start_time and end_time:

            if end_time <= start_time:

                return render(
                    request,
                    'attendance/add_timetable.html',
                    {
                        'classrooms': classrooms,
                        'teachers': teachers,
                        'error': (
                            'End time must be after '
                            'start time.'
                        )
                    }
                )

        # -------------------------------------------------
        # CLASS OVERLAP VALIDATION
        # -------------------------------------------------

        overlapping_timetable = Timetable.objects.filter(
            classroom_id=classroom_id,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping_timetable:

            return render(
                request,
                'attendance/add_timetable.html',
                {
                    'classrooms': classrooms,
                    'teachers': teachers,
                    'error': (
                        'This timetable overlaps with '
                        'an existing period for this class.'
                    )
                }
            )

        # -------------------------------------------------
        # TEACHER OVERLAP VALIDATION
        # -------------------------------------------------

        teacher_overlap = Timetable.objects.filter(
            teacher_id=teacher_id,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if teacher_overlap:

            return render(
                request,
                'attendance/add_timetable.html',
                {
                    'classrooms': classrooms,
                    'teachers': teachers,
                    'error': (
                        'This teacher already has another '
                        'class during this time.'
                    )
                }
            )

        # -------------------------------------------------
        # CREATE TIMETABLE
        # -------------------------------------------------

        Timetable.objects.create(

            classroom_id=classroom_id,

            teacher_id=teacher_id,

            subject=subject,

            day=day,

            start_time=start_time,

            end_time=end_time
        )

        return redirect(
            'timetables'
        )

    return render(
        request,
        'attendance/add_timetable.html',
        {
            'classrooms': classrooms,
            'teachers': teachers
        }
    )


# =========================================================
# EDIT TIMETABLE
# =========================================================

@login_required
def edit_timetable(request, timetable_id):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    timetable = get_object_or_404(
        Timetable,
        id=timetable_id
    )

    classrooms = ClassRoom.objects.all().order_by(
        'name'
    )

    teachers = User.objects.filter(
        is_staff=False
    ).order_by(
        'username'
    )

    if request.method == 'POST':

        classroom_id = request.POST.get(
            'classroom'
        )

        teacher_id = request.POST.get(
            'teacher'
        )

        subject = request.POST.get(
            'subject'
        )

        day = request.POST.get(
            'day'
        )

        start_time = request.POST.get(
            'start_time'
        )

        end_time = request.POST.get(
            'end_time'
        )

        # -------------------------------------------------
        # TIME VALIDATION
        # -------------------------------------------------

        if start_time and end_time:

            if end_time <= start_time:

                return render(
                    request,
                    'attendance/edit_timetable.html',
                    {
                        'timetable': timetable,
                        'classrooms': classrooms,
                        'teachers': teachers,
                        'error': (
                            'End time must be after '
                            'start time.'
                        )
                    }
                )

        # -------------------------------------------------
        # CLASS OVERLAP VALIDATION
        # -------------------------------------------------

        overlapping_timetable = Timetable.objects.filter(
            classroom_id=classroom_id,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(
            id=timetable.id
        ).exists()

        if overlapping_timetable:

            return render(
                request,
                'attendance/edit_timetable.html',
                {
                    'timetable': timetable,
                    'classrooms': classrooms,
                    'teachers': teachers,
                    'error': (
                        'This timetable overlaps with '
                        'an existing period for this class.'
                    )
                }
            )

        # -------------------------------------------------
        # TEACHER OVERLAP VALIDATION
        # -------------------------------------------------

        teacher_overlap = Timetable.objects.filter(
            teacher_id=teacher_id,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(
            id=timetable.id
        ).exists()

        if teacher_overlap:

            return render(
                request,
                'attendance/edit_timetable.html',
                {
                    'timetable': timetable,
                    'classrooms': classrooms,
                    'teachers': teachers,
                    'error': (
                        'This teacher already has another '
                        'class during this time.'
                    )
                }
            )

        # -------------------------------------------------
        # UPDATE TIMETABLE
        # -------------------------------------------------

        timetable.classroom_id = classroom_id

        timetable.teacher_id = teacher_id

        timetable.subject = subject

        timetable.day = day

        timetable.start_time = start_time

        timetable.end_time = end_time

        timetable.save()

        return redirect(
            'timetables'
        )

    return render(
        request,
        'attendance/edit_timetable.html',
        {
            'timetable': timetable,
            'classrooms': classrooms,
            'teachers': teachers
        }
    )


# =========================================================
# DELETE TIMETABLE
# =========================================================

@login_required
def delete_timetable(request, timetable_id):

    if not request.user.is_staff:

        return render(
            request,
            'attendance/access_denied.html'
        )

    timetable = get_object_or_404(
        Timetable,
        id=timetable_id
    )

    timetable.delete()

    return redirect(
        'timetables'
    )


# =========================================================
# URL ALIASES
# =========================================================

students_view = students

classes_view = classes

teachers_view = teachers

timetables_view = timetables