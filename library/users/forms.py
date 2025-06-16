from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        label=_('Username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        help_text=_('Required. Enter a valid email address.')
    )
    phone_number = forms.CharField(
        label=_('Phone Number'),
        max_length=20,
        required=False,
        help_text=_('Optional. Your phone number.')
    )
    address = forms.CharField(
        label=_('Address'),
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text=_('Optional. Your address.')
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'address', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(_('A user with that email already exists.'))
        return email
