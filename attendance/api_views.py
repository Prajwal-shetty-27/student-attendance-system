
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceListAPI(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        attendance = Attendance.objects.all().order_by('-date')

        # Date filter

        date = request.GET.get('date')

        if date:

            attendance = attendance.filter(
                date=date
            )


        # Class filter

        class_name = request.GET.get('class_name')

        if class_name:

            attendance = attendance.filter(
                timetable__classroom__name=class_name
            )


        serializer = AttendanceSerializer(
            attendance,
            many=True
        )

        return Response(serializer.data)

