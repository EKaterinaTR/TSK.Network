from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())
    vk_key = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['password'] != cleaned_data['password2']:
            self.add_error("password", "Пароли не совпадают")
        return cleaned_data

    class Meta:
        model = User
        fields = ("email", "username", "password", "password2")


class AuthForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class GraphPointListForm(forms.Form):
    vk_id = forms.CharField()
    CHOICES = [
        ('1', 'Без алгоритма'),
        ('2', 'Page Rank'),
        ('3', 'Hits'),
    ]
    algorithm = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=CHOICES,
    )
    # min_showing_score = forms.CharField(empty_value='0')