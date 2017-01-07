import time
from benchmark.constant.benchmark_type import BenchmarkType
from benchmark.constant.operate_type import OperateType
from benchmark.constant.task_status import TaskStatus
from benchmark.constant.task_result import TaskResult
from benchmark.utils import socket_util
from benchmark.utils import log_util

LOG = log_util.get_logger(__name__)


class CpuRpc:
    def __init__(self, ip, num_threads="64", max_prime="20000",
                 task_num="1", requery_time_delay=30):
        self.ip = ip
        self.num_threads = num_threads
        self.max_prime = max_prime
        self.task_num = task_num
        self.requery_time_delay = requery_time_delay

    def start(self):
        request_dict = {OperateType.KEY: OperateType.START,
                        BenchmarkType.KEY: BenchmarkType.CPU,
                        "args": {"num-threads": self.num_threads,
                                 "cpu-max-prime": self.max_prime}}
        LOG.debug("start cpu benchmarking on %s " % self.ip)
        return socket_util.rpc_call(self.ip, request_dict)

    def status(self):
        request_dict = {OperateType.KEY: OperateType.STATUS,
                        BenchmarkType.KEY: BenchmarkType.CPU}
        LOG.debug("query cpu benchmarking status on %s " % self.ip)
        return socket_util.rpc_call(self.ip, request_dict)

    def result(self):
        request_dict = {OperateType.KEY: OperateType.RESULT,
                        BenchmarkType.KEY: BenchmarkType.CPU}
        LOG.debug("get cpu benchmarking result on %s " % self.ip)
        return socket_util.rpc_call(self.ip, request_dict)

    def run(self):
        try:
            self.start()
            done = False
            while not done:
                time.sleep(self.requery_time_delay)
                status_dict = self.status()
                if status_dict[TaskStatus.KEY] == TaskStatus.FINISHED:
                    done = True
            result_dict = self.result()
            return result_dict[TaskResult.KEY]
        except Exception, exception:
            LOG.exception(exception)
            LOG.error("cpu benchmarking error, skipping...")
            return 0
