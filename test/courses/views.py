# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from .models import Course

def home(request):
	# return render(request, 'home.html')
	if 'searchform' in request.GET:
	    searchinput = request.GET.get("searchinput", "")
	    print searchinput
	    responseobject = {
	    	'message': searchinput
	    }
	    return JsonResponse(responseobject)
	else:
		# courses = Course.objects.all()
		return render(request, 'home.html')
