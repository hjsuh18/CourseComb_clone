from .models import Course, Meeting
from django.contrib.postgres.search import SearchVector
from copy import deepcopy

# for a certain course meeting anchor, remove all courses in course_list that conflict with anchor
def exclude_conflicts(anchor, course_list):

	courses = deepcopy(course_list[0])
	course_meetings = deepcopy(course_list[1])
	c_length = len(courses)
	# go through each course and get rid of meetings that conflict with anchor meeting
	# if all meetings of course conflicts, delete entire course from course list
	# iterate through every course
	for i in range(c_length - 1, -1, -1):
		# m is all the primary meetings of i'th course
		m = course_meetings[i]
		course_conflict = False
		# go through every meeting of course and delete meetings that conflict
		m_length = len(m)
		for j in range(m_length - 1, -1, -1):
			if anchor.is_conflict(m[j]):
				m.pop(j)
				# there are no meetings that do not conflict
				if len(m) == 0:
					courses.pop(i)
					course_meetings.pop(i)
					course_conflict = True
					break
		# if there are still meetings that do not conflict, update meetings
		if not course_conflict:
			course_meetings[i] = m

	course_list = [courses, course_meetings]
	return course_list

# append all elements in list l with prefix
def append(prefix, l):
	for i in range (0, len(l)):
		l[i] = prefix.registrar_id + ',' + l[i]
	return l

# courses is a list of courses, k is the number courses being selected
def course_combine(courses, k):

	# error: k is greater than length of courses
	if (k > len(courses[0])):
		return None

	# base case where combinations are length 1
	if k == 1:
		l = []
		for i in range (0, len(courses[0])):
			l.append(courses[0][i].registrar_id)
		return l

	# recursion
	combinations = []
	for i in range (0, len(courses[0]) - k + 1):
		anchor_course = courses[0][i]
		anchor_meetings = courses[1][i]

		# courses[i+1:len(courses)] needs to be filtered to exclude conflicts
		for m in anchor_meetings:
			x = exclude_conflicts(m, [courses[0][i + 1:len(courses[0])], courses[1][i + 1:len(courses[0])]])
			subset = course_combine(x, k - 1)
			if subset == None:
				continue
			combinations.extend(append(anchor_course, subset))

	# deal with courses with multiple primary meeting times
	seen = set()
	for i in range(len(combinations)-1, -1, -1):
		if combinations[i] not in seen:
			seen.add(combinations[i])
		else:
			combinations.pop(i)

	return combinations

# set up data structures for processing by course_combine
# returns an array of all course combinations without time conflicts of primary meetings
# combination is represented as a String of registrar ids separated by commas
def combine(courses, k):
	meetings = []
	for i in range(0, len(courses)):
		m = list(courses[i].meetings.filter(is_primary=True))
		meetings.append(m)
	courses = [courses, meetings]
	return course_combine(courses, k)