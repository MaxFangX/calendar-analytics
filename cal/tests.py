from django.auth.models import User
from django.test import TestCase
from cal.models import GCalendar, GEvent

class FindCategoryTestCase(TestCase):

    def setUp(self):
        self.alice = User(username='alice')
        self.alice.save()
        self.calendar = GCalendar(user=self.alice)
        self.calendar.save()

    def test_separation_of_categories(self):
        pass
