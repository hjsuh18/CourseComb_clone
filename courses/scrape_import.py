import datetime
import re
# heavily modified from same named script in ReCal's repository
# for instance, has a part to get max pages of reading/wk, as well as grading
# criteria (necessary for our project, but not ReCal)
class ScrapeCounter:

    def __init__(self):
        self.totalCoursesCount = 0
        self.createdCoursesCount = 0
        self.totalMeetingsCount = 0
        self.createdMeetingsCount = 0

    def __str__(self):
        return str(self.createdCoursesCount) + " new courses\n" + \
               str(self.totalCoursesCount) + " total courses\n" + \
               str(self.createdMeetingsCount) + " new meetings\n" + \
               str(self.totalMeetingsCount) + " total meetings"


def scrape_import_course(course, counter=ScrapeCounter()):
    from courses.models import Course, Meeting

    def import_meeting(meeting, course_object, letter):
        # creates Meeting object and a relationship with the calling Course obj
        start = None if meeting['starttime'] == 'TBA' else datetime.datetime.strptime(meeting['starttime'], "%I:%M:%S %p").time()
        end = None if meeting['endtime'] == 'TBA' else datetime.datetime.strptime(meeting['endtime'], "%I:%M:%S %p").time()

        meeting_object, created = Meeting.objects.get_or_create(
            course=course_object,
            start_time= start,
            end_time= end,
            days=meeting['days'],
            section=meeting['section'],
            is_primary=letter in meeting['section'],
            enroll=meeting['enroll'],
            limit=meeting['limit']
        )
        meeting_object.save()
        if created:
            counter.createdMeetingsCount += 1
        counter.totalMeetingsCount += 1
        return meeting_object

    # only check registrar_id to see if create or update, since other things
    # may change
    course_object, created = Course.objects.update_or_create(
        registrar_id=course['courseid'],
        defaults = {
            "deptnum": '/'.join([x['dept'] + " " + x['number'] for x in course['listings']]),
            "evals": course['evaluation'],
            "area": course['area'] or "",
            "url": course['url'],

            "pdfaudit": course['pdfaudit'] or "",
            "pdfable": not "npdf" in course['pdfaudit'] and not "No P/D/F" in course['pdfaudit'] and not "No Pass/D/Fail" in course['pdfaudit'],
            "auditable": not "na" in course['pdfaudit'] and not "No Audit" in course['pdfaudit'],
            "pdfonly": "P/D/F Only" in course['pdfaudit'],
            "title": course['title'],
        }

    )

    # Debugging output to check things scraped normally
    print course_object.deptnum + " " + course_object.title + " "+ \
        course_object.registrar_id

    # finding the primary meeting
    letter = 'C'
    for x in course['classes']:
        if x['section'][0] in 'LSU':
            letter = x['section'][0]
            break

    # delete any current meetings since may have change and reimport
    course_object.meetings.all().delete()
    [import_meeting(x, course_object, letter) for x in course['classes']]

    course_object.save()
    if created:
        counter.createdCoursesCount += 1
    counter.totalCoursesCount += 1


    return counter
