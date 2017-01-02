import unittest

import bson.json_util

from benchmark.utils import chart_util
from benchmark.utils import mongo_util
from benchmark.utils import stats_util


class TestChartUtil(unittest.TestCase):
    def setUp(self):
        self.chart_id = 2
        self.server_id = 1
        self.servers = mongo_util.get_all_servers()
        self.chart = mongo_util.get_chart(self.chart_id)
        self.stats = stats_util.get_all_statistics_avg()

    def test_get_name_of_server_in_chart(self):
        server_name_in_chart = chart_util.get_name_of_server_in_chart(
            self.servers, self.server_id, self.chart)
        print server_name_in_chart

    def test_get_value_of_server(self):
        value = chart_util.get_value_of_server(self.servers, self.server_id,
                                               self.chart, self.stats)
        print value

    def test_construct_char(self):
        data = chart_util.construct_char(self.chart_id)
        print bson.json_util.dumps(data)
