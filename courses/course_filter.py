# -*- coding: utf-8 -*-
from .models import Course, Profile, Combination, Meeting
from django.contrib.postgres.search import SearchVector
import json, cgi
from django.urls import resolve

from time_compare import day_convert

def filter_course(profile, filters):
	queue = profile.faves
	queue = queue.split(',')
	combination = profile.combinations.all()

	# reset everything to unfiltered state
	combination.update(filtered=False)

	# needed distributions
	distribution = filters.get("distribution[]")
	# d keeps track of which courses are in which distribution area e.g. {'HA':'HIS 314,'}
	d = dict()
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

	# go through each combination, and see if it contains a course in each of required distirbution
	for i in range (0, len(combination)):
		for key in d:
			contains_dist = False
			for course in d[key]:
				if course in combination[i].registrar_combo:
					contains_dist = True
					break
			if not contains_dist:
				combination[i].filtered = True
				combination[i].save()
				print "hello"

	max_dept = filters.get("max_dept")	
	time = filters.get("time[]")
	full = filters.get("full")
	pdf = filters.get("pdf")

	print 'distribution: ', distribution
	print 'max_dept: ', max_dept
	print 'time: ', time
	print 'full: ', full
	print 'pdf: ', pdf
