from django.urls import path

from .views import (
    teacher_home,
    timetable_view,
    take_attendance
)

from .api_views import AttendanceListAPI


urlpatterns = [

    # =====================================================
    # TEACHER HOME
    # =====================================================

    path(
        '',
        teacher_home,
        name='teacher_home'
    ),


    # =====================================================
    # TAKE ATTENDANCE
    # =====================================================

    path(
        'attendance/<int:timetable_id>/',
        take_attendance,
        name='take_attendance'
    ),


    # =====================================================
    # ATTENDANCE API
    # =====================================================

    path(
        'api/attendance/',
        AttendanceListAPI.as_view(),
        name='attendance_api'
    ),


    # =====================================================
    # TEACHER TIMETABLE
    # =====================================================

    path(
        'class/<int:class_id>/',
        timetable_view,
        name='timetable'
    ),

]