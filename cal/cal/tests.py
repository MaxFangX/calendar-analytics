from django.contrib.auth.models import User
from django.test import TestCase
from cal.models import GCalendar, GEvent, Statistic
from cal.helpers import TimeNodeChain, TimeNode

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

    def test_insert(self):

        # Test proper initialization
        ab = TimeNode(self.a, self.b, "ab")
        self.assertEquals("ab", ab.event_id)
        self.assertEquals(self.a, ab.start)
        self.assertEquals(self.b, ab.end)
        self.assertIsNone(ab.tail)
        chain1 = TimeNodeChain()
        self.assertIsNone(chain1.get_first())
        chain2 = TimeNodeChain(ab)
        self.assertEquals(ab, chain2.get_first())

        # AB CD EF Insert at front
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(ef)
        first = chain.get_first()
        self.assertEquals(cd, ab.tail)
        self.assertEquals(ef, cd.tail)
        self.assertEquals(ef, ab.tail.tail)
        self.assertEquals(ef, first.tail.tail)
        self.assertIsNone(ef.tail)
        self.assertIsNone(cd.tail.tail)
        self.assertIsNone(ab.tail.tail.tail)
        self.assertIsNone(first.tail.tail.tail)

        # EF CD AB (inserted backwards)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(ef)
        chain.insert(cd)
        chain.insert(ab)
        first = chain.get_first()
        self.assertEquals(cd, ab.tail)
        self.assertEquals(ef, cd.tail)
        self.assertEquals(ef, ab.tail.tail)
        self.assertEquals(ef, first.tail.tail)
        self.assertIsNone(ef.tail)
        self.assertIsNone(cd.tail.tail)
        self.assertIsNone(ab.tail.tail.tail)
        self.assertIsNone(first.tail.tail.tail)

        # TODO
        # CD EF AB
        # AB EF CD

        # AB BC CD
        # CD BC AB
