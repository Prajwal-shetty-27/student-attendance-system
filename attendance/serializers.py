from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):

    student_name = serializers.CharField(
        source='student.name',
        read_only=True
    )

    roll_number = serializers.CharField(
        source='student.roll_number',
        read_only=True
    )

    class_name = serializers.CharField(
        source='timetable.classroom.name',
        read_only=True
    )

    subject = serializers.CharField(
        source='timetable.subject',
        read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            'id',
            'student_name',
            'roll_number',
            'class_name',
            'subject',
            'date',
            'status'
        ]