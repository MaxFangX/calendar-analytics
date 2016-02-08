from django.contrib.auth.models import User
from django.test import TestCase
from cal.models import GCalendar, GEvent, Statistic

import datetime


class CategoryTestCase(TestCase):

    def setUp(self):
        self.alice = User(username='alice')
        self.alice.save()
        self.calendar = GCalendar(user=self.alice)
        self.calendar.save()

    def test_separation_of_categories(self):
        # TODO
        print "SKIPPING CATEGORY TESTS"
        return

        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)

        e1 = GEvent(name='bigger',
                    start=yesterday,
                    end=yesterday+datetime.timedelta(hours=1),
                    calendar=self.calendar, color=GEvent.EVENT_COLORS[0])
        e1.save()
        e2 = GEvent(name='bigger smaller',
                    start_time=yesterday,
                    end_time=yesterday+datetime.timedelta(hours=1),
                    calendar=self.calendar, color=GEvent.EVENT_COLORS[0],)
        e2.save()

        stat1 = Statistic(user=self.alice,
                          name='Bigger',
                          start_time=yesterday,
                          end_time=now,)
        stat1.save()

        self.assertEqual(2, stat1.query().count())


class TimeTestCase(TestCase):

    def setUp(self):
        self.start = datetime.datetime.now()
        self.a = self.start + datetime.timedelta(hours=1)
        self.b = self.start + datetime.timedelta(hours=2)
        self.c = self.start + datetime.timedelta(hours=3)
        self.d = self.start + datetime.timedelta(hours=4)
        self.e = self.start + datetime.timedelta(hours=5)
        self.f = self.start + datetime.timedelta(hours=6)
        self.g = self.start + datetime.timedelta(hours=7)
        self.h = self.start + datetime.timedelta(hours=8)

        if self.a < self.b and self.b < self.c and self.c < self.d and\
            self.d < self.e and self.e < self.f and self.f < self.g and self.g < self.h:
            print "Initialized times a-g"

    def test_timenodes(self):
        pass
