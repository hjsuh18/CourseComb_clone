from .models import Course, Meeting


# 1. need to work in the logic for finding conflicts between classes. This may lead to the exclusion part not working, so be careful
# 2. once enough testing is done, transfer this code/translate to django and work into code

# for a certain course anchor, remove all courses in course_list that conflict with anchor
def exclude_conflicts(anchor, course_list):
	length = len(course_list)
	for i in range(length - 1, -1, -1):
		if anchor.is_conflict(course_list[i]):
			course_list.pop(i)
	return course_list


# append all elements in list l with prefix
def append(prefix, l):
	for i in range (0, len(l)):
		l[i] = l[i] + ', ' + str(prefix)
	return l


# courses is a list of courses, k is the number courses being selected
def combine(courses, k):
	# error: k is greater than length of courses
	if (k > len(courses)):
		return None

	# base case where combinations are length 1
	if k == 1:
		for i in range (0, len(courses)):
			courses[i] = str(courses[i])
		return courses

	# recursion
	combinations = []
	for i in range (0, len(courses) - k + 1):
		anchor = courses[i]
		# courses[i+1:len(courses)] needs to be filtered to exclude conflicts
		x = exclude_conflicts(anchor, courses[i + 1:len(courses)])
		subset = combine(x, k - 1)
		if subset == None:
			continue
		combinations.extend(append(anchor, subset))
	return combinations