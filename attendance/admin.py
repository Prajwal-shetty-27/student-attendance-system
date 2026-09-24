from django.contrib import admin
from .models import Student, ClassRoom, Timetable, Attendance

admin.site.register(Student)
admin.site.register(ClassRoom)
admin.site.register(Timetable)
admin.site.register(Attendance)