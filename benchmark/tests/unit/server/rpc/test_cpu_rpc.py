import os
import unittest

import benchmark
from benchmark.utils import config_util
from benchmark.utils import log_util

ini_path = os.path.dirname(benchmark.__file__) + "/../etc/benchmark/server.ini"
CONFIG = config_util.get_config()
CONFIG.parse_ini(ini_path)

from benchmark.server.rpc.cpu_rpc import CpuRpc

LOG = log_util.get_logger(__name__)


class TestCpuRPC(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.max_prime = 50000
        self.requery_time_delay = 3

    def test_run(self):
        cpurpc = CpuRpc(self.ip, max_prime=self.max_prime,
                        requery_time_delay=self.requery_time_delay)
        result = cpurpc.run()
        LOG.debug("the result of testing is %s" % result)
