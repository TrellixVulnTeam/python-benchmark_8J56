"""
you should run this script as root,
or the kill command will fail and the status will always be running
"""

import SocketServer
import json
import os
import signal
import subprocess
import traceback

from benchmark.utils import log_util
from benchmark.agent.worker.cpu_benchmark import CPUBenchmark
from benchmark.constant.benchmark_type import BenchmarkType
from benchmark.constant.operate_type import OperateType
from benchmark.constant.return_code import ReturnCode
from benchmark.utils import config_util

CONFIG = config_util.get_config()
LOG = log_util.get_logger(__name__)

result_file_prefix = CONFIG.get_opt("result_file_prefix", "agent")
pid_file_prefix = CONFIG.get_opt("pid_file_prefix", "agent")


def local_ips():
    cmd = "/sbin/ip a | awk '/inet /{print substr($2,0,20)}' | " \
          "grep -v 127.0.0.1"
    ip_info_output = subprocess.check_output([cmd], shell=True)
    ips = []
    for ip in ip_info_output.split('\n'):
        if "127.0.0.1" not in ip:
            ips.append(ip)
    return ("[local info(ip)] " + "-".join(ips)).strip("-")


def clean():
    # TODO: kill process by port

    LOG.info("[clean] kill all processes and clean all tmp files")
    for tmp_file in os.listdir('/tmp'):
        if tmp_file.startswith("pid_benchmark_") \
                or tmp_file.startswith("result_benchmark_"):
            file_name = '/tmp/' + tmp_file
            if os.path.isfile(file_name):
                if "pid_benchmark_" in file_name:
                    with open(file_name, 'r') as f:
                        pid = f.readline()
                        try:
                            LOG.debug("[clean] kill process(%)" % pid)
                            os.kill(int(pid), signal.SIGTERM)
                        except:
                            LOG.debug("pid: %s not exists" % pid)
                LOG.debug("[clean]      remove file: %s" % file_name)
                os.remove(file_name)


# {code, message, task_status, result}
class Handler(SocketServer.BaseRequestHandler):
    def get_benchmark_class(self, benchmark_type):
        if benchmark_type == BenchmarkType.CPU:
            return CPUBenchmark()
        return None

    def handle(self):
        try:
            received_str = self.request.recv(8192).strip()
            LOG.debug("received from %s : %s" %
                      (self.client_address[0], received_str))
            received_dict = json.loads(received_str)
            operate_type = received_dict.get("operate_type", "")
            task_num = received_dict.get("task_num", "")
            benchmark_type = received_dict.get("benchmark_type", "")
            benchmark_class = self.get_benchmark_class(benchmark_type)
            LOG.debug("operate_type: %s" % operate_type)
            LOG.debug("benchmark_type: %s" % benchmark_type)
            if operate_type == OperateType.START:
                try:
                    args = received_dict["args"]
                    benchmark_class.start(task_num, args)
                    ret = {"code": ReturnCode.SUCCESSED,
                           "message": "%s testing is running." %
                                      benchmark_type}
                    self.request.sendall(json.dumps(ret))
                except Exception, exception:
                    ret = {"code": ReturnCode.FAILED,
                           "message": "task run error"}
                    LOG.exception(exception)
                    self.request.sendall(json.dumps(ret))
            elif operate_type == OperateType.STOP:
                pass
            elif operate_type == OperateType.STATUS:
                ret = benchmark_class.status(task_num)
                self.request.sendall(json.dumps(ret))
            elif operate_type == OperateType.RESULT:
                ret = benchmark_class.result(task_num)
                self.request.sendall(json.dumps(ret))
            elif operate_type == OperateType.ONLINE:
                ret = {"code": ReturnCode.SUCCESSED}
                self.request.sendall(json.dumps(ret))
            else:
                message = "unsupport operate type: %s" % operate_type
                LOG.error(message)
                ret = {"code": ReturnCode.FAILED,
                       "message": message}
                self.request.sendall(json.dumps(ret))
        except ValueError, error:
            LOG.exception(error)
            message = "cannot convert request to json"
            LOG.error(message)
            ret = {"code": ReturnCode.FAILED,
                   "message": message}
            self.request.sendall(json.dumps(ret))
        except Exception, exception:
            LOG.exception(exception)
            ret = {"code": ReturnCode.FAILED,
                   "message": traceback.format_exc()}
            self.request.sendall(json.dumps(ret))

# class TCPHandler(SocketServer.BaseRequestHandler):
#     def handle(self):
#         data = self.request.recv(8192).strip()
#         print "[handler] received data from %s: %s" % \
#               (self.client_address[0], data)
#         msg = json.loads(data)
#         operate = msg.get("operate", "")
#         if operate == OperateType.START:
#             command = msg["command"]
#             task_id = msg["task_id"]
#             thread = threading.Thread(target=execute_command,
#                                       args=(command, task_id))
#             thread.start()
#             msg = {"code": ReturnCode.SUCCESSED}
#             self.request.sendall(json.dumps(msg))
#         elif operate == OperateType.STOP:
#             task_id = msg["task_id"]
#             with open(pid_file_prefix + str(task_id), "r") as f:
#                 pid = f.readline()
#             try:
#                 print "[handler] kill process(%s)" % pid
#                 os.kill(int(pid), signal.SIGTERM)
#             except:
#                 print "[handler] pid: %s not exists" % pid
#
#             # send result to client
#             msg = {"code": ReturnCode.SUCCESSED}
#             self.request.sendall(json.dumps(msg))
#         elif operate == OperateType.STATUS:
#             task_id = msg["task_id"]
#             if os.path.exists(pid_file_prefix + str(task_id)):
#                 # print "pid exists"
#                 if os.path.exists(result_file_prefix + str(task_id)):
#                     # print "result %s exists" % (result_file_prefix + str(task_id))
#                     with open(result_file_prefix + str(task_id), 'r') as f:
#                         result = f.read()
#
#                     msg = {"code": ReturnCode.SUCCESSED,
#                            "status": TaskStatus.FINISHED, "result": result}
#                     self.request.sendall(json.dumps(msg))
#                 else:
#                     msg = {"code": ReturnCode.SUCCESSED,
#                            "status": TaskStatus.RUNNING}
#                     self.request.sendall(json.dumps(msg))
#             else:
#                 msg = {"code": ReturnCode.SUCCESSED,
#                        "status": TaskStatus.NOT_STARTED}
#                 self.request.sendall(json.dumps(msg))
#         elif operate == OperateType.CLEAN:
#             clean()
#             msg = {"code": ReturnCode.SUCCESSED}
#             self.request.sendall(json.dumps(msg))
#         elif operate == OperateType.DIRECT_COMMAND:
#             # TODO: it is dangerous to expose this api
#             command = msg["command"]
#             output = execute_command_direct(command)
#             msg = {"code": ReturnCode.SUCCESSED, "output": output}
#             self.request.sendall(json.dumps(msg))
#         else:
#             print "opertion type: %s not found" % operate
