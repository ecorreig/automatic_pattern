__author__ = 'dracks'
import unittest
import dateutil.parser
from ..EndpointProperties import DateProperty

class DateTest(unittest.TestCase):
    def test_completed_date(self):
        date = '2008-08-09T15:06:00Z'
        subject = DateProperty()
        subject = subject.instantiate(date)
        self.assertEqual(subject.get(), dateutil.parser.parse(date))

    def test_none_date(self):
        subject = DateProperty()
        self.assertEqual(subject.get(), None)