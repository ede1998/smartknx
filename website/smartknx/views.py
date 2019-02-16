from django.shortcuts import render
from . import configuration

# Create your views here.

def details(request, **kwargs):
    ctx = {'all': configuration.__dict__, 'current': kwargs['area']}
    return render(request, 'smartknx/details.html', ctx)

def navigation(request, **kwargs):
    ctx = {'all': configuration.__dict__, 'current': kwargs.get('area', configuration)}
    return render(request, 'smartknx/navigation.html', ctx)