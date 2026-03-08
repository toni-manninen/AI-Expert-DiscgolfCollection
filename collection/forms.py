from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Disc


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Kayttajatunnus')
    password = forms.CharField(label='Salasana', widget=forms.PasswordInput)


class DiscForm(forms.ModelForm):
    in_bag = forms.BooleanField(required=False, label='Lisataan bakiin')

    class Meta:
        model = Disc
        fields = ('name', 'manufacturer', 'plastic', 'weight', 'color', 'image', 'acquired_at')
        widgets = {
            'acquired_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.acquired_at:
            self.initial['acquired_at'] = self.instance.acquired_at.strftime('%Y-%m-%dT%H:%M')
