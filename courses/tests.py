# Some of the code was borrowed from ReCourse, but most was written by CourseComb
import unittest
from django.conf import settings
from django.test import Client
import courses.views
from django.contrib.auth.models import User
import datetime, re, json
from django.db.models import Max, Min
from random import randint
from courses.models import Course
from courses.combination import combine
from courses.time_compare import day_compare

# Tests course conflict filter
# Run by python manage.py shell < courses/tests.py
class TestConflict(unittest.TestCase):

	# helper function for generating random Course objects
	# taken from https://www.peterbe.com/plog/getting-random-rows-postgresql-django with some modifications
	def random_queryset_elements(self, qs, number):
		global Max
		global Min
		global randint
		assert number <= 10000, 'too large'
		max_pk = qs.aggregate(Max('pk'))['pk__max']
		min_pk = qs.aggregate(Min('pk'))['pk__min']
		ids = set()
		while len(ids) < number:
			next_pk = randint(min_pk, max_pk)
			while next_pk in ids:
				next_pk = randint(min_pk, max_pk)
			try:
				found = qs.get(pk=next_pk)
				ids.add(found.pk)
				yield found
			except qs.model.DoesNotExist:
				pass

	# helper function to check for conflicts
	# courses is an array of registrar_id's 
	# conflicting_days is a string
	# conflicting_times is an array of datetime objects
	def check_conflict(self, courses, conflicting_days, conflicting_times):
		
		global day_compare
		has_conflict = False
		for c in courses:
			# check that at least one of the primary meetings doesn't conflict
			all_conflict = True
			
			c_meetings = Course.objects.get(registrar_id = c).meetings.filter(is_primary=True)
			
			if len(c_meetings) == 1:
				c_meetings = c_meetings[0]
				if not day_compare(c_meetings.days, conflicting_days):
					all_conflict = False
					continue
				if c_meetings.start_time == None:
					all_conflict = False
					continue
				m_start = c_meetings.start_time
				m_end = c_meetings.end_time
				if not any(((m_start <= end) and (start <= m_end)) for (start, end) in conflicting_times):
					all_conflict = False

				if all_conflict:
					has_conflict = True
					print c # print conflicting course
					break

		return has_conflict

	# actual test function
	def test_conflict(self):
		global Client
		global User
		global Course
		global combine

		# Create test user
		c = Client()
		user = User.objects.create_user(username='tester21', password='test')
		c.force_login(user=user)

		has_conflict = False

		# Generate 7 random courses and choose 4
		random_7 = self.random_queryset_elements(Course.objects.all(), 7)
		registrar_combo = combine(list(random_7), 4)

		# Go through each combo to check if there are time conflicts
		if registrar_combo is not None:
			for com in registrar_combo:
				combo = com.split(",")
				course_0 = Course.objects.get(registrar_id = combo[0])
				conflict = course_0.meetings.filter(is_primary=True)
				if len(conflict) == 1:
					conflict = conflict[0]
					conflict_days = conflict.days
					conflict_times = [(conflict.start_time, conflict.end_time)]
					courses_array = combo[1:]
					has_conflict = self.check_conflict(courses_array, conflict_days, conflict_times)

		user.delete()
		self.assertFalse(has_conflict)

# Running the tests
test_classes_to_run = [TestConflict]

loader = unittest.TestLoader()

suites_list = []
for test_class in test_classes_to_run:
	suite = loader.loadTestsFromTestCase(test_class)
	suites_list.append(suite)

big_suite = unittest.TestSuite(suites_list)

runner = unittest.TextTestRunner(verbosity=2)
results = runner.run(big_suite)
