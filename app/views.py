from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
from django.contrib.sites.models import Site
from . import forms, models
import requests
import json
import pyotp

session = requests.Session()


def error_404(request, exception):
    return render(request, 'app/errors/404.html')


def error_500(request):
    return render(request, 'app/errors/500.html')


def get_config(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 403,
            'message': "You do not have permission to access this endpoint."
        })
    else:
        return JsonResponse({
            'status': 200,
            'config': request.session['connection'],
        })

def request_2fa(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 403,
            'message': "You do not have permission to access this endpoint."
        })
    else:
        if request.user.totp_code == None:
            while True:
                totp_code = pyotp.random_base32()
                try:
                    models.User.objects.get(totp_code=totp_code)
                    continue
                except models.User.DoesNotExist:
                    break

            otp = pyotp.TOTP(totp_code).now()

            return JsonResponse({
                'status': 200,
                'code': totp_code,
                'qr': pyotp.totp.TOTP(totp_code).provisioning_uri(
                    name=request.user.email, issuer_name="Kommander" 
                ),
                'otp': otp,
            })
        else:
            return JsonResponse({
                'status': 200,
                'otp': pyotp.TOTP(request.user.totp_code).now(),
            })

def enable_2fa(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 403,
            'message': "You do not have permission to access this endpoint."
        })
    else:
        body = json.loads(request.body.decode('utf-8'))
        totp = body['totp']

        request.user.totp_code = totp
        request.user.save()

        return JsonResponse({
            'status': 200,
        })

def disable_2fa(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 403,
            'message': "You do not have permission to access this endpoint."
        })
    else:
        request.user.totp_code = None
        request.user.save()

        return JsonResponse({
            'status': 200,
        })

def home(request):
    if not request.user.is_authenticated:
        return render(request, 'app/about.html')
    else:
        if request.method == 'POST':
            form = forms.ConnectionForm(request.POST)
            if form.is_valid():
                host = form.cleaned_data['host']
                port = form.cleaned_data['port']
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                private_key = form.cleaned_data['private_key']
                save_to_db = form.cleaned_data['save_to_db']

                if save_to_db:
                    models.Configuration.objects.create(
                        host=host, port=port, username=username,
                        password=password if password else None,
                        private_key=private_key if private_key else None,
                        user=request.user,
                    )

                request.session['connection'] = {
                    'host': host,
                    'port': port,
                    'username': username,
                    'password': password if password else None,
                    'private_key': private_key if private_key else None,
                }

                return terminal(request)
            else:
                connections = models.Configuration.objects.filter(user=request.user)
                return render(request, 'app/home.html', {'form': form, 'connections': connections})

        form = forms.ConnectionForm()
        connections = models.Configuration.objects.filter(user=request.user)

        return render(request, 'app/home.html', {'form': form, 'connections': connections})


def account(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that!")
    else:
        context = {}
        if request.user.totp_code != None:
            context['2fa'] = False
        else:
            context['2fa'] = True

        return render(request, 'app/account.html', context=context)


def terminal(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that!")
        return redirect('app:home')
    else:
        connection = request.GET.get('id')
        if connection:
            try:
                connection = models.Configuration.objects.get(
                    pk=connection, user=request.user)
                config = {
                    'host': connection.host,
                    'port': connection.port,
                    'username': connection.username,
                    'password': connection.password if connection.password else None,
                    'private_key': connection.private_key if connection.private_key else None,
                }

                request.session['connection'] = config

            except models.Configuration.DoesNotExist:
                messages.error(request, "Configuration does not exist!")
                return redirect('app:home')

        else:
            config = request.session['connection']

        return render(request, 'app/terminal.html')


def delete(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that!")
    else:
        connection = request.GET.get('id')
        if connection:
            try:
                connection = models.Configuration.objects.get(
                    pk=connection, user=request.user)
                connection.delete()
                messages.success(
                    request, "Configuration deleted successfully.")
            except models.Configuration.DoesNotExist:
                messages.error(request, "Configuration does not exist!")
        else:
            messages.error(request, "Configuration does not exist!")
        return redirect('app:home')


def edit(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that!")
    else:
        connection = request.GET.get('id')
        try:
            model = models.Configuration.objects.get(
                pk=connection, user=request.user)
        except models.Configuration.DoesNotExist:
            messages.error(request, "Configuration does not exist!")
            return redirect('app:home')

        if request.method == 'POST':
            form = forms.EditConnectionForm(connection, request.POST)
            if form.is_valid():
                host = form.cleaned_data['host']
                port = form.cleaned_data['port']
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                private_key = form.cleaned_data['private_key']

                model.host = host
                model.port = port
                model.username = username
                model.password = password if password else None
                model.private_key = private_key if private_key else None
                model.save()

                messages.success(
                    request, "Configuration updated successfully.")
                return redirect('app:home')

        form = forms.EditConnectionForm(pk=connection)
        return render(request, 'app/edit.html', {'form': form, 'model': model})


def logout(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to do that!")
    else:
        logout_user(request)
        messages.success(request, "You have been logged out.")
        return redirect('app:home')

def login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = forms.LoginForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']

                user = authenticate(request, email=email, password=password)

                if user.totp_code == None:
                    login_user(request, user)

                    messages.success(request, 'Logged in successfully.')
                    return redirect('app:home')
                
                else:
                    request.session['2fa_user'] = user.id
                    return redirect('app:2fa')
            else:
                return render(request, 'app/login.html', {'form': form})

        form = forms.LoginForm()
        return render(request, 'app/login.html', {'form': form})
    else:
        return redirect('app:home')

def two_factor_auth(request):
    if request.user.is_authenticated:
        return redirect('app:home')
    else:
        user = models.User.objects.get(pk=request.session['2fa_user'])

        if request.method == 'POST':
            form = forms.TwoFactorAuthForm(user, request.POST)

            if form.is_valid():
                login_user(request, user)

                messages.success(request, 'Logged in successfully.')
                return redirect('app:home')
            else:
                return render(request, 'app/2fa.html', {'form': form})

        form = forms.TwoFactorAuthForm(user)
        return render(request, 'app/2fa.html', {'form': form})


def register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = forms.RegisterForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                user = models.User.objects.create_user(
                    email=email, password=password)
                user.save()
                login_user(request, user)
                messages.success(request, 'Account created successfully.')
                return redirect('app:home')
            else:
                return render(request, 'app/register.html', {'form': form})

        form = forms.RegisterForm()
        return render(request, 'app/register.html', {'form': form})
    else:
        return redirect('app:home')
