# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Course, Profile, Combination, Meeting
from django.contrib.postgres.search import SearchVector
import json, cgi
from .cas import CASClient
from django.urls import resolve

from combination import combine
from time_compare import day_convert

# temporarily so that heroku problem can be identified
def landing(request):
	return render(request, 'landing.html')


def home(request):
	curr_profile = request.user.profile

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
		registrar_combo = combine(course_list, 2)

		# make course_combo array
		course_combo = []
		for i in range(0, len(registrar_combo)):
			ids = registrar_combo[i].split(',')
			s = Course.objects.get(registrar_id=ids[0]).deptnum
			for j in range(1, len(ids)):
				if (ids[j] != ''):
					course = Course.objects.get(registrar_id=ids[j]).deptnum
					s = s + ', ' + course
			course_combo.append(s)

		# create course combination object for each combination and link to user
		curr_profile.combinations.all().delete()

		for i in range(0, len(registrar_combo)):
			# save course combination into database
			c = Combination.objects.create(
				user = curr_profile,
				comb_id = i,
				course_combo = course_combo[i],
				registrar_combo = registrar_combo[i],
				# should initial filtering take place here?
				filtered = False,
				deleted = False
				)
			c.save()
			# possibly need to keep a count of the total number of combination created

		response = []
		# render the course combinations
		for i in range (0, len(course_combo)):
			temp = "<div class = 'coursecomb " + str(i) + "'>" + course_combo[i] + " <button type = 'button' class = 'btn btn-danger btn-xs deletecomb' id = " + str(i) + "> x </button> </div>"
			response.append(temp)
		responseobject = {'courses_com': json.dumps(response)}
		return JsonResponse(responseobject)

	# delete course combination in database
	elif 'deletecomb' in request.POST:
		comb_id = request.POST.get("comb_id", "")
		c = curr_profile.combinations.get(comb_id=comb_id)
		c.deleted = True
		c.save()
		responseobject = {}
		return JsonResponse(responseobject)	

	# show schedule of selected combination
	elif 'comb_click' in request.GET:
		comb_id = request.GET.get("comb_id", "")
		comb = curr_profile.combinations.get(comb_id=comb_id)
		comb = comb.registrar_combo.split(',')
		comb_schedule = []
		for i in comb:
			course = Course.objects.get(registrar_id = i)
			meeting = Meeting.objects.filter(course = course, is_primary = True)[0]
			days = day_convert(meeting.days)
			newdays = [i+1 for i, j in enumerate(days) if j == 1]
			course_schedule = {'title': course.deptnum + ": " + course.title, 'dow': newdays, 'start': meeting.start_time, 'end':meeting.end_time}
			comb_schedule.append(course_schedule)
		responseobject = {'schedule': json.dumps(comb_schedule, default=str)}
		return JsonResponse(responseobject)	

	else:
		favorites = curr_profile.faves
		favorites = favorites.split(",")
		combination = curr_profile.combinations.all()

		curr_faves = []
		curr_combs = []
		for i in favorites:
			if (i != ''):
				course = Course.objects.filter(registrar_id = i)
				curr_faves.append("<div class = '" + i + "'>" + course[0].deptnum + ": " + course[0].title + " <button type = 'button' class = 'btn btn-danger btn-xs deleteclass' id = " + i + "> x </button> </div>") 
		for i in range (0, len(combination)):
			if combination[i].deleted == True or combination[i].filtered == True:
				continue
			curr_combs.append("<div class = 'coursecomb " + str(combination[i].comb_id) + "'>" + str(combination[i]) + " <button type = 'button' class = 'btn btn-danger btn-xs deletecomb' id = " + str(combination[i].comb_id) + "> x </button> </div>")

		return render(request, 'home.html', {"favorites": curr_faves, "combinations": curr_combs})

# get courses for autocomplete functionality
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