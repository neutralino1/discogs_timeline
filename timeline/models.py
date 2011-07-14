import logging
from django.db import models
from django.contrib.auth.models import User
from timeline.helpers import connect_hooks
from django.core.exceptions import ValidationError
#from math import max, min
#from timeline.fields import ReleasedField

class TimelineUser(models.Model):
    user = models.OneToOneField(User)
    releases = models.ManyToManyField("Release", db_table="timeline_release_owners")
    
class Release(models.Model):
    discogs_id = models.IntegerField()
    artist = models.CharField(max_length=200)
    label = models.CharField(max_length=200)
    thumb = models.URLField()
    released = models.DateField()
    catno = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    owners = models.ManyToManyField(TimelineUser, related_name="owner")
    
    def normalize_released(self):
        if len(self.released) == 4 and int(self.released) >= 1900:
            self.released = self.released + '-01-01'
        else:
            self.released = '1970-01-01'
        logging.debug(self.released)

    def clean_and_save(self):
        self.normalize_released()
        self.save()

    def year(self):
        return int(self.released.year)

    def month(self):
        return int(self.released.month)
    
    def day(self):
        return int(self.released.day)

class Year:
    def __init__(self, year):
        self.releases = []
        self.year = year

    def __str__(self):
        return str(self.year)

    def __int__(self):
        return self.year

    def __lshift__(self, item):
        if isinstance(item, Release):
            self.releases += [item]
            
    def __lt__(self, item):
        if isinstance(item, Year):
            return self.year < item.year

    def __gt__(self, item):
        if isinstance(item, Year):
            return self.year > item.year

    def odd(self):
        return self.year % 2 != 0

    def even(self):
        return self.year % 2 == 0

class Timeline:
    def __init__(self, releases):
        self.years = []
        for r in releases:
            self.add_release(r)
        self.complete()

    def complete(self):
        for i in range(self.years[0].year + 1, self.years[-1].year):
            self.year(i)

    def add_release(self, release):
        y = self.year(release.year())
        y << release

    def year(self, y):
        for i in self.years:
            if i.year == y:
                return i
        i = Year(y)
        self << i
        return i

    def __lshift__(self, item):
        if isinstance(item, Year):
            if len(self.years) == 0:
                self.years += [item]
            else:
                logging.debug('Adding %i' % item.year)
                y = self.years[0]
                i = 0
                while item > y:
                    i += 1
                    if i >= len(self.years):
                        break
                    y = self.years[i]
                self.years.insert(i, item)
                

    def earliest_year(self):
        earliest = Year(3000)
        for y in self.years:
            earliest = min(y, earliest)
        return earliest

    def latest_year(self):
        latest = Year(0)
        for y in self.years:
            latest = max(y, latest)
        return latest
