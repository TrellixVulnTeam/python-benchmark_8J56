import os
import threading

from benchmark.constant.return_code import ReturnCode
from benchmark.constant.task_status import TaskStatus
from benchmark.utils import command_util
from benchmark.utils import config_util
from benchmark.utils import log_util

CONFIG = config_util.get_config()
LOG = log_util.get_logger(__name__)

result_file_prefix = CONFIG.get_opt("result_file_prefix", "agent")
pid_file_prefix = CONFIG.get_opt("pid_file_prefix", "agent")


class CPUBenchmark:
    def start(self, task_num, args):
        num_threads = args["num-threads"]
        max_prime = args["cpu-max-prime"]
        command = "sysbench --num-threads=%s " \
                  "--test=cpu --cpu-max-prime=%s run" % \
                  (num_threads, max_prime)
        thread = threading.Thread(target=command_util.execute,
                                  args=(command, task_num))
        thread.start()

    def status(self, task_num):
        if os.path.exists(pid_file_prefix + str(task_num)):
            if os.path.exists(result_file_prefix + str(task_num)):
                return {"code": ReturnCode.SUCCESSED,
                        "task_status": TaskStatus.FINISHED}
            else:
                return {"code": ReturnCode.SUCCESSED,
                        "task_status": TaskStatus.RUNNING}
        else:
            return {"code": ReturnCode.SUCCESSED,
                    "task_status": TaskStatus.NOT_STARTED}

    def result(self, task_num):
        with open(result_file_prefix + str(task_num)) as f:
            for line in f.readlines():
                if "total time:" in line:
                    cpu_result = line.split(':')[1].strip().replace('s', '')
                    return {"code": ReturnCode.SUCCESSED,
                            "task_status": TaskStatus.FINISHED,
                            "result": cpu_result}
