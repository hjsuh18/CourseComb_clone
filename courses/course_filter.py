# -*- coding: utf-8 -*-
from .models import Course, Profile, Combination, Meeting
from django.contrib.postgres.search import SearchVector
import json, cgi, datetime
from django.urls import resolve

from time_compare import time_compare

# Apply the filters that are saved to the profile
# If filtered, save 'filtered' field of combination as True
def filter_course(profile):
	# queue is a list of courses enrolled
	queue = profile.faves
	queue = queue.split(',')

	# combination is all the combinations saved to profile
	combination = profile.combinations.all()

	# reset everything to unfiltered state
	combination.update(filtered=False)

	# get all the fields of filter
	filters = profile.filter
	must_distribution = filters.distribution
	must_courses = filters.must_courses
	must_dept = filters.must_dept
	max_dept = filters.max_dept
	no_friday_class = filters.no_friday_class
	no_evening_class = filters.no_evening_class
	after_ten_am = filters.after_ten_am
	full = filters.full
	pdf = filters.pdf


	# dist keeps track of which courses are in which distribution area e.g. {'HA':'HIS 314,'}
	dist = get_dist(must_distribution, queue)
	# if a distribution has no courses, no combinations are possible
	for key in dist:
		if not dist[key]:
			combination.update(filtered=True)
			return

	# make dictionary of departments that have more courses than maximum allowed
	max_departments = get_max_dept(max_dept, queue)

	# make array of courses that are not allowed due to filter time constraints
	time_avoid_course = get_bad_time_course(no_friday_class, no_evening_class, after_ten_am, queue)

	# make array of full classes in queue
	full_classes = get_full_classes(full, queue)

	# make array of pdf only classes in queue
	pdf_only_courses = get_pdf_only(pdf, queue)

	# go through each combination
	for i in range (0, len(combination)):
		already_filtered = False
		# filter if does not contain must have courses
		if must_courses != None:
			for c in must_courses:
				if c not in combination[i].registrar_combo:
					combination[i].filtered = True
					already_filtered = True
					combination[i].save()

		# filter if does not contain must have departments
		if not already_filtered and must_dept != None:
			for dept in must_dept:
				if dept not in combination[i].course_combo:
					combination[i].filtered = True
					already_filtered = True
					combination[i].save()

		# filter if does not contain course in each of required distirbution
		if not already_filtered:
			for key in dist:
				contains_dist = False
				for course in dist[key]:
					if course in combination[i].registrar_combo:
						contains_dist = True
						break
				if not contains_dist:
					combination[i].filtered = True
					already_filtered = True
					combination[i].save()

		# max dept filter
		if not already_filtered:
			for d in max_departments:
				cnt = 0
				for x in max_departments[d]:
					if x in combination[i].registrar_combo:
						cnt = cnt + 1
				if cnt > max_dept:
					combination[i].filtered = True
					already_filtered = True
					combination[i].save()

		# time restraint filter
		if not already_filtered:
			if time_avoid_course != None:
				for c in time_avoid_course:
					if c in combination[i].registrar_combo:
						combination[i].filtered = True
						already_filtered = True
						combination[i].save()

		# full classes filter
		if not already_filtered:
			for c in full_classes:
				if c in combination[i].registrar_combo:
					combination[i].filtered = True
					already_filtered = True
					combination[i].save()

		# pdf filter
		if not already_filtered:
			contains_pdf_only = False
			for c in pdf_only_courses:
				if c in combination[i].registrar_combo:
					contains_pdf_only = True
					break
			if pdf and not contains_pdf_only:
				combination[i].filtered = True
				combination[i].save()

# returns a dictionary of must_distribution:courses relationship
def get_dist(must_distribution, course_queue):
	dist = dict()

	if must_distribution != None:
		# initialize the dist dictionary
		for i in range(0, len(must_distribution)):
			dist[must_distribution[i]] = []

		# put courses in distribution categories in dist dictionary
		for x in course_queue:
			if x == '':
				continue
			else:
				x_area = Course.objects.get(registrar_id=x).area
				# if distribution of course is required, update field in dist
				if x_area in dist:
					dist[x_area].append(x)

	return dist

# returns an array of pdf only classes in course queue
def get_pdf_only(pdf_filter, course_queue):
	pdf_only_courses = []
	if pdf_filter:
		for x in course_queue:
			if x == '':
				continue
			
			# append pdf only courses in course queue
			c = Course.objects.get(registrar_id=x)
			if c.pdfonly:
				pdf_only_courses.append(x)

	return pdf_only_courses

# returns an array of full classes in course queue
def get_full_classes(full_filter, course_queue):
	full_classes = []
	if full_filter:
		for x in course_queue:
			if x == '':
				continue
			c = Course.objects.get(registrar_id=x)
			primary_meetings = c.meetings.filter(is_primary = True)

			# if every primary meeting is full, append to full classes array
			class_full = True
			for m in primary_meetings:
				if m.enroll < m.limit:
					class_full = False
					break
			if class_full:
				full_classes.append(x)
	return full_classes

# returns an array of courses with bad times
def get_bad_time_course(no_friday_class, no_evening_class, after_ten_am, course_queue):
	time_avoid_course =[]
	if no_friday_class or no_evening_class or after_ten_am:
		for x in course_queue:
			# initialize such that x is not a course to be avoided
			not_avoid = False

 			if x == '':
				continue

			# get primary and nonprimary meetings of course
			c = Course.objects.get(registrar_id=x)
			primary_meetings = c.meetings.filter(is_primary = True)
			nonprimary_meetings = c.meetings.filter(is_primary = False)

			# filter primary meetings by time
			for m in primary_meetings:
				not_avoid_nfc = True
				not_avoid_nec = True
				not_avoid_ta = True

				if no_friday_class:
					not_avoid_nfc = False
					if 'F' not in m.days:
						not_avoid_nfc = True

				evening = datetime.time(19, 00)
				if no_evening_class:
					not_avoid_nec = False
					if time_compare(evening, m.end_time) != 1:
						not_avoid_nec = True

				ten = datetime.time(9, 59)
				if after_ten_am:
					not_avoid_ta = False
					if time_compare(ten, m.start_time) != -1:
						not_avoid_ta = True

				if not_avoid_nfc and not_avoid_nec and not_avoid_ta:
					not_avoid = True
					break

			if not not_avoid:
				time_avoid_course.append(x)
				continue

			# all non primary meetings do not meet 
			for m in nonprimary_meetings:
				not_avoid = False
				not_avoid_nfc = True
				not_avoid_nec = True
				not_avoid_ta = True

				if no_friday_class:
					not_avoid_nfc = False
					if 'F' not in m.days:
						not_avoid_nfc = True

				evening = datetime.time(19, 00)
				if no_evening_class:
					not_avoid_nec = False
					if time_compare(evening, m.end_time) != 1:
						not_avoid_nec = True

				ten = datetime.time(9, 59)
				if after_ten_am:
					not_avoid_ta = False
					if time_compare(ten, m.start_time) != -1:
						not_avoid_ta = True
						
				if not_avoid_nfc and not_avoid_nec and not_avoid_ta:
					not_avoid = True
					break
			if not not_avoid:
				time_avoid_course.append(x)

	return time_avoid_course

# return a dictionary with key as departments whose number of courses is above max_dept
# value is an array of courses in that department
def get_max_dept(max_dept_filter, course_queue):
	departments = dict()
	if max_dept_filter != None:
		# place courses into every department they are associated with
		for x in course_queue:
			if x == '':
				continue
			deptnum = Course.objects.get(registrar_id=x).deptnum
			deptnum = deptnum.split('/')
			for a in deptnum:
				a = a.split(' ')
				if departments.get(a[0]) == None:
					departments[a[0]] = [x]
				else:
					departments[a[0]].append(x)

	# if the number of courses in department does not exceed max dept number, no need to consider it
	for k, v in departments.items():
		if len(v) <= max_dept_filter:
			del departments[k]

	return departments