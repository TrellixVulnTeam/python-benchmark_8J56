import json
import socket
import time
import traceback
import unittest

from benchmarkd import BenchmarkType
from benchmarkd import OperateType
from benchmarkd import ReturnCode
from benchmarkd import TaskStatus


class TestBenchmarkd(unittest.TestCase):
    def setUp(self):
        self.ip = "172.16.7.18"
        self.port = 9898

    def send_msg(self, ip, port, msg_dict):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.sendall(json.dumps(msg_dict) + "\n")
            received = sock.recv(8192).strip()
            return received
        except:
            print traceback.format_exc()
            print "get data from %s failed." % ip

    def test_cpu_start(self):
        msg_dict = {"operate_type": OperateType.START,
                    "benchmark_type": BenchmarkType.CPU,
                    "args": {"num-threads": "64", "cpu-max-prime": "20000"}}
        print self.send_msg(self.ip, self.port, msg_dict)

    def test_cpu_status(self):
        msg_dict = {"operate_type": OperateType.STATUS,
                    "benchmark_type": BenchmarkType.CPU}
        print self.send_msg(self.ip, self.port, msg_dict)

    def test_cpu_result(self):
        msg_dict = {"operate_type": OperateType.RESULT,
                    "benchmark_type": BenchmarkType.CPU}
        print self.send_msg(self.ip, self.port, msg_dict)

    def test_benchmark_cpu(self):
        num_threads = "64"
        cpu_max_prime_ = "10000"
        requery_time_delay = 5  # second

        start_dict = {"operate_type": OperateType.START,
                      "benchmark_type": BenchmarkType.CPU,
                      "args": {"num-threads": num_threads,
                               "cpu-max-prime": cpu_max_prime_}}
        start_ret = json.loads(self.send_msg(self.ip, self.port, start_dict))
        if start_ret["code"] == ReturnCode.SUCCESSED:
            done = False
            while not done:
                status_dict = {"operate_type": OperateType.STATUS,
                               "benchmark_type": BenchmarkType.CPU}
                status_ret = json.loads(self.send_msg(self.ip,
                                                      self.port,
                                                      status_dict))
                if status_ret["task_status"] == TaskStatus.FINISHED:
                    done = True
                time.sleep(requery_time_delay)

            result_dict = {"operate_type": OperateType.RESULT,
                           "benchmark_type": BenchmarkType.CPU}

            result_ret = json.loads(self.send_msg(self.ip,
                                                  self.port,
                                                  result_dict))
            print "result is %s" % result_ret["result"]
