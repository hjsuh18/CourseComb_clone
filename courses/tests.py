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

# Tests course conflict filter
class TestConflict(unittest.TestCase):
	# only works when run with python manage.py shell --plain < courses/tests.py and with no new lines in between

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

	def check_conflict(self, courses, conflicting_days, conflicting_times):
		# helper method to check for conflicts, best to use with just one class
		has_conflict = False
		for c in courses:
			# check that at least one of the primary meetings doesn't conflict
			all_conflict = True
			has_primary = False # to handle weird classes with no clear primary
			for m in c['meetings']:
				if m['is_primary'] == True:
					has_primary = True
					if not re.search(conflicting_days, m['days']):
						all_conflict = False # non matching days
						break
					if m['start_time'] == 'TBA':
						all_conflict = False # TBA class
						break
					m_start = datetime.datetime.strptime(m['start_time'], "%I:%M %p").time()
					m_end = datetime.datetime.strptime(m['end_time'], "%I:%M %p").time()
					if not any(((m_start <= end) and (start <= m_end)) for (start, end) in conflicting_times):
						all_conflict = False #non matching times
						break
			if all_conflict and has_primary:
				has_conflict = True
				print c # print conflicting course
				break
		return has_conflict
	
	#-------------------------------------------------------------------------
	# conflict with one class (has precepts, but one primary)
	def test_oneclass(self):
		global Client
		global User
		global Course
		global combine
		c = Client()
		user = User.objects.create_user(username='tester15', password='test')
		c.force_login(user=user)
		random_7 = self.random_queryset_elements(Course.objects.all(), 7)
		registrar_combo = combine(list(random_7), 4)
		if registrar_combo is not None:
			combo_0 = registrar_combo[0].split(",")
			print combo_0[0]
			course_0 = Course.objects.get(registrar_id = combo_0[0])
			conflict = course_0.meetings.filter(is_primary=True)
			if len(conflict) == 1:
				conflict = conflict[0]
				conflict_days = conflict.days
				print conflict_days
				print type(conflict_days)
				print type(conflict.start_time)
		# no_conflict = json.loads(c.get('/courses/filter/conflict_|COS 340').content)
		# conflicting_days = 'M|W'
		# conflicting_times = [(datetime.time(13, 30), datetime.time(14, 50))]
		# has_conflict = self.check_conflict(no_conflict, conflicting_days, conflicting_times)

		
		user.delete()
		self.assertFalse(False)
		# self.assertFalse(has_conflict)
	


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
