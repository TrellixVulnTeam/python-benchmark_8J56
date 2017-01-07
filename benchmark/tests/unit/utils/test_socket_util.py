import os
import unittest

import benchmark
from benchmark.utils import config_util
from benchmark.utils import log_util

ini_path = os.path.dirname(benchmark.__file__) + "/../etc/benchmark/server.ini"
CONFIG = config_util.get_config()
CONFIG.parse_ini(ini_path)

from benchmark.utils import socket_util

LOG = log_util.get_logger(__name__)


class TestSocketUtil(unittest.TestCase):
    def setUp(self):
        self.remote_host = "127.0.0.1"
        self.remote_port = 9898

    def test_send_request(self):
        messages = []
        messages.append("abcd")

        for message in messages:
            socket_util.send_request(self.remote_host, self.remote_port,
                                     message)

    def test_rpc_call(self):
        messages = []
        messages.append({})
        messages.append({"operate_type": "some action"})

        for message in messages:
            socket_util.rpc_call(self.remote_host, message)
