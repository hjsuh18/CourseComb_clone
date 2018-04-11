# 1. need to work in the logic for finding conflicts between classes. This may lead to the exclusion part not working, so be careful
# 2. once enough testing is done, transfer this code/translate to django and work into code

def time_convert(time):
	return time.split(':')

# return 1 if x is before y, 0 if same, -1 if x is after y
def time_compare(x, y):
	time_1 = time_convert(x)
	time_2 = time_convert(y)
	if time_1[0] < time_2[0]:
		return 1
	elif time_1[0] > time_2[0]:
		return -1
	if time_1[1] < time_2[1]:
		return 1
	elif time_1[1] > time_2[1]:
		return -1
	return 0

# convert days of the week string representation to array
def day_convert(day):
	day_array = [0, 0, 0, 0, 0]
	for i in range(0, len(day)):
		d = day[i]
		if d == 'M':
			day_array[0] = 1
		if d == 'T':
			if i + 1 < len(day) and day[i + 1] == 'h':
				day_array[3] = 1
				i += 1
			else:
				day_array[1] = 1
		if d == 'W':
			day_array[2] = 1
		if d == 'F':
			day_array[4] = 1
	return day_array

# return a list of days where x and y overlap
def day_compare(x, y):
	day_1 = day_convert(x)
	day_2 = day_convert(y)
	for i in range (0, 5):
		if day_1[i] + day_2[i] == 2:
			return True
	return False

# Meeting object to mimic Django model
class Meeting:
	def __init__(self, days, start_time, end_time):
		self.days = days
		self.start_time = start_time
		self.end_time = end_time
	def __str__(self):
		return self.days + " (" + self.start_time + ", " + self.end_time + ")"

	# made the assumption that class is held at same time on all days for a certain course
	def is_conflict(self, Meeting):
		day_overlap = day_compare(self.days, Meeting.days)
		if not day_overlap:
			return False
		else:
			# conflict = start_time_1 < end_time_2 && end_time_1 > start_time_2
			x = time_compare(self.start_time, Meeting.end_time)
			y = time_compare(Meeting.start_time, self.end_time)
			if x == 1 and y == 1:
				return True
			else:
				return False

# Course object to mimic Django model
class Course:
	def __init__(self, deptnum, meetings):
		self.deptnum = deptnum
		self.meetings = meetings

	def __str__(self):
		meeting_list = ''
		for meeting in self.meetings:
			meeting_list = meeting_list + str(meeting) + "\t"
		return self.deptnum + '\t' + meeting_list

	def is_conflict(self, Course):
		# need logic here to see if two courses conflict
		for i in range(0, len(self.meetings)):
			for j in range(0, len(Course.meetings)):
				if not (self.meetings[i]).is_conflict(Course.meetings[j]):
					return False
		return True
		

# for a certain course anchor, remove all courses in course_list that conflict with anchor
def exclude_conflicts(anchor, course_list):
	length = len(course_list)
	for i in range(length - 1, -1, -1):
		if anchor.is_conflict(course_list[i]):
			course_list.pop(i)
	return course_list


# append all elements in list l with prefix
def append(prefix, l):
	for x in l:
		x = x.append(prefix)
	return l


# courses is a list of courses, k is the number courses being selected
def combine(courses, k):
	# error: k is greater than length of courses
	if (k > len(courses)):
		return None

	# base case where combinations are length 1
	if k == 1:
		for i in range (0, len(courses)):
			courses[i] = [courses[i]]
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

P01 = Meeting('MWF', '10:00', '10:50')
P02 = Meeting('TTh', '11:00', '11:50')
P03 = Meeting('MWF', '11:00', '11:50')
P04 = Meeting('TTh', '12:00', '13:20')
P05 = Meeting('MWF', '10:30', '11:20') # conflicts with P03
P06 = Meeting('TTh', '11:00', '12:20') # conflicts with P02, P04
cos126 = Course('COS 126', [P02])
cos226 = Course('COS 226', [P03])
cos217 = Course('COS 217', [P04])
cos326 = Course('COS 326', [P05]) # conflicts with cos226
cos445 = Course('COS 445', [P06]) # conflicts with cos126 and cos217

course_list = [cos126, cos226, cos217, cos326, cos445]

combo = combine(course_list, 2)
print len(combo)

for combination in combo:
	for course in combination:
		print str(course),
	print