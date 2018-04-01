# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse
from .models import Course

def home(request):
	courses = Course.objects.all()
	return render(request, 'home.html', {'courses': courses})
