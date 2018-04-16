# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from time_compare import time_compare, day_convert, day_compare

# Course model below adopted from ReCal's model, with modifications to fields
# E.g. Instead of a Course_Listing model, we added department and number to
# the model (deptnum).
# We also have additional fields for things like max pages of reading/wk,
# pdf- and audit-ability, and grading categories.
class Course(models.Model):
    # identifying fields
    registrar_id = models.CharField(max_length=20, unique=True)
    title = models.TextField()
    deptnum = models.TextField()

    # general information easily gained from scraping
    evals = ArrayField(models.TextField(), default=['', ''])
    #description = models.TextField()
    area = models.CharField(max_length=3)
    url = models.TextField()

    # information about a course after some parsing
    pdfable = models.BooleanField(default = True)
    pdfonly = models.BooleanField(default=False)
    auditable = models.BooleanField(default=True)
    pdfaudit = models.TextField()

    def is_conflict(self, Course):
        # need logic here to see if two courses conflict
        self_meetings = self.meetings.filter(is_primary=True)
        Course_meetings = Course.meetings.filter(is_primary=True)
        for i in range(0, len(self_meetings)):
            for j in range(0, len(Course_meetings)):
                if not (self_meetings[i]).is_conflict(Course_meetings[j]):
                    return False
        return True

    def __str__(self):
        return self.deptnum

    def __unicode__(self):
        return self.deptnum + ": " + self.title

# Adopted from ReCal (merging their Meeting and Section mode), but using
# TimeFields for start and end times, as well as using a field for section
# (rather than a relationship with another model).
class Meeting(models.Model):
    course = models.ForeignKey(Course, related_name="meetings")
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    days = models.CharField(max_length=10)
    section = models.CharField(max_length=4) # probably 3, but just in case
    is_primary = models.BooleanField(default=False) # whether meeting is primary

    # made the assumption that class is held at same time on all days for a certain course
    def is_conflict(self, Meeting):
        day_overlap = day_compare(self.days, Meeting.days)
        if not day_overlap:
            return False
        else:
            if self.start_time == None or Meeting.start_time == None:
                return False
            else:
                x = time_compare(self.start_time, Meeting.end_time)
                y = time_compare(Meeting.start_time, self.end_time)
                if x == 1 and y == 1:
                    return True
                else:
                    return False

    def __unicode__(self):
        if self.start_time != None:
            times = self.start_time.strftime("%I:%M %p")+ ' - ' + self.end_time.strftime("%I:%M %p")
        else:
            times = "TBA"
        return  self.days + ": " + times

# Model that is auto created upon the saving of a User.
# Has one-to-one relationship with User and stores the User's favorites
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique = True)
    faves = models.TextField()
    # course_combo = ArrayField(models.TextField(), blank=True)
    
    def __unicode__(self):
        return "User: " + self.user.username + ", Favorites: " + self.faves + ", Course Combinations: " + course_combo

# A certain user's course combination
class Combination(models.Model):
    user = models.ForeignKey(Profile, related_name='combinations')
    comb_id = models.SmallIntegerField(default=-1)
    course_combo = models.TextField(default=None)
    registrar_combo = models.TextField(default=None, null=True)
    filtered = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.course_combo

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, faves="")

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    