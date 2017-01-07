import unittest
import benchmark
from benchmark.utils import config_util
from benchmark.utils import log_util
import os


ini_path = os.path.dirname(benchmark.__file__)+"/../etc/benchmark/agent.ini"
CONFIG = config_util.get_config()
CONFIG.parse_ini(ini_path)


LOG = log_util.get_logger(__name__)


class TestConfigUtil(unittest.TestCase):
    def setUp(self):
        self.server_int = os.path.dirname(benchmark.__file__)+"/../etc/benchmark/server.ini"
        self.mongodb_host = "127.0.0.1"

    def test_parse_ini(self):
        CONFIG.parse_ini(self.server_int)
        LOG.debug(CONFIG.groups)
        self.assertEqual(self.mongodb_host,
                         CONFIG.get_opt("host", "mongodb"))
