from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response


def google_login(request):
    """ Страница входа через Google
    """
    return render(request, 'google_login.html')


def login_my_account(request):
    """ Страница входа через Google
    """
    return render(request, 'login.html')
