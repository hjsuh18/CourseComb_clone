'''
Adopted from the Recal repository (file of the same name).
Modified to only scrape for one semester (compared to multiple).
'''

from django.conf import settings
import django
# from courses.scraper import scrape_all
# from courses.scrape_import import scrape_import_course, ScrapeCounter
import pickle

django.setup()

# * For new scraping *
# print "Scraping for this semester"
# courses = scrape_all()
# f = open('courses.pckl', 'wb')
# pickle.dump(list(courses), f)
# f.close()

# # For old scraping
# print "open previous scraping"
# f = open('courses.pckl', 'rb')
# courses = pickle.load(f)
# f.close()
# print "put in database"
# scrapeCounter = ScrapeCounter()
# [scrape_import_course(x, scrapeCounter) for x in courses]
# print str(scrapeCounter)
# print "----------------------------------"

def get_all_courses():
    from courses.scraper import scrape_all
    from courses.scrape_import import scrape_import_course, ScrapeCounter
	# scrape_all()
    try:
        print "Scraping for this semester"
        courses = scrape_all()

        scrapeCounter = ScrapeCounter()
        # courses = []
        # a =[]
        # scrape_import_course(courses,a)
        #[scrape_import_course(x, a) for x in courses]
        [scrape_import_course(x, scrapeCounter) for x in courses]
        print str(scrapeCounter)
        print "----------------------------------"
    except Exception as e:
        print e

# settings.configure()

get_all_courses()
