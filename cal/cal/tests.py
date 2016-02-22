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
        self.assertEquals("ab", ab.id)
        self.assertEquals(self.a, ab.start)
        self.assertEquals(self.b, ab.end)
        self.assertIsNone(ab.next)
        chain1 = TimeNodeChain()
        self.assertIsNone(chain1.get_head())
        chain2 = TimeNodeChain()
        chain2.insert(ab)
        self.assertEquals(ab, chain2.get_head())

        def check_ordering(head, first, second, third=None):
            self.assertEquals(first, head)
            self.assertEquals(first, first.next.prev)
            self.assertEquals(second, first.next)
            self.assertEquals(third, second.next)
            self.assertEquals(third, first.next.next)
            if third:  # Sometimes we just want to check ordering of two events
                self.assertIsNone(third.next)
                self.assertIsNone(second.next.next)
                self.assertIsNone(first.next.next.next)
                self.assertEquals(first, first.next.next.prev.prev)
                self.assertEquals(second, first.next.next.prev)

        # AB CD EF Insert at front
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(ef)
        head = chain.get_head()
        check_ordering(head, ab, cd, ef)

        # EF CD AB (inserted backwards)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(ef)
        chain.insert(cd)
        chain.insert(ab)
        head = chain.get_head()
        check_ordering(head, ab, cd, ef)

        # CD EF AB (mixed ordering)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(cd)
        chain.insert(ef)
        chain.insert(ab)
        head = chain.get_head()
        check_ordering(head, ab, cd, ef)

        # AB EF CD (more mixed orderings)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert(ab)
        chain.insert(ef)
        chain.insert(cd)
        head = chain.get_head()
        check_ordering(head, ab, cd, ef)

        # AB BC CD (exactly equal start/end times, out of order)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        bc = TimeNode(self.c, self.d, "bc")
        cd = TimeNode(self.e, self.f, "cd")
        chain.insert(ab)
        chain.insert(bc)
        chain.insert(cd)
        head = chain.get_head()
        check_ordering(head, ab, bc, cd)

        # AB CD BC (exactly equal start/end times, out of order)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        bc = TimeNode(self.c, self.d, "bc")
        cd = TimeNode(self.e, self.f, "cd")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(bc)
        head = chain.get_head()
        check_ordering(head, ab, bc, cd)

    def test_insert_with_overwrite(self):

        def check_ordering(head, first, second, third=None):
            self.assertEquals(first, head)
            self.assertEquals(first, first.next.prev)
            self.assertEquals(second, first.next)
            self.assertEquals(third, second.next)
            self.assertEquals(third, first.next.next)
            if third:  # Sometimes we just want to check ordering of two events
                self.assertIsNone(third.next)
                self.assertIsNone(second.next.next)
                self.assertIsNone(first.next.next.next)
                self.assertEquals(first, first.next.next.prev.prev)
                self.assertEquals(second, first.next.next.prev)

        # AB1 CD EF + AB2 = AB2 CD EF
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        ab1 = TimeNode(self.a, self.b, "ab")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(ef)
        chain.insert(ab1)
        head = chain.get_head()
        check_ordering(head, ab1, cd, ef)

        # CD EF AB1 + AB2 = AB2 CD EF
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        ab1 = TimeNode(self.a, self.b, "ab")
        chain.insert(cd)
        chain.insert(ef)
        chain.insert(ab)
        chain.insert(ab1)
        head = chain.get_head()
        check_ordering(head, ab1, cd, ef)

        # AB CD EF + AD = AD EF
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        ad = TimeNode(self.a, self.d, "ad")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(ef)
        chain.insert(ad)
        head = chain.get_head()
        check_ordering(head, ad, ef, None)

        # AB CD EF + AD + DE = AD DE EF
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        ad = TimeNode(self.a, self.d, "ad")
        de = TimeNode(self.d, self.e, "de")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(ef)
        chain.insert(ad)
        chain.insert(de)
        head = chain.get_head()
        check_ordering(head, ad, de, ef)

        # AC DE EF + BD = BD DE EF
        chain = TimeNodeChain()
        ac = TimeNode(self.a, self.c, "ac")
        de = TimeNode(self.d, self.e, "de")
        ef = TimeNode(self.e, self.f, "ef")
        bd = TimeNode(self.b, self.d, "bd")
        chain.insert(ac)
        chain.insert(de)
        chain.insert(ef)
        chain.insert(bd)
        head = chain.get_head()
        check_ordering(head, bd, de, ef)

        # AC DE EF + BD + BE = BE EF
        chain = TimeNodeChain()
        ac = TimeNode(self.a, self.c, "ac")
        de = TimeNode(self.d, self.e, "de")
        ef = TimeNode(self.e, self.f, "ef")
        bd = TimeNode(self.b, self.d, "bd")
        be = TimeNode(self.b, self.e, "be")
        chain.insert(ac)
        chain.insert(de)
        chain.insert(ef)
        chain.insert(bd)
        chain.insert(be)
        head = chain.get_head()
        check_ordering(head, be, ef, None)

        # BE EF FG + EG = BE EG
        chain = TimeNodeChain()
        be = TimeNode(self.b, self.e, "be")
        ef = TimeNode(self.e, self.f, "ef")
        fg = TimeNode(self.f, self.g, "fg")
        eg = TimeNode(self.e, self.g, "eg")
        chain.insert(be)
        chain.insert(ef)
        chain.insert(fg)
        chain.insert(eg)
        head = chain.get_head()
        check_ordering(head, be, eg, None)

        # AB CD EF + GH + AG = AG GH
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        gh = TimeNode(self.g, self.h, "gh")
        ag = TimeNode(self.a, self.g, "ag")
        chain.insert(ab)
        chain.insert(cd)
        chain.insert(ef)
        chain.insert(gh)
        chain.insert(ag)
        head = chain.get_head()
        check_ordering(head, ag, gh, None)

    def test_insert_all(self):

        # Test proper initialization
        ab = TimeNode(self.a, self.b, "ab")
        self.assertEquals("ab", ab.id)
        self.assertEquals(self.a, ab.start)
        self.assertEquals(self.b, ab.end)
        self.assertIsNone(ab.next)
        chain1 = TimeNodeChain()
        self.assertIsNone(chain1.get_head())
        chain2 = TimeNodeChain()
        chain2.insert(ab)
        self.assertEquals(ab, chain2.get_head())

        def check_ordering(head, first, second, third=None):
            self.assertEquals(first, head)
            self.assertEquals(first, first.next.prev)
            self.assertEquals(second, first.next)
            self.assertEquals(third, second.next)
            self.assertEquals(third, first.next.next)
            if third:  # Sometimes we just want to check ordering of two events
                self.assertIsNone(third.next)
                self.assertIsNone(second.next.next)
                self.assertIsNone(first.next.next.next)
                self.assertEquals(first, first.next.next.prev.prev)
                self.assertEquals(second, first.next.next.prev)

        # AB CD EF
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert_all([ab, cd, ef])
        head = chain.get_head()
        check_ordering(head, ab, cd, ef)

        # EF CD AB (inserted backwards)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert_all([ef, cd, ab])
        head = chain.get_head()
        check_ordering(head, ab, cd, ef)

        # CD EF AB (mixed ordering)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert_all([cd, ef, ab])
        head = chain.get_head()
        check_ordering(head, ab, cd, ef)

        # AB EF CD (more mixed orderings)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        cd = TimeNode(self.c, self.d, "cd")
        ef = TimeNode(self.e, self.f, "ef")
        chain.insert_all([ab, ef, cd])
        head = chain.get_head()
        check_ordering(head, ab, cd, ef)

        # AB BC CD (exactly equal start/end times, out of order)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        bc = TimeNode(self.c, self.d, "bc")
        cd = TimeNode(self.e, self.f, "cd")
        chain.insert_all([ab, bc, cd])
        head = chain.get_head()
        check_ordering(head, ab, bc, cd)

        # AB CD BC (exactly equal start/end times, out of order)
        chain = TimeNodeChain()
        ab = TimeNode(self.a, self.b, "ab")
        bc = TimeNode(self.c, self.d, "bc")
        cd = TimeNode(self.e, self.f, "cd")
        chain.insert_all([ab, cd, bc])
        head = chain.get_head()
        check_ordering(head, ab, bc, cd)

    # TODO tests for insert_all with conflicts
