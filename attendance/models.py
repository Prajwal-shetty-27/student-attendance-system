from django.db import models
from django.contrib.auth.models import User


# =========================================================
# CLASS ROOM
# =========================================================

class ClassRoom(models.Model):

    name = models.CharField(
        max_length=50
    )

    def __str__(self):

        return self.name


# =========================================================
# STUDENT
# =========================================================

class Student(models.Model):

    name = models.CharField(
        max_length=100
    )

    roll_number = models.CharField(
        max_length=20
    )

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    'roll_number',
                    'classroom'
                ],
                name='unique_roll_number_per_class'
            )

        ]

    def __str__(self):

        return self.name


# =========================================================
# TIMETABLE
# =========================================================

class Timetable(models.Model):

    DAY_CHOICES = [

        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),

    ]

    classroom = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    subject = models.CharField(
        max_length=100
    )

    day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    def __str__(self):

        return f"{self.classroom} - {self.subject}"


# =========================================================
# ATTENDANCE
# =========================================================

class Attendance(models.Model):

    STATUS_CHOICES = [

        ('Present', 'Present'),
        ('Absent', 'Absent'),

    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    timetable = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE
    )

    date = models.DateField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    def __str__(self):

        return (
            f"{self.student} - "
            f"{self.date} - "
            f"{self.status}"
        )