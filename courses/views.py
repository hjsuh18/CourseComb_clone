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

from .course_filter import filter_course

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
				course = Course.objects.get(registrar_id=i)
				course_list.append(course)
		
		course_num = int(request.POST.get("course_number", ""))
		if course_num > len(course_list):
			# need to show an error message
			responseobject = {}
			return JsonResponse(responseobject)
		registrar_combo = combine(course_list, course_num)

		# if registrar_combo is None, render a message saying no combinations

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

	# user presses update filter
	elif 'filterresults' in request.POST:
		filter_course(curr_profile, dict(request.POST))

		combination = curr_profile.combinations.all()
		response = []
		for i in range (0, len(combination)):
			if combination[i].deleted == True or combination[i].filtered == True:
				continue
			response.append("<div class = 'coursecomb " + str(combination[i].comb_id) + "'>" + str(combination[i]) + " <button type = 'button' class = 'btn btn-danger btn-xs deletecomb' id = " + str(combination[i].comb_id) + "> x </button> </div>")
		responseobject = {'courses_com': json.dumps(response)}
		return JsonResponse(responseobject)

	# user clicks on the filter button on main page
	elif 'click_filter' in request.POST:
		response_course = []
		departments = []
		response_dept = []
		queue = curr_profile.faves.split(',')
		for i in range(0, len(queue)):
			if queue[i] is '':
				continue
			# make form for must take courses
			course = Course.objects.get(registrar_id=queue[i]).deptnum
			temp_course = "<label class='form-check-label' for=" + course + "> " + course + " <input class='form-check-input class-check' type='checkbox' value=" + queue[i] + "></label>"	
			response_course.append(temp_course)

			# make form for must take departmentals
			dept = course.split(' ')[0]
			if dept not in departments:
				departments.append(dept)
				temp_dept = "<label class='form-check-label' for=" + dept + "> " + dept + " <input class='form-check-input dep-check' type='checkbox' value=" + dept + "></label>"
				response_dept.append(temp_dept)
						
		responseobject = {'must_have_courses': json.dumps(response_course), 'must_have_departments': json.dumps(response_dept)}
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
	# LOOKS LIKE THE PLACE TO IMPLEMENT TIME FILTERS/RESOLVE DISPLAY OF TIME CONFLICTS
	elif 'comb_click' in request.GET:
		comb_id = request.GET.get("comb_id", "")
		comb = curr_profile.combinations.get(comb_id=comb_id)
		comb = comb.registrar_combo.split(',')
		comb_schedule = []
		responseobject = {}
		for registrar_id in comb:
			course = Course.objects.get(registrar_id = registrar_id)
			# get primary meeting
			meeting = Meeting.objects.filter(course = course, is_primary = True)
			for m in meeting:
				days = day_convert(m.days)
				newdays = [i+1 for i, j in enumerate(days) if j == 1]
				course_schedule = {'title': course.deptnum + " " + m.section, 'dow': newdays, 'start': m.start_time, 'end':m.end_time}
				comb_schedule.append(course_schedule)
			
			# get non-primary meetings
			meetings = Meeting.objects.filter(course = course, is_primary = False)
			course_classes_schedule = []
			for m in meetings:
				if m.start_time != None:
					days = day_convert(m.days)
					newdays = [i+1 for i, j in enumerate(days) if j == 1]
					class_schedule = {'title': course.deptnum + " " + m.section, 'dow': newdays, 'start': m.start_time, 'end':m.end_time}
					course_classes_schedule.append(class_schedule)
			responseobject[course.deptnum] = json.dumps(course_classes_schedule, default=str)

		responseobject['schedule'] = json.dumps(comb_schedule, default=str)
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