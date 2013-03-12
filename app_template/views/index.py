# -*- coding: utf-8 -*
from django.shortcuts import render


def index_view(request):
    """
    An example index view.
    """
    attrs = {}

    return render(request, 'foundation.html', attrs)