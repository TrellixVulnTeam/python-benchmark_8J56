"""
you should run this script as root,
or the kill command will fail and the status will always be running
"""

import SocketServer
import json
import logging
import os
import signal
import socket
import subprocess
import sys
import threading


class TaskStatus:
    RUNNING = "running"
    NOT_STARTED = "not started"
    FINISHED = "finished"


class OperateType:
    START = "start"
    STOP = "stop"
    STATUS = "status"
    RESULT = "result"
    CLEAN = 3
    DIRECT_COMMAND = 4

class BenchmarkType:
    CPU = "cpu"
    MEMORY = "memory"

class ReturnCode:
    SUCCESSED = 0
    FAILED = 1


pid_file_prefix = "/tmp/pid_benchmark_"
result_file_prefix = "/tmp/result_benchmark_"
log_file = "/tmp/benchmarkd.log"
listen_ip = "0.0.0.0"
listen_port = 9898
wait_task_start_time = 1  # seconds
run_command_as_sudo = False


def get_logger(name):
    format_string = "%(asctime)s - %(levelname)s - " \
                    "%(module)s:%(lineno)s - %(message)s"
    formatter = logging.Formatter(fmt=format_string)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


LOG = get_logger(__name__)

packages = ["epel-release", "tree", "htop", "nload", "sysstat", "pciutils",
            "iproute", "net-tools",
            "sysbench", "fio", "iperf", "iperf3"]


def install_packages(packages):
    for package in packages:
        existed_command = "rpm -qa | grep %s" % package
        try:
            subprocess.check_output([existed_command], shell=True)
        except:
            LOG.debug("%s is not installed, install it" % package)
            sudo = "sudo" if run_command_as_sudo else ""
            cmd = "%s yum -y install %s" % (sudo, package)
            LOG.debug(cmd)
            subprocess.check_output([cmd], shell=True)


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


def execute_command(command, task_num):
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
            sys.stdout.flush()

    LOG.debug("writing results to file %s" %
              (result_file_prefix + str(task_num)))
    with open(result_file_prefix + str(task_num), "w") as f:
        f.writelines(output)


def execute_command_direct(command):
    output = subprocess.check_output([command], shell=True)
    return output


class CPUBenchmark():
    def start(self, task_num, args):
        num_threads = args["num-threads"]
        max_prime = args["cpu-max-prime"]
        command = "sysbench --num-threads=%s " \
                  "--test=cpu --cpu-max-prime=%s run" % \
                  (num_threads, max_prime)
        thread = threading.Thread(target=execute_command,
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


# {code, message, task_status, result}
class Handler(SocketServer.BaseRequestHandler):
    def get_benchmark_class(self, benchmark_type):
        if benchmark_type == BenchmarkType.CPU:
            return CPUBenchmark()

    def handle(self):
        received_str = self.request.recv(8192).strip()
        LOG.debug("received from %s : %s" %
                  (self.client_address[0], received_str))
        received_dict = json.loads(received_str)
        operate_type = received_dict.get("operate_type", "")
        task_num = received_dict.get("task_num", "")
        benchmark_type = received_dict["benchmark_type"]
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
        else:
            pass


class TCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(8192).strip()
        print "[handler] received data from %s: %s" % \
              (self.client_address[0], data)
        msg = json.loads(data)
        operate = msg.get("operate", "")
        if operate == OperateType.START:
            command = msg["command"]
            task_id = msg["task_id"]
            thread = threading.Thread(target=execute_command,
                                      args=(command, task_id))
            thread.start()
            msg = {"code": ReturnCode.SUCCESSED}
            self.request.sendall(json.dumps(msg))
        elif operate == OperateType.STOP:
            task_id = msg["task_id"]
            with open(pid_file_prefix + str(task_id), "r") as f:
                pid = f.readline()
            try:
                print "[handler] kill process(%s)" % pid
                os.kill(int(pid), signal.SIGTERM)
            except:
                print "[handler] pid: %s not exists" % pid

            # send result to client
            msg = {"code": ReturnCode.SUCCESSED}
            self.request.sendall(json.dumps(msg))
        elif operate == OperateType.STATUS:
            task_id = msg["task_id"]
            if os.path.exists(pid_file_prefix + str(task_id)):
                # print "pid exists"
                if os.path.exists(result_file_prefix + str(task_id)):
                    # print "result %s exists" % (result_file_prefix + str(task_id))
                    with open(result_file_prefix + str(task_id), 'r') as f:
                        result = f.read()

                    msg = {"code": ReturnCode.SUCCESSED,
                           "status": TaskStatus.FINISHED, "result": result}
                    self.request.sendall(json.dumps(msg))
                else:
                    msg = {"code": ReturnCode.SUCCESSED,
                           "status": TaskStatus.RUNNING}
                    self.request.sendall(json.dumps(msg))
            else:
                msg = {"code": ReturnCode.SUCCESSED,
                       "status": TaskStatus.NOT_STARTED}
                self.request.sendall(json.dumps(msg))
        elif operate == OperateType.CLEAN:
            clean()
            msg = {"code": ReturnCode.SUCCESSED}
            self.request.sendall(json.dumps(msg))
        elif operate == OperateType.DIRECT_COMMAND:
            # TODO: it is dangerous to expose this api
            command = msg["command"]
            output = execute_command_direct(command)
            msg = {"code": ReturnCode.SUCCESSED, "output": output}
            self.request.sendall(json.dumps(msg))
        else:
            print "opertion type: %s not found" % operate


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "sudo":
        run_command_as_sudo = True

    try:
        clean()
        install_packages(packages)
        LOG.info("[local info(hostname)] " + socket.gethostname())
        LOG.info(local_ips())
        LOG.info("listen on %s:%s" % (listen_ip, listen_port))
        server = SocketServer.TCPServer((listen_ip, listen_port), Handler)
        server.serve_forever()
    except Exception, exception:
        LOG.exception(exception)
