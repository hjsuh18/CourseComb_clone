# -*- coding: utf-8 -*-
from .models import Course, Profile, Combination, Meeting
from django.contrib.postgres.search import SearchVector
import json, cgi, datetime
from django.urls import resolve

from time_compare import time_compare


def filter_course(profile):
	print 'what?'
	queue = profile.faves
	print 'ffilter is the problem'
	queue = queue.split(',')
	combination = profile.combinations.all()

	# reset everything to unfiltered state
	combination.update(filtered=False)

	filters = profile.filter
	must_courses = filters.must_courses
	must_dept = filters.must_dept
	distribution = filters.distribution
	max_dept = filters.max_dept
	no_friday_class = filters.no_friday_class
	no_evening_class = filters.no_evening_class
	ten_am = filters.ten_am
	full = filters.full
	pdf = filters.pdf

	# dist keeps track of which courses are in which distribution area e.g. {'HA':'HIS 314,'}
	dist = dict()
	if distribution != None:
		for x in queue:
			if x == '':
				continue
			else:
				x_area = Course.objects.get(registrar_id=x).area
				if x_area in distribution:
					if x_area in dist:
						dist[x_area].append(x)
					else:
						dist[x_area] = [x]

		# dictionary is empty meaning that none of the courses are in required distribution
		if not dist:
			combination.update(filtered=True)


	time_avoid_course =[]
	if not no_friday_class or not no_evening_class or not ten_am:
		for x in queue:
			not_avoid = False

 			if x == '':
				continue
			else:
				c = Course.objects.get(registrar_id=x)
				primary_meetings = c.meetings.filter(is_primary = True)
				nonprimary_meetings = c.meetings.filter(is_primary = False)

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
						if time_compare(evening, m.end_time) == -1:
							not_avoid_nec = True

					ten = datetime.time(9, 59)
					if ten_am:
						not_avoid_ta = False
						if time_compare(ten, m.start_time) == 1:
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
						if time_compare(evening, m.end_time) == -1:
							not_avoid_nec = True

					ten = datetime.time(9, 59)
					if ten_am:
						not_avoid_ta = False
						if time_compare(ten, m.start_time) == 1:
							not_avoid_ta = True
							
					if not_avoid_nfc and not_avoid_nec and not_avoid_ta:
						not_avoid = True
						break
				if not not_avoid:
					time_avoid_course.append(x)

	departments = dict()
	if max_dept != None:
		for x in queue:
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

	# find pdf only classes in queue
	pdf_only_courses = []
	if pdf:
		for x in queue:
			if x == '':
				continue
				
			c = Course.objects.get(registrar_id=x)
			if c.pdfonly:
				pdf_only_courses.append(x)

	# full classes
	full_classes = []
	if full:
		for x in queue:
			if x == '':
				continue
			c = Course.objects.get(registrar_id=x)
			primary_meetings = c.meetings.filter(is_primary = True)
			class_full = True
			for m in primary_meetings:
				if m.enroll < m.limit:
					class_full = False
					break
			if class_full:
				full_classes.append(x)

	# go through each combination
	for i in range (0, len(combination)):
		# filter if does not contain must have courses
		if must_courses != None:
			for c in must_courses:
				if c not in combination[i].registrar_combo:
					combination[i].filtered = True
					combination[i].save()

		# filter if does not contain must have departments
		if must_dept != None:
			for dept in must_dept:
				if dept not in combination[i].course_combo:
					combination[i].filtered = True
					combination[i].save()

		# filter if does not contain course in each of required distirbution
		for key in dist:
			contains_dist = False
			for course in dist[key]:
				if course in combination[i].registrar_combo:
					contains_dist = True
					break
			if not contains_dist:
				combination[i].filtered = True
				combination[i].save()

		if time_avoid_course != None:
			for c in time_avoid_course:
				if c in combination[i].registrar_combo:
					combination[i].filtered = True
					combination[i].save()

		contains_pdf_only = False
		for c in pdf_only_courses:
			if c in combination[i].registrar_combo:
				contains_pdf_only = True
				break
		if pdf and not contains_pdf_only:
			combination[i].filtered = True
			combination[i].save()

		for c in full_classes:
			if c in combination[i].registrar_combo:
				combination[i].filtered = True
				combination[i].save()

		for d in departments:
			if len(departments[d]) > max_dept:
				cnt = 0
				for x in departments[d]:
					if x in combination[i].registrar_combo:
						cnt = cnt + 1
				if cnt > max_dept:
					combination[i].filtered = True
					combination[i].save()