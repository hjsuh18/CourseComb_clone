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

def __get_eval_soup(url):
    """
    Returns a Beautiful Soup instnace for the given term and course id.
    Be warned that a page existing is not a guarantee that the course
    existed in that term.
    """
    page = urllib.urlopen(url)
    return BeautifulSoup(page, 'html5lib')


def __get_eval_stats(soup):
    """
    Returns a mapping of category to average for the given
    course.
    """
    # The eval stats are included in the element with
    # selector `#chart > input` in its value attribute, and is
    # base64 encoded as a JSON file.
    eval_stats_str = soup.find(id='chart').input['value']
    eval_stats = json.loads(base64.b64decode(eval_stats_str))

    # compute the average rating of course and return it
    value_items = eval_stats['PlotArea']['ListOfSeries'][0]['Items']
    values = [float(val['YValue']) for val in value_items]
    sum_ratings = 0
    for x in values:
        sum_ratings = sum_ratings + x
    return "{:.2f}".format(sum_ratings / len(values))

def course_eval(term, course_id):
    """
    Returns the course evaluation stats (as a dict) and comments
    (as an array of strings) for a given course and term.
    """

    url = __get_url(term, course_id)
    soup = __get_eval_soup(url)
    if soup.find(id='chart') is None:
        return {},[]

    stats = __get_eval_stats(soup)

    return url, stats

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
