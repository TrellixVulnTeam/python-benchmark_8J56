import json
import unittest

import utils.stats_util as stats_util


class TestStatsUtil(unittest.TestCase):
    def setUp(self):
        self.ip = "10.0.246.150/24"

    def tearDown(self):
        pass

    def test_get_statistics_avg(self):
        avg_values = stats_util.get_one_statistics_avg(self.ip)
        print json.dumps(avg_values)

    def test_get_all_statistics_avg(self):
        all_statistics = stats_util.get_all_statistics_avg()
        print json.dumps(all_statistics)
