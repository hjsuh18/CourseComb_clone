# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Course
from django.contrib.postgres.search import SearchVector
import json, cgi
from .cas import CASClient
from django.urls import resolve


def home(request):
	# return render(request, 'home.html')
	if 'searchform' in request.GET:
		searchinput = request.GET.get("searchinput", "")
		results = Course.objects.annotate(
			search=SearchVector('title', 'deptnum'),
		).filter(search=searchinput)
		for result in results:
			print result.title
		responseobject = {
			'message': results.title
		}
		return JsonResponse(responseobject)
	else:
		# courses = Course.objects.all()
		return render(request, 'home.html')

def get_courses(request):
	if request.is_ajax():
		q = request.GET.get('term', '')
		searchresults = Course.objects.annotate(
			search=SearchVector('title', 'deptnum'),
		).filter(search=q)
		results = []
		for result in searchresults:
			course_json = {}
			course_json = result.deptnum + ": " + result.title
			results.append(course_json)
		data = json.dumps(results)
	else:
		data = 'fail'
	
	mimetype = 'application/json'
	return HttpResponse(data, mimetype)

def login(request):
	# return render(request, 'home.html')
	C = CASClient()
	auth_attempt = C.Authenticate(request.GET)
	if "netid" in auth_attempt:  # Successfully authenticated.
		return render(request, 'home.html')
	elif "location" in auth_attempt:  # Redirect to CAS.
		return HttpResponseRedirect(auth_attempt["location"])
	else:  # This should never happen!
		abort(500)
