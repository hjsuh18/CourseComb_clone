import unittest
from django.conf import settings
from django.test import Client
import courses.views
from django.contrib.auth.models import User
import datetime, re, json

# Tests course conflict filter
class TestConflict(unittest.TestCase):
    # only works when run with python manage.py shell --plain < courses/tests.py and with no new lines in between

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
        c = Client()
        user = User.objects.create_user(username='test', password='test')
        c.force_login(user=user)
        no_conflict = json.loads(c.get('/courses/filter/conflict_|COS 340').content)
        conflicting_days = 'M|W'
        conflicting_times = [(datetime.time(13, 30), datetime.time(14, 50))]
        has_conflict = self.check_conflict(no_conflict, conflicting_days, conflicting_times)
        user.delete()
        self.assertFalse(has_conflict)
    #-------------------------------------------------------------------------
    def test_multiple_primary(self):
        # conflict with one class, two primaries
        c = Client()
        user = User.objects.create_user(username='test', password='test')
        c.force_login(user=user)
        no_conflict = json.loads(c.get('/courses/filter/conflict_|SML 201').content)
        conflicting_days = 'T|Th'
        conflicting_times = [(datetime.time(11, 0), datetime.time(12, 20)), (datetime.time(15, 0), datetime.time(16, 20))]
        has_conflict = self.check_conflict(no_conflict, conflicting_days, conflicting_times)
        user.delete()
        self.assertFalse(has_conflict)
    #-------------------------------------------------------------------------
    def test_sametime(self):
        # conflict with two classes at same time
        c = Client()
        user = User.objects.create_user(username='test', password='test')
        c.force_login(user=user)
        no_conflict = json.loads(c.get('/courses/filter/conflict_|COS 333|ORF 363').content)
        conflicting_days = 'T|Th'
        conflicting_times = [(datetime.time(13, 30), datetime.time(14, 50))]
        has_conflict = self.check_conflict(no_conflict, conflicting_days, conflicting_times)
        user.delete()
        self.assertFalse(has_conflict)
    #-------------------------------------------------------------------------
    def test_difftime(self):
        # conflict with two classes at diff time but same days
        c = Client()
        user = User.objects.create_user(username='test', password='test')
        c.force_login(user=user)
        no_conflict = json.loads(c.get('/courses/filter/conflict_|COS 333|COS 226').content)
        conflicting_days = 'T|Th'
        conflicting_times = [(datetime.time(11,0), datetime.time(12, 20)), (datetime.time(13, 30), datetime.time(14, 50))]
        has_conflict = self.check_conflict(no_conflict, conflicting_days, conflicting_times)
        user.delete()
        self.assertFalse(has_conflict)
    #-------------------------------------------------------------------------
    def test_diffdays(self):
        # conflict with two classes on diff days
        c = Client()
        user = User.objects.create_user(username='test', password='test')
        c.force_login(user=user)
        no_conflict = json.loads(c.get('/courses/filter/conflict_|COS 333|COS 432').content)
        conflicting_days = 'M|W' # for one class
        conflicting_times = [(datetime.time(15, 0), datetime.time(16, 20))]
        has_conflict1 = self.check_conflict(no_conflict, conflicting_days, conflicting_times)
        conflicting_days = 'T|Th' # for other class
        conflicting_times = [(datetime.time(13, 30), datetime.time(14, 50))]
        has_conflict2 = self.check_conflict(no_conflict, conflicting_days, conflicting_times)
        user.delete()
        self.assertFalse(has_conflict1 or has_conflict2)


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
