# -*- coding: utf-8 -*-
from .models import Course, Profile, Combination, Meeting
from django.contrib.postgres.search import SearchVector
import json, cgi, datetime
from django.urls import resolve

from time_compare import time_compare


def filter_course(profile):
	queue = profile.faves
	queue = queue.split(',')
	combination = profile.combinations.all()

	# reset everything to unfiltered state
	combination.update(filtered=False)

	filters = profile.filter
	must_courses = filters.must_courses
	must_dept = filters.must_dept
	distribution = filters.distribution
	max_dept = filters.max_dept
	time = filters.time
	full = filters.full
	pdf = filters.pdf

	# dist keeps track of which courses are in which distribution area e.g. {'HA':'HIS 314,'}
	d = dict()
	if distribution != None:
		for x in queue:
			if x == '':
				continue
			else:
				x_area = Course.objects.get(registrar_id=x).area
				if x_area in distribution:
					if x_area in d:
						d[x_area].append(x)
					else:
						d[x_area] = [x]

		# dictionary is empty meaning that none of the courses are in required distribution
		if not d:
			combination.update(filtered=True)


	time_avoid_course =[]
	if time != None:
		no_friday_class = False
		no_evening_class = False
		ten_am = False

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

					if 'no-friday-class' in time:
						not_avoid_nfc = False
						if 'F' not in m.days:
							not_avoid_nfc = True

					evening = datetime.time(19, 00)
					if 'no-evening-class' in time:
						not_avoid_nec = False
						if time_compare(evening, m.end_time) == -1:
							not_avoid_nec = True

					ten = datetime.time(9, 59)
					if 'ten_am' in time:
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

					if 'no-friday-class' in time:
						not_avoid_nfc = False
						if 'F' not in m.days:
							not_avoid_nfc = True

					evening = datetime.time(19, 00)
					if 'no-evening-class' in time:
						not_avoid_nec = False
						if time_compare(evening, m.end_time) == -1:
							not_avoid_nec = True

					ten = datetime.time(9, 59)
					if 'ten_am' in time:
						not_avoid_ta = False
						if time_compare(ten, m.start_time) == 1:
							not_avoid_ta = True
							
					if not_avoid_nfc and not_avoid_nec and not_avoid_ta:
						not_avoid = True
						break
				if not not_avoid:
					time_avoid_course.append(x)

	# find pdf only classes in queue
	pdf_only_courses = []
	if pdf:
		for x in queue:
			if x == '':
				continue
				
			c = Course.objects.get(registrar_id=x)
			if c.pdfonly:
				pdf_only_courses.append(x)

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
		for key in d:
			contains_dist = False
			for course in d[key]:
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



	

	print 'max_dept: ', max_dept
	print 'full: ', full
	print 'pdf: ', pdf
