from django import forms
from . import models
import pyotp

def has_special_char(text: str) -> bool:
    return any(c for c in text if not c.isalnum() and not c.isspace())

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email:', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'user@example.com'
    }))

    password = forms.CharField(label='Password:', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your super secure password!'
    }), help_text='<a href="/accounts/password_reset">Forgot your password?</a>')

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        try:
            user = models.User.objects.get(email=email)

            if not user.check_password(password):
                self.add_error('password', 'Invalid email or password.')
        except models.User.DoesNotExist:
            self.add_error('email', 'Invalid email or password.')

        return cleaned_data


class TwoFactorAuthForm(forms.Form):
    otp = forms.IntegerField(label='Enter the OTP from your authenticator app:', widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': '123456'
    }))

    def __init__(self, user, *args, **kwargs):
        super(TwoFactorAuthForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super(TwoFactorAuthForm, self).clean()
        otp = cleaned_data.get('otp')
        self.otp = int(pyotp.TOTP(self.user.totp_code).now())

        if otp != self.otp:
            self.add_error('otp', 'Invalid OTP!')

        return cleaned_data


class RegisterForm(forms.Form):
    email = forms.EmailField(label='Email:', max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'user@example.com',
    }))
    password = forms.CharField(label='Password:', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your super secure password!'
    }), help_text='Your password must be longer than 8 characters, contain at least one special character and at least one number.')
    password_confirmation = forms.CharField(label='Confirm Password:', widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Re-enter your super secure password!'
    }))

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        try:
            models.User.objects.get(email=cleaned_data.get("email"))
            self.add_error('email', 'Email is already in use! Please login instead.')
        except models.User.DoesNotExist:
            pass

        if password != password_confirmation:
            self.add_error('password_confirmation', "Passwords do not match!")
        
        if len(password) < 8:
            self.add_error('password', "Password must be at least 8 characters long!")
        
        if not any(char.isdigit() for char in password):
            self.add_error('password', "Password must contain at least one number!")
        
        if not has_special_char(password):
            self.add_error('password', "Password must contain at least one special character!")

        return cleaned_data


class ConnectionForm(forms.Form):
    host = forms.CharField(label="Host:", max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    port = forms.IntegerField(label="Port:", widget=forms.NumberInput(attrs={
        'class': 'form-control',
    }))
    username = forms.CharField(label="Username:", max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    password = forms.CharField(label="Password:", widget=forms.PasswordInput(attrs={
        'class': 'form-control',
    }), help_text="Leave blank if you don't want to use a password.", required=False)
    private_key = forms.CharField(label="Private Key:", max_length=5000, widget=forms.Textarea(attrs={
        'class': 'form-control',
    }), help_text="Paste in your private key if you want to use a private key, else leave blank.", required=False)
    save_to_db = forms.BooleanField(label="Do you want to save this configuration to the server?", required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
    }))

    def clean(self):
        cleaned_data = super(ConnectionForm, self).clean()
        password = cleaned_data.get("password")
        private_key = cleaned_data.get("private_key")

        if not password and not private_key:
            raise forms.ValidationError("You must enter a password or a private key!")
        
        return cleaned_data


class EditConnectionForm(ConnectionForm):
    save_to_db = None

    def __init__(self, pk, *args, **kwargs):
        super(EditConnectionForm, self).__init__(*args, **kwargs)
        model = models.Configuration.objects.get(pk=pk)

        self.fields['host'].initial = model.host
        self.fields['port'].initial = model.port
        self.fields['username'].initial = model.username
        self.fields['password'].initial = model.password
        self.fields['private_key'].initial = model.private_key
