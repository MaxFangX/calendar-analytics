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

        def check_ordering(head, first, second, third):
            self.assertEquals(first, head)
            self.assertEquals(second, first.tail)
            self.assertEquals(third, second.tail)
            self.assertEquals(third, first.tail.tail)
            self.assertEquals(third, head.tail.tail)
            self.assertIsNone(third.tail)
            self.assertIsNone(second.tail.tail)
            self.assertIsNone(first.tail.tail.tail)
            self.assertIsNone(head.tail.tail.tail)

        # AB CD EF Insert at front
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(ef)
        head = chain.get_first()
        check_ordering(head, ab, cd, ef)

        # EF CD AB (inserted backwards)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(ef)
        chain.insert(cd)
        chain.insert(ab)
        head = chain.get_first()
        check_ordering(head, ab, cd, ef)

        # TODO
        # CD EF AB (mixed ordering)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(cd)
        chain.insert(ef)
        chain.insert(ab)
        head = chain.get_first()
        check_ordering(head, ab, cd, ef)

        # AB EF CD (more mixed orderings)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(ab)
        chain.insert(ef)
        chain.insert(cd)
        head = chain.get_first()
        check_ordering(head, ab, cd, ef)

        # AB BC CD (exactly equal start/end times, out of order)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        bc = TimeNode(self.c, self.d, "bc")
        cd = TimeNode(self.e, self.f, "cd")
        chain.insert(ab)
        chain.insert(bc)
        chain.insert(cd)
        head = chain.get_first()
        check_ordering(head, ab, bc, cd)

        # AB CD BC (exactly equal start/end times, out of order)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        bc = TimeNode(self.c, self.d, "bc")
        cd = TimeNode(self.e, self.f, "cd")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(bc)
        head = chain.get_first()
        check_ordering(head, ab, bc, cd)

    def test_insert_with_overwrite(self):
        print "TESTS WITH OVERWRITE UNIMPLEMENTED"
        pass
