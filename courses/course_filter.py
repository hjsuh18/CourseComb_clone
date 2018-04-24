# -*- coding: utf-8 -*-
from .models import Course, Profile, Combination, Meeting
from django.contrib.postgres.search import SearchVector
import json, cgi
from django.urls import resolve

from time_compare import day_convert

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

	# go through each combination
	for i in range (0, len(combination)):
		# filter if does not contain must have courses
		if must_courses != None:
			for c in must_courses:
				if c not in combination[i].registrar_combo:
					combination[i].filtered = True
					combination[i].save()
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

	

	print 'distribution: ', distribution
	print 'max_dept: ', max_dept
	print 'time: ', time
	print 'full: ', full
	print 'pdf: ', pdf
