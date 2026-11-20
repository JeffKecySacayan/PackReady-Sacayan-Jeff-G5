import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class BootstrapFormMixin:
    """Adds Bootstrap classes to every field widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


def validate_contact_number(value):
    if value and not re.fullmatch(r"\+?[0-9 \-]{7,15}", value):
        raise forms.ValidationError(
            "Enter a valid contact number (7-15 digits, may start with +)."
        )


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    contact_number = forms.CharField(
        max_length=20, required=False, validators=[validate_contact_number]
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username", "email", "contact_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    pass


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    contact_number = forms.CharField(
        max_length=20, required=False, validators=[validate_contact_number]
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "contact_number", "profile_photo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email