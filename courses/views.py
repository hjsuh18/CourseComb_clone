# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Course, Profile, Combination, Meeting, Filter, Favorite
from django.contrib.postgres.search import SearchVector
import json, cgi, datetime
from .cas import CASClient
from django.urls import resolve
from collections import OrderedDict

from combination import combine
from time_compare import day_convert, time_compare

from .course_filter import filter_course

# colorsssssss
lightpalette = ["#E0FFFF", "#D8BFD8", "#FFDEAD", "#DCDCDC", "#FFDAB9", "#BDB76B", "#74b9ff", "#FFB6C1", "#2EC4B6", "#CD853F", "#B0C4DE"];
darkpalette  = ["#001f3f"];

# loads landing page
def landing(request):
	if request.user.is_authenticated:
		return HttpResponseRedirect('/home')
	else:
		return render(request, 'landing.html')

# loads about page
def about(request):
	return render(request, 'about.html')

# loads feedback page
def feedback(request):
	return render(request, 'feedback.html')

# loads favorites page
def favorites(request):
	# delete a favorited schedule
	curr_profile = request.user.profile
	if 'deletefav' in request.POST:
		fav_data = json.loads(request.POST.get("fav_data", ""))
		fav_object = curr_profile.favorites.get(favorite_fields = fav_data)
		fav_object.delete()
		return JsonResponse({})
	else:
		
		schedule_favorites = curr_profile.favorites.all()
		favoriteobject = []
		for i in schedule_favorites:
			favorite = []
			favorite.append(i.name)
			favorite.append(i.courses)
			favorite.append(i.favorite_fields)
			favoriteobject.append(favorite)

		return render(request, 'favorites.html', {"favorites": json.dumps(favoriteobject)})

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

			evaluation = Course.objects.get(registrar_id=registrar_id).evals
			url = Course.objects.get(registrar_id=registrar_id).url

			responseobject = {'newclass': class_name, 'newid': registrar_id, 'eval': evaluation, 'url': url}
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
	elif 'searchresults' in request.POST:
		# update filter fields
		d = dict(request.POST)

		ids = curr_profile.faves.split(',')

		# delete all saved combinations
		curr_profile.combinations.all().delete()

		if len(ids) < 2:
			responseobject = {'no_courses': "Please add courses to your Courses of Interest"}
			return JsonResponse(responseobject)

		# make must_courses array from priority 
		priority = d.get("priority[]")
		must_courses = []
		for i in range (0, len(priority)):
			# 3 is must-have course
			if priority[i] == '3':
				must_courses.append(priority[i - 1])

		f = Filter.objects.update_or_create(
			user = curr_profile,
			defaults={
				'number_of_courses': int(d.get("number_of_courses")[0]),
				'must_courses': must_courses,
				'must_dept': d.get("depts[]"),
				'distribution': d.get("distribution[]"),
				'priority': d.get("priority[]"),
				'max_dept': int(d.get("max_dept")[0]),
				'no_friday_class': (d.get("no_friday_class")[0] == 'true'),
				'no_evening_class': (d.get("no_evening_class")[0] == 'true'),
				'after_ten_am': (d.get("after_ten_am")[0] == 'true'),
				'full': (d.get("full")[0] == 'true'),
				'pdf': (d.get("pdf")[0] == 'true'),
			}
			)

		# order the courses in priority specified by user
		priority = curr_profile.filter.priority
		high_priority = []
		medium_priority = []
		low_priority = []
		for i in ids:
			if (i != ''):
				# p is 1, 2 or 3 depending on priority of course i
				# 1 is low priority, 3 is high priority
				p = int(priority[priority.index(i) + 1])
				course = Course.objects.get(registrar_id=i)
				if p == 1:
					low_priority.append(course)
				elif p == 2:
					medium_priority.append(course)
				else:
					high_priority.append(course)

		course_list = high_priority + medium_priority + low_priority

		course_num = curr_profile.filter.number_of_courses
		if course_num > len(course_list):
			# need to show an error message
			responseobject = {'course_number': "You don't have enough courses selected on your Courses of Interest."}
			return JsonResponse(responseobject)

		registrar_combo = combine(course_list, course_num)

		# if registrar_combo is None, render a message saying no combinations
		if not registrar_combo:
			responseobject = {'no_combo': "There are no possible combinations for your selected courses due to time conflicts"}
			return JsonResponse(responseobject)

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
		for i in range(0, len(registrar_combo)):
			# save course combination into database
			c = Combination.objects.create(
				user = curr_profile,
				comb_id = i,
				course_combo = course_combo[i],
				registrar_combo = registrar_combo[i],
				filtered = False,
				)
			c.save()

		filter_course(curr_profile)

		combination = curr_profile.combinations.all()
		response = []

		count = 0
		for i in range (0, len(combination)):
			if combination[i].filtered == True:
				continue
			count = count + 1
			response.append("<div class = 'coursecomb " + str(combination[i].comb_id) + "'>" + str(count) + ". " + str(combination[i]) + "</div>")

		if not response:
			responseobject = {'filter_restrict': 'There are no possible combinations that fit all your selected preferences.'}
			return JsonResponse(responseobject)

		responseobject = {'courses_com': json.dumps(response)}

		return JsonResponse(responseobject)

	# user clicks on the filter button on main page
	elif 'click_filter' in request.POST:
		response_course = []
		departments = []
		response_dept = []
		response_priority = []
		responseobject = dict()

		queue = curr_profile.faves.split(',')

		# get the inputs from filter from before to upload saved fields
		previous_course_priority = []
		previous_must_dept = []

		# if there is already a filter set, set filter values as previous saved values
		if hasattr(curr_profile, 'filter'):
			responseobject['filter_coursenum'] = curr_profile.filter.number_of_courses
			responseobject['filter_maxdept'] = curr_profile.filter.max_dept
			responseobject['filter_nofridayclass'] = curr_profile.filter.no_friday_class
			responseobject['filter_noeveningclass'] = curr_profile.filter.no_evening_class
			responseobject['filter_aftertenam'] = curr_profile.filter.after_ten_am
			responseobject['filter_full'] = curr_profile.filter.full
			responseobject['filter_pdf'] = curr_profile.filter.pdf
			responseobject['filter_distribution'] = json.dumps(curr_profile.filter.distribution)

			previous_course_priority = curr_profile.filter.priority
			previous_must_dept = curr_profile.filter.must_dept
		# Filter has never been set, so set fields as default values
		else:
			responseobject['filter_coursenum'] = 1
			responseobject['filter_maxdept'] = 5
			responseobject['filter_nofridayclass'] = False
			responseobject['filter_noeveningclass'] = False
			responseobject['filter_aftertenam'] = False
			responseobject['filter_full'] = False
			responseobject['filter_pdf'] = False
			responseobject['filter_distribution'] = json.dumps([])

		# go through queue and construct must have courses, must have departments, priority of course
		for i in range(0, len(queue)):
			if queue[i] is '':
				continue
			
			# html element for each filter category
			temp_course = ''
			temp_dept = ''
			temp_priority = ''

			# only get the first listed coruse name
			course = Course.objects.get(registrar_id=queue[i]).deptnum
			course = course.split('/')[0]

			# restore course priority value if it was saved from previous filter
			if previous_course_priority != None and queue[i] in previous_course_priority:
				x = previous_course_priority.index(queue[i])
				p = int(previous_course_priority[x + 1])
				if p == 1:
					temp_priority = "<label class='form-check-label' for=" + course + "-priority> <span class='filter_label_priority'>" + course + "</span><select class= 'form-control-in-line priority-select' id=" + queue[i] + ">" + course + "  <option selected='selected' value='1'>Low</option><option value='2'>Medium</option><option value='3'>Must-have</option></select>"
				elif p == 2:
					temp_priority = "<label class='form-check-label' for=" + course + "-priority> <span class='filter_label_priority'>" + course + "</span><select class= 'form-control-in-line priority-select' id=" + queue[i] + ">" + course + "  <option value='1'>Low</option><option selected='selected' value='2'>Medium</option><option value='3'>Must-have</option></select>"
				else:
					temp_priority = "<label class='form-check-label' for=" + course + "-priority> <span class='filter_label_priority'>" + course + "</span><select class= 'form-control-in-line priority-select' id=" + queue[i] + ">" + course + "  <option value='1'>Low</option><option value='2'>Medium</option><option selected='selected' value='3'>Must-have</option></select>"
			else:
				temp_priority = "<label class='form-check-label' for=" + course + "-priority> <span class='filter_label_priority'>" + course + "</span><select class= 'form-control-in-line priority-select' id=" + queue[i] + ">" + course + "  <option value='1'>Low</option><option value='2'>Medium</option><option value='3'>Must-have</option></select>"


			# restore must dept form value
			dept = course.split(' ')[0]
			if dept not in departments:
				departments.append(dept)
				if previous_must_dept != None and dept in previous_must_dept:
					temp_dept = "<label class='form-check-label' for=" + dept + "> <span class='filter_label'>" + dept + "</span> <input class='form-check-input dep-check' type='checkbox' value=" + dept + " checked></label>"
				else:
					temp_dept = "<label class='form-check-label' for=" + dept + "> <span class='filter_label'>" + dept + "</span> <input class='form-check-input dep-check' type='checkbox' value=" + dept + "></label>"
				response_dept.append(temp_dept)
			
			response_course.append(temp_course)
			response_priority.append(temp_priority)

		
		responseobject['must_have_departments'] = json.dumps(response_dept)
		responseobject['course_priority'] = json.dumps(response_priority)

		return JsonResponse(responseobject)

	# user clicks on the filter button on main page
	elif 'reset_filter' in request.POST:
		departments = []
		response_dept = []
		response_priority = []
		queue = curr_profile.faves.split(',')

		# reset the saved filters
		if hasattr(curr_profile, 'filter'):
			curr_profile.filter.number_of_courses=1
			curr_profile.filter.must_courses = []
			curr_profile.filter.must_dept = []
			curr_profile.filter.distribution = []
			curr_profile.filter.priority = []
			curr_profile.filter.max_dept = 5
			curr_profile.filter.no_friday_class=False
			curr_profile.filter.no_evening_class=False
			curr_profile.filter.after_ten_am=False
			curr_profile.filter.full=False
			curr_profile.filter.pdf=False
			
			curr_profile.filter.save()


		for i in range(0, len(queue)):
			if queue[i] is '':
				continue

			course = Course.objects.get(registrar_id=queue[i]).deptnum
			course = course.split('/')[0]

			temp_priority = "<label class='form-check-label' for=" + course + "-priority> <span class='filter_label_priority'>" + course + "</span><select class= 'form-control-in-line priority-select' id=" + queue[i] + ">" + course + "  <option value='1'>Low</option><option value='2'>Medium</option><option value='3'>Must-have</option></select>"
			response_priority.append(temp_priority)

			dept = course.split(' ')[0]
			if dept not in departments:
				departments.append(dept)
				temp_dept = "<label class='form-check-label' for=" + dept + "> <span class='filter_label'>" + dept + " </span><input class='form-check-input dep-check' type='checkbox' value=" + dept + "></label>"
				response_dept.append(temp_dept)

		responseobject = dict()
		responseobject['must_have_departments'] = json.dumps(response_dept)
		responseobject['course_priority'] = json.dumps(response_priority)

		return JsonResponse(responseobject)


	# show schedule of selected combination
	elif 'comb_click' in request.GET:
		full_filter = curr_profile.filter.full
		no_friday_class = curr_profile.filter.no_friday_class
		no_evening_class = curr_profile.filter.no_evening_class
		after_ten_am = curr_profile.filter.after_ten_am

		comb_id = request.GET.get("comb_id", "")
		comb = curr_profile.combinations.get(comb_id=comb_id)
		comb = comb.registrar_combo.split(',')
		
		responseobject = {}

		single_meeting_course = []
		for registrar_id in comb:
			meetings = Course.objects.get(registrar_id = registrar_id).meetings.filter(is_primary=True)
			if len(meetings) == 1:
				single_meeting_course.append(meetings[0])

		course_names = []
		comb_schedule = {}
		for registrar_id in comb:
			course = Course.objects.get(registrar_id = registrar_id)
			course_title = course.deptnum.split("/")[0]
			course_names.append(course_title)
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
			course_schedule_all = []
			# this will never get rid of all meetings, since if all meetings do not meet conditions
			# it would have been filtered out in course_filter
			for m in meeting:
				if full_filter and m.enroll >= m.limit:
					continue
				if no_friday_class and 'F' in m.days:
					continue
				if no_evening_class and time_compare(datetime.time(19,00), m.end_time) == 1:
					continue
				if after_ten_am and time_compare(datetime.time(9,59), m.start_time) == -1:
					continue
				days = day_convert(m.days)
				newdays = [i+1 for i, j in enumerate(days) if j == 1]
				
				if length > 1:
					course_schedule = {'title': course_title + " " + m.section, 'dow': newdays, 'start': m.start_time, 'end':m.end_time, 'color': lightpalette[int(registrar_id)%11], 'className':
					'precept_render primary', 'id': course_title + "-" + m.section}
				else:
					course_schedule = {'title': course_title + " " + m.section, 'dow': newdays, 'start': m.start_time, 'end':m.end_time, 'color': lightpalette[int(registrar_id)%11]}
				course_schedule_all.append(course_schedule)
				
			
			comb_schedule[course_title] = json.dumps(course_schedule_all, default = str)
			# get non-primary meetings
			meetings = Meeting.objects.filter(course = course, is_primary = False)
			class_types = set()
			course_classes = {}
			for m in meetings:
				class_types.add(m.section[0])
			for class_type in class_types:
				course_classes[class_type] = []
			for m in meetings:
				if m.start_time != None:
					# this will never get rid of all meetings, since if all meetings do not meet conditions
					# it would have been filtered out in course_filter
					if full_filter and m.enroll > m.limit:
						continue
					if no_friday_class and 'F' in m.days:
						continue
					if no_evening_class and time_compare(datetime.time(19,00), m.end_time) == 1:
						continue
					if after_ten_am and time_compare(datetime.time(9,59), m.start_time) == -1:
						continue
					days = day_convert(m.days)
					newdays = [i+1 for i, j in enumerate(days) if j == 1]
					class_schedule = {'title': course_title + " " + m.section, 'dow': newdays, 'start': m.start_time, 'end':m.end_time, 'color': lightpalette[int(registrar_id)%11], 'className':
					'precept_render', 'id': course_title + "-" + m.section}
					class_type = m.section[0]
					course_classes[class_type].append(class_schedule)

			empty_class = True
			for class_type in class_types:
				if course_classes[class_type] != []:
					empty_class = False
			if empty_class:
				course_classes = {}
			responseobject[course_title] = json.dumps(course_classes, default=str)

		comb_schedule['names'] = json.dumps(course_names, default = str)
		responseobject['schedule'] = json.dumps(comb_schedule, default=str)
		return JsonResponse(responseobject)	
	
	elif 'save_schedule' in request.POST:
		# Comment this in and comment all the below things out except return statement to delete all favorites
		# responseobject = {}
		# Favorite.objects.all().delete()
		# print "hello"
		calendar_name = request.POST.get("calendar_name", "")
		calendar_courses = request.POST.get("calendar_courses", "")
		calendar = json.loads(request.POST.get("calendar_data", ""))
		calendar_data = []
		for i in calendar:
			calendar_data.append(json.dumps(i))

		curr_favorites = curr_profile.favorites.all()
		curr_favorite_fields = []
		for i in curr_favorites:
			curr_favorite_fields.append(i.favorite_fields)
		
		responseobject = {}
		if calendar_data in curr_favorite_fields:
			responseobject = {'error': 'This schedule is already saved'}
		else:
			f = Favorite.objects.create(
				user = curr_profile,
				name = calendar_name,
				courses = calendar_courses,
				favorite_fields = calendar_data)
			responseobject = {'message': 'Schedule successfully saved!'}

		return JsonResponse(responseobject)
	else:
		favorites = curr_profile.faves
		favorites = favorites.split(",")
		combination = curr_profile.combinations.all()

		curr_faves = []
		curr_combs = []
		for i in favorites:
			if (i != ''):
				course = Course.objects.get(registrar_id = i)
				curr_faves.append("<div class = 'refreshed-courses container " + i + "'>" + course.deptnum + ": " + course.title + 
					'<div class="overlay"> <span class = "row1"> \
					<a href="' + course.url + '" target="_blank"><div class = "registrar"> <span class = "text"> <i class="fa fa-info" aria-hidden="true"></i> </span> </div></a> \
        			<a href="' + course.evals + '"target="_blank"><div class = "reviews"> <span class = "text"> <i class="fas fa-chart-pie"></i> </span> </div></a> \
        			<div class = "deletebutton deleteclass" id ="' + i + '"> <span class = "text"> <i class="fa fa-times" aria-hidden="true"></i> </span> </div> </span> </div> </div>')

		count = 0
		for i in range (0, len(combination)):
			if combination[i].filtered == True:
				continue
			count = count + 1
			curr_combs.append("<div class = 'coursecomb " + str(combination[i].comb_id) + "'>" + str(count) + ". " + str(combination[i]) + "</div>")

		# -1 because there is always an empty string
		queue_length = len(favorites) - 1
		combination_length = len(curr_combs)

		# Test complete new user by deleting user profile
		# request.user.delete()
		# print 'ACCOUNT DELETED'

		return render(request, 'home.html', {"favorites": curr_faves, "combinations": curr_combs, "queue_length": queue_length, "combination_length": combination_length})

# get courses for autocomplete functionality
def get_courses(request):
	if request.is_ajax():
		q = request.GET.get('term', '')
		searchresults = Course.objects.filter(deptnum__icontains = q)
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