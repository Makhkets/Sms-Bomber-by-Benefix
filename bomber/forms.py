from django import forms
from django.contrib.auth import get_user_model
from django.contrib import auth
from loguru import logger

from .models import Attack

class RegisterForm(forms.ModelForm):
    confrim_password = forms.CharField(label="", max_length=50, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Confrim Password"
    }))
    
    class Meta:
        model = get_user_model()
        fields = ["username", "password"]


        widgets = {
            "username" : forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username",
            }),

            "password": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Password",
            }),
        }

        labels = {
            "username" : "",
            "password" : "",
        }

        help_texts = {
            'username': None,
            'password': None,
        }

    def isValid(self):
        if self.cleaned_data.get("password") == self.cleaned_data.get("confrim_password"):
            return True
        else: return False

class LoginForm(forms.Form):
    username = forms.CharField(label="", max_length=15, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))
    password = forms.CharField(label="", max_length=15, widget=forms.PasswordInput(attrs={
        "class": "form-control"
    }))

    def isValid(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        return True

class AttackForm(forms.ModelForm):
    class Meta:
        model = Attack
        fields = ["phone", "minute", "description"]

        widgets = {
            "phone": forms.TextInput(attrs={
                "class": "feedback-input",
                "placeholder": "79XXXXXXXXX"
            }),
            "minute": forms.TextInput(attrs={
                "class": "feedback-input",
                "placeholder": "Время в минутах (Максимум 30)"
            }),
            "description": forms.Textarea(attrs={
                "class": "feedback-input",
                "placeholder": "Заметка о номере"
            })
        }

    def isValid(self):
        if int(self.data.get("minute")) <= 30:
            return True
        return False
            
        