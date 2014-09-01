# -*- coding: utf-8 -*
from django.shortcuts import render


def hello_world(request):
    """
    Say hello world.
    """
    return render(request, 'hello_world.html', {})
