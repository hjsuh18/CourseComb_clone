# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Course, Profile
from django.contrib.postgres.search import SearchVector
import json, cgi
from .cas import CASClient
from django.urls import resolve

from combination import combine

def home(request):
	# return render(request, 'home.html')
	curr_profile = request.user.profile


	ids = curr_profile.faves.split(',')
	course_list = []
	for i in ids:
		if (i != ''):
			course = Course.objects.filter(registrar_id=i)
			course_list.append(course[0])
	combo = combine(course_list, 2)

	combination = []
	if combo != None:
		for c in combo:
			comb_str = str(c[len(c) - 1])
			for i in range(len(c) - 2, -1, -1):
				comb_str = comb_str + ', ' + str(c[i])
			combination.append(comb_str)

	# save the course combinations to user
	curr_profile.course_combo = combination
	curr_profile.save()

	# render the course combinations
	display = []
	for i in range (0, len(combination)):
		display.append("<div class = '" + str(i) + "'>" + combination[i] + " <button type = 'button' class = 'btn btn-danger btn-xs deletecomb' id = " + str(i) + "> x </button> </div>") 

	return render(request, 'home.html', {"combinations": display})







	# if 'searchform' in request.GET:
	# 	searchinput = request.GET.get("searchinput", "")
	# 	results = Course.objects.annotate(
	# 		search=SearchVector('title', 'deptnum'),
	# 	).filter(search=searchinput)
	# 	for result in results:
	# 		print result.title
	# 	responseobject = {
	# 		'message': results.title
	# 	}
	# 	return JsonResponse(responseobject)

	# add course to faves by registrar_id
	if 'addclass' in request.POST:
		registrar_id = request.POST.get("registrar_id", "")
		class_name = request.POST.get("class", "")
		if registrar_id not in curr_profile.faves:
			new_faves = curr_profile.faves + "," + registrar_id
			curr_profile.faves = new_faves
			curr_profile.save()
			responseobject = {'newclass': class_name, 'newid': registrar_id}
		else:
			responseobject = {}
		return JsonResponse(responseobject)
	# delete course from course queue
	elif 'deleteclass' in request.POST:
		registrar_id = request.POST.get("registrar_id", "")
		favorites = curr_profile.faves
		favorites = favorites.split(",")
		curr_faves = [x for x in favorites if registrar_id not in x]
		curr_profile.faves = ','.join(curr_faves)
		curr_profile.save()
		responseobject = {}
		return JsonResponse(responseobject)

	# delete course combination in database
	elif 'deletecomb' in request.POST:
		# change this for course combination
		registrar_id = request.POST.get("registrar_id", "")
		favorites = curr_profile.faves
		favorites = favorites.split(",")
		curr_faves = [x for x in favorites if registrar_id not in x]
		curr_profile.faves = ','.join(curr_faves)
		curr_profile.save()
		responseobject = {}
		return JsonResponse(responseobject)	

	# This should be triggered by pressing Search results button
	# calculate combinations, display it and save it to database under user
	# The courses in the search results are probably in reverse order
	elif 'searchresults' in request.POST:
		ids = curr_profile.faves.split(',')
		course_list = []
		for i in ids:
			if (i != ''):
				course = Course.objects.filter(registrar_id=i)
				course_list.append(course[0])
		combo = combine(course_list, 2)
		if combo == None:
			combination = []
		else: 
			for c in combo:
				comb_str = str(c[len(c) - 1])
				for i in range(len(c) - 2, -1, -1):
					comb_str = comb_str + ', ' + str(c[i])
				combination.append(comb_str)
		print combination

		# save the course combinations to user
		curr_profile.course_combo = combination
		curr_profile.save()

		# render the course combinations
		display = []
		for i in range (0, len(combination))
			display.append("<div class = '" + i + "'>" + combination[i] + " <button type = 'button' class = 'btn btn-danger btn-xs deleteclass' id = " + i + "> x </button> </div>") 

		return render(request, 'home.html', {"combinations": display})

	else:
		favorites = curr_profile.faves
		favorites = favorites.split(",")
		curr_faves = []
		for i in favorites:
			if (i != ''):
				course = Course.objects.filter(registrar_id = i)
				curr_faves.append("<div class = '" + i + "'>" + course[0].deptnum + ": " + course[0].title + " <button type = 'button' class = 'btn btn-danger btn-xs deleteclass' id = " + i + "> x </button> </div>") 
		return render(request, 'home.html', {"favorites": curr_faves})

def get_courses(request):
	if request.is_ajax():
		q = request.GET.get('term', '')
		searchresults = Course.objects.annotate(
			search=SearchVector('title', 'deptnum'),
		).filter(search=q)
		results = []
		for result in searchresults:
			course_json = {}
			course_json = {
				'label': result.deptnum + ": " + result.title,
				'value': result.registrar_id
			}
			# course_json = result.deptnum + ": " + result.title
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