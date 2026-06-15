from django import forms
from django.contrib.auth import get_user_model
from django_countries.widgets import CountrySelectWidget
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Create a strong password"
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password"
        })
    )

    phone_number = forms.CharField(
    required=False,
    widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Enter your phone number"
    })
)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "company",
            "country",
            "phone_number",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your first name"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your last name"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your email"
            }),
            "company": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your company name"
            }),
            "country": CountrySelectWidget(attrs={
                "class": "form-select"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:

            # Check match
            if password != confirm_password:
                self.add_error("confirm_password", "Passwords do not match")
                return cleaned_data

            # Django built-in password validation
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                self.add_error("password", e)

        return cleaned_data
    
    # def clean_phone_number(self):
    #     phone = self.cleaned_data.get("phone_number")

    #     if phone and User.objects.filter(phone_number=phone).exists():
    #         raise forms.ValidationError("This phone number is already registered.")

    #     return phone
    
    def clean_email(self):
        email = self.cleaned_data.get("email")

        if email:
            email = email.lower()  # normalize

            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Email is already registered.")

        return email

    def clean_phone_number(self):
        full_phone = self.data.get("full_phone_number")

        if full_phone:
            return full_phone

        return self.cleaned_data.get("phone_number")



