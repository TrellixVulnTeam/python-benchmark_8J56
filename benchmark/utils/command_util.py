import os
import subprocess
import sys

from benchmark.utils import log_util
from benchmark.utils import config_util

CONFIG = config_util.get_config()
LOG = log_util.get_logger(__name__)

result_file_prefix = CONFIG.get_opt("result_file_prefix", "agent")
pid_file_prefix = CONFIG.get_opt("pid_file_prefix", "agent")


def execute(command, task_num):
    """
    Execute a command with task_id to support multiple task on the same server.
    :param command: command to be executed
    :param task_num: task id from client
    """

    # clean by task_num before start
    if os.path.exists(result_file_prefix + str(task_num)):
        os.remove(result_file_prefix + str(task_num))
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
    LOG.debug("running command: %s" % command)
    LOG.debug("writing pid(%s) to file %s" %
              (process.pid, pid_file_prefix + str(task_num)))
    with open(pid_file_prefix + str(task_num), "w") as f:
        f.write(str(process.pid))

    output = ""
    while True:
        out = process.stdout.read(1)
        if out == '' and process.poll() is not None:
            break
        if out != '':
            output += out
            sys.stdout.write(out)
            sys.stdout.flush()

    LOG.debug("writing results to file %s" %
              (result_file_prefix + str(task_num)))
    LOG.debug("testing result content is : \n %s" % output)
    with open(result_file_prefix + str(task_num), "w") as f:
        f.writelines(output)
