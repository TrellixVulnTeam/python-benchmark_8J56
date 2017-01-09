import unittest

from benchmark.utils import fabric_util


class TestFabricUtil(unittest.TestCase):
    def setUp(self):
        self.ips = ["centos7", "centos7"]
        self.users = ["root", "root"]
        self.ports = ["22", "22"]
        self.key_files = ["~/.ssh/id_rsa", "~/.ssh/id_rsa"]
        self.command = "ls"

    def test_wrapper_execute(self):
        host_config = "%s@%s:%s" % (self.users[0], self.ips[0], self.ports[0])
        fabric_util.wrapper_execute(host_config, self.command,
                                    self.key_files[0])

    def test_execute_remote_command_one_host(self):
        fabric_util.execute_remote_command_one_host(self.ips[0], self.users[0],
                                                    self.ports[0],
                                                    self.command,
                                                    self.key_files[0])

    def test_execute_remote_command_multiple_hosts(self):
        fabric_util.execute_remote_command_multiple_hosts(self.ips, self.users,
                                                          self.ports,
                                                          self.command,
                                                          self.key_files)
