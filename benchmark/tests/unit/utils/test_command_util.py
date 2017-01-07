import os
import unittest

import benchmark
from benchmark.utils import config_util
from benchmark.utils import log_util


ini_path = os.path.dirname(benchmark.__file__) + "/../etc/benchmark/agent.ini"
CONFIG = config_util.get_config()
CONFIG.parse_ini(ini_path)

LOG = log_util.get_logger(__name__)
from benchmark.utils import command_util


class TestCommandUtil(unittest.TestCase):
    def setUp(self):
        self.command = "sysbench --num-threads=64 --test=cpu " \
                       "--cpu-max-prime=50000 run"
        self.task_num = 1

    def test_execute(self):
        command_util.execute(self.command, self.task_num)
