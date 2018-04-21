from .models import Course, Meeting
from django.contrib.postgres.search import SearchVector


# 1. need to work in the logic for finding conflicts between classes. This may lead to the exclusion part not working, so be careful
# 2. once enough testing is done, transfer this code/translate to django and work into code

# for a certain course anchor, remove all courses in course_list that conflict with anchor
def exclude_conflicts(anchor, course_list):
	length = len(course_list)
	for i in range(length - 1, -1, -1):
		course_meetings = course_list[i].meetings.filter(is_primary=True)
		for j in range(0, len(course_meetings)):
			if anchor.is_conflict(course_meetings[j]):
				course_list.pop(i)
				break
	return course_list

# append all elements in list l with prefix
def append(prefix, l):
	for i in range (0, len(l)):
		l[i] = prefix.registrar_id + ',' + l[i]
	return l


# courses is a list of courses, k is the number courses being selected
def combine(courses, k):
	# error: k is greater than length of courses
	if (k > len(courses)):
		return None

	# base case where combinations are length 1
	if k == 1:
		for i in range (0, len(courses)):
			courses[i] = courses[i].registrar_id
		return courses

	# recursion
	combinations = []
	for i in range (0, len(courses) - k + 1):
		anchor = courses[i]
		anchor_meetings = courses[i].meetings.filter(is_primary=True)
		# courses[i+1:len(courses)] needs to be filtered to exclude conflicts
		for m in anchor_meetings:
			x = exclude_conflicts(m, courses[i + 1:len(courses)])
			subset = combine(x, k - 1)
			if subset == None:
				continue
			combinations.extend(append(anchor, subset))

	# deal with courses with multiple primary meeting times
	seen = set()
	for i in range(len(combinations)-1, -1, -1):
		if combinations[i] not in seen:
			seen.add(combinations[i])
		else:
			combinations.pop(i)
			
	return combinations