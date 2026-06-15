from django import forms
from live_webinars.models import Instructor

class InstructorForm(forms.ModelForm):

    class Meta:
        model = Instructor

        fields = [
            "name",
            "designation",
            "organization",
            "email",
            "country",
            "phone_number",
            "bio",
            "photo",
        ]