import unittest

from operations.core.ericsson.ocs.offer_server_generator import OffersGenerator
from operations.scheduler.schedules import Schedules


class TestOffersGenerator(unittest.TestCase):
    
    def setUp(self):
        print 111
        self.os = OffersGenerator()

    def test_schedule(self):
        print 'start'
        s = Schedules()
        s.schedule_time('min_1',self.os.schedule_min)

        while True:
            pass
    
if __name__ == "__main__":
    unittest.main()

    
    