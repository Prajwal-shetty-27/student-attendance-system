from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from attendance.views import (
    login_view,
    login_redirect,
    logout_view,

    admin_dashboard,
    subject_attendance,

    students,
    add_student,
    edit_student,
    delete_student,

    classes,
    add_class,
    edit_class,
    delete_class,

    teachers,
    add_teacher,
    edit_teacher,
    delete_teacher,

    timetables,
    add_timetable,
    edit_timetable,
    delete_timetable,
)


urlpatterns = [

    # =====================================================
    # HOME
    # =====================================================

    path(
        '',
        lambda request: redirect('/login/')
    ),

    # =====================================================
    # DJANGO ADMIN
    # =====================================================

    path(
        'admin/',
        admin.site.urls
    ),

    # =====================================================
    # LOGIN / LOGOUT
    # =====================================================

    path(
        'login/',
        login_view,
        name='login'
    ),

    path(
        'login-redirect/',
        login_redirect,
        name='login_redirect'
    ),

    path(
        'logout/',
        logout_view,
        name='logout'
    ),

    # =====================================================
    # TEACHER
    # =====================================================

    path(
        'teacher/',
        include('attendance.urls')
    ),

    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    path(
        'dashboard/',
        admin_dashboard,
        name='admin_dashboard'
    ),

    # =====================================================
    # SUBJECT-WISE ATTENDANCE
    # =====================================================

    path(
        'subject-attendance/',
        subject_attendance,
        name='subject_attendance'
    ),

    # =====================================================
    # STUDENTS
    # =====================================================

    path(
        'students/',
        students,
        name='students'
    ),

    path(
        'students/add/',
        add_student,
        name='add_student'
    ),

    path(
        'students/edit/<int:student_id>/',
        edit_student,
        name='edit_student'
    ),

    path(
        'students/delete/<int:student_id>/',
        delete_student,
        name='delete_student'
    ),

    # =====================================================
    # CLASSES
    # =====================================================

    path(
        'classes/',
        classes,
        name='classes'
    ),

    path(
        'classes/add/',
        add_class,
        name='add_class'
    ),

    path(
        'classes/edit/<int:class_id>/',
        edit_class,
        name='edit_class'
    ),

    path(
        'classes/delete/<int:class_id>/',
        delete_class,
        name='delete_class'
    ),

    # =====================================================
    # TEACHERS
    # =====================================================

    path(
        'teachers/',
        teachers,
        name='teachers'
    ),

    path(
        'teachers/add/',
        add_teacher,
        name='add_teacher'
    ),

    path(
        'teachers/edit/<int:teacher_id>/',
        edit_teacher,
        name='edit_teacher'
    ),

    path(
        'teachers/delete/<int:teacher_id>/',
        delete_teacher,
        name='delete_teacher'
    ),

    # =====================================================
    # TIMETABLES
    # =====================================================

    path(
        'timetables/',
        timetables,
        name='timetables'
    ),

    path(
        'timetables/add/',
        add_timetable,
        name='add_timetable'
    ),

    path(
        'timetables/edit/<int:timetable_id>/',
        edit_timetable,
        name='edit_timetable'
    ),

    path(
        'timetables/delete/<int:timetable_id>/',
        delete_timetable,
        name='delete_timetable'
    ),

]