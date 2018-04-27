# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Course, Profile, Combination, Meeting, Filter
from django.contrib.postgres.search import SearchVector
import json, cgi, datetime
from .cas import CASClient
from django.urls import resolve

from combination import combine
from time_compare import day_convert, time_compare

from .course_filter import filter_course

# colorsssssss
lightpalette = ["#E0FFFF", "#D8BFD8", "#FFDEAD", "#DCDCDC", "#FFDAB9", "#BDB76B", "#E6E6FA", "#FFB6C1", "##CD853F", "#B0C4DE"];
darkpalette  = ["#001f3f"];

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
			# s = Course.objects.get(registrar_id=ids[0]).deptnum
			s = ''
			for j in range(0, len(ids)):
				if (ids[j] != ''):
					course = Course.objects.get(registrar_id=ids[j]).deptnum
					# in combination, only show first deptnum of cross-listed courses
					if '/' in course:
						course = course.split('/')
						course = course[0]
					if j == 0:
						s = course
					else:
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
				filtered = False,
				deleted = False
				)
			c.save()
			# possibly need to keep a count of the total number of combination created

		# apply the filters currently stored to profile
		if hasattr(curr_profile, 'filter'):
			filter_course(curr_profile)
		else:
			f = Filter.objects.create(user = curr_profile)

		combination = curr_profile.combinations.all()
		response = []

		for i in range (0, len(combination)):
			if combination[i].deleted == True or combination[i].filtered == True:
				continue
			response.append("<div class = 'coursecomb " + str(combination[i].comb_id) + "'>" + str(combination[i]) + " <button type = 'button' class = 'btn btn-danger btn-xs deletecomb' id = " + str(combination[i].comb_id) + "> x </button> </div>")

		responseobject = {'courses_com': json.dumps(response)}

		return JsonResponse(responseobject)

	# user presses update filter
	elif 'filterresults' in request.POST:
		# update filter fields
		d = dict(request.POST)
		f = Filter.objects.update_or_create(
			user = curr_profile,
			defaults={
				'must_courses': d.get("courses[]"),
				'must_dept': d.get("depts[]"),
				'distribution': d.get("distribution[]"),
				'max_dept': int(d.get("max_dept")[0]),
				'no_friday_class': (d.get("no_friday_class")[0] == 'true'),
				'no_evening_class': (d.get("no_evening_class")[0] == 'true'),
				'ten_am': (d.get("ten_am")[0] == 'true'),
				'full': (d.get("full")[0] == 'true'),
				'pdf': (d.get("pdf")[0] == 'true'),
			}
			)

		filter_course(curr_profile)

		combination = curr_profile.combinations.all()
		response = []
		for i in range (0, len(combination)):
			if combination[i].deleted == True or combination[i].filtered == True:
				continue
			response.append("<div class = 'coursecomb " + str(combination[i].comb_id) + "'>" + str(combination[i]) + " <button type = 'button' class = 'btn btn-xs deletecomb' id = " + str(combination[i].comb_id) + "> x </button> </div>")
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
	elif 'comb_click' in request.GET:
		full_filter = curr_profile.filter.full
		no_friday_class = curr_profile.filter.no_friday_class
		no_evening_class = curr_profile.filter.no_evening_class
		ten_am = curr_profile.filter.ten_am

		comb_id = request.GET.get("comb_id", "")
		comb = curr_profile.combinations.get(comb_id=comb_id)
		comb = comb.registrar_combo.split(',')
		comb_schedule = []
		responseobject = {}

		single_meeting_course = []
		for registrar_id in comb:
			meetings = Course.objects.get(registrar_id = registrar_id).meetings.filter(is_primary=True)
			if len(meetings) == 1:
				single_meeting_course.append(meetings[0])

		for registrar_id in comb:
			course = Course.objects.get(registrar_id = registrar_id)
			course_title = course.deptnum.split("/")[0]
			# get primary meeting
			meeting = list(Meeting.objects.filter(course = course, is_primary = True))

			# if multiple meeting course, get rid of conflicts
			length = len(meeting)
			if length > 1:
				for i in range(length-1, -1, -1):
					for x in single_meeting_course:
						if meeting[i].is_conflict(x):
							meeting.pop(i)
							break

			for m in meeting:
				if full_filter and m.enroll > m.limit:
					continue
				if no_friday_class and 'F' in m.days:
					continue
				if no_evening_class and time_compare(datetime.time(19,00), m.end_time) == 1:
					continue
				if ten_am and time_compare(datetime.time(9,59), m.start_time) == -1:
					continue
				days = day_convert(m.days)
				newdays = [i+1 for i, j in enumerate(days) if j == 1]
				
				course_schedule = {'title': course_title + " " + m.section, 'dow': newdays, 'start': m.start_time, 'end':m.end_time, 'color': lightpalette[int(registrar_id)%10]}
				comb_schedule.append(course_schedule)
			
			# get non-primary meetings
			meetings = Meeting.objects.filter(course = course, is_primary = False)
			course_classes_schedule = []
			for m in meetings:
				if m.start_time != None:
					if full_filter and m.enroll > m.limit:
						continue
					if no_friday_class and 'F' in m.days:
						continue
					if no_evening_class and time_compare(datetime.time(19,00), m.end_time) == 1:
						continue
					if ten_am and time_compare(datetime.time(9,59), m.start_time) == -1:
						continue
					days = day_convert(m.days)
					newdays = [i+1 for i, j in enumerate(days) if j == 1]
					class_schedule = {'title': course_title + " " + m.section, 'dow': newdays, 'start': m.start_time, 'end':m.end_time, 'color': lightpalette[int(registrar_id)%10], 'className':
					'precept_render', 'id': course_title + "-" + m.section}
					course_classes_schedule.append(class_schedule)
			responseobject[course_title] = json.dumps(course_classes_schedule, default=str)

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
				curr_faves.append("<div class = '" + i + "'>" + course[0].deptnum + ": " + course[0].title + " <button type = 'button' class = 'btn btn-xs deleteclass' id = " + i + "> x </button> </div>") 
		for i in range (0, len(combination)):
			if combination[i].deleted == True or combination[i].filtered == True:
				continue
			curr_combs.append("<div class = 'coursecomb " + str(combination[i].comb_id) + "'>" + str(combination[i]) + " <button type = 'button' class = 'btn btn-xs deletecomb' id = " + str(combination[i].comb_id) + "> x </button> </div>")

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