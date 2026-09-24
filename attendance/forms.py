from django import forms

from .models import Student, ClassRoom


# =========================================================
# STUDENT FORM
# =========================================================

class StudentForm(forms.ModelForm):

    class Meta:

        model = Student

        fields = [
            'name',
            'roll_number',
            'classroom'
        ]

        error_messages = {
            'roll_number': {
                'unique': 'This roll number already exists in this class.'
            }
        }

    def clean(self):

        cleaned_data = super().clean()

        roll_number = cleaned_data.get('roll_number')
        classroom = cleaned_data.get('classroom')

        if roll_number and classroom:

            existing_student = Student.objects.filter(
                roll_number=roll_number,
                classroom=classroom
            ).exclude(
                id=self.instance.id
            ).exists()

            if existing_student:

                self.add_error(
                    'roll_number',
                    'This roll number already exists in this class.'
                )

        return cleaned_data


# =========================================================
# CLASS ROOM FORM
# =========================================================

class ClassRoomForm(forms.ModelForm):

    class Meta:

        model = ClassRoom

        fields = [
            'name'
        ]

    def clean_name(self):

        name = self.cleaned_data['name'].strip()

        if not name:

            raise forms.ValidationError(
                'Class name is required.'
            )

        existing_class = ClassRoom.objects.filter(
            name__iexact=name
        ).exclude(
            id=self.instance.id
        ).exists()

        if existing_class:

            raise forms.ValidationError(
                'This class already exists.'
            )

        return name