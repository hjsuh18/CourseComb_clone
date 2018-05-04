"""
Scrapes the course evaluations page for a single course.
From USG Labs (NOT ReCourse's code).
"""
from bs4 import BeautifulSoup
import urllib
import base64
import json
import sys
import pprint
import html5lib

#: Base URL for course evaluations page
BASE_URL = 'https://reg-captiva.princeton.edu/chart/index.php'

def __get_url(term,course_id):
    url_opts = {
        'terminfo': term,
        'courseinfo': course_id
    }

    url_opts_enc = urllib.urlencode(url_opts)
    request_url = BASE_URL + '?' + url_opts_enc

    return request_url

def course_eval(term, course_id):
    """
    Returns the course evaluation stats (as a dict) and comments
    (as an array of strings) for a given course and term.
    """

    url = __get_url(term, course_id)
    return url

if __name__ == '__main__':
    """
    Usage: python evals.py [term] [subject]
    Pretty prints the information and classes found with the
    given term and subject.
    """
    pp = pprint.PrettyPrinter(indent = 2)

    term = sys.argv[1]
    course_id = sys.argv[2]

    pp.pprint(course_eval(term, course_id))
