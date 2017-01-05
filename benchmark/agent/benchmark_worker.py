import SocketServer
import json
import subprocess
import sys
import threading
import time
import os
import signal
import socket


class TaskStatus:
    RUNNING = 0
    NOT_STARTED = 1
    STOPPED = 2


class OperateType:
    START = 0
    STATUS = 1
    KILL = 2
    CLEAN = 3
    DIRECT_COMMAND = 4


class ReturnCode:
    SUCCESSED = 0
    FAILED = 1


pid_file = "/tmp/pid_benchmark_"
result_file = "/tmp/result_benchmark_"
listen_ip = "0.0.0.0"
listen_port = 9898

wait_task_start_time = 1  # seconds


def execute_command(command, task_id):
    """
    Execute a command with task_id to support multiple task on the same server.
    :param command: command to be executed
    :param task_id: task id from client
    """
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)

    print "writing pid(%s) to file %s" % (process.pid, pid_file + str(task_id))
    with open(pid_file + str(task_id), "w") as f:
        f.write(str(process.pid))

    output = ""
    while True:
        out = process.stdout.read(1)
        if out == '' and process.poll() is not None:
            break
        if out != '':
            output += out
            sys.stdout.flush()

    print "writing results to file %s" % (result_file + str(task_id))
    with open(result_file + str(task_id), "w") as f:
        f.writelines(output)


def execute_command_direct(command):
    output = subprocess.check_output([command], shell=True)
    return output


class TCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(8192).strip()
        print "[handler] received data from %s: %s" % (self.client_address[0], data)
        msg = json.loads(data)
        operate = msg.get("operate", "")
        if operate == OperateType.START:
            command = msg["command"]
            task_id = msg["task_id"]
            thread = threading.Thread(target=execute_command, args=(command, task_id))
            thread.start()
            msg = {"code": ReturnCode.SUCCESSED}
            self.request.sendall(json.dumps(msg))
        elif operate == OperateType.KILL:
            task_id = msg["task_id"]
            with open(pid_file + str(task_id), "r") as f:
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
            if os.path.exists(pid_file + str(task_id)):
                # print "pid exists"
                if os.path.exists(result_file + str(task_id)):
                    # print "result %s exists" % (result_file + str(task_id))
                    with open(result_file + str(task_id), 'r') as f:
                        result = f.readlines()
                    msg = {"code": ReturnCode.SUCCESSED, "status": TaskStatus.STOPPED, "result": result}
                    self.request.sendall(json.dumps(msg))
                else:
                    # print "result %s not exists" % (result_file + str(task_id))
                    msg = {"code": ReturnCode.SUCCESSED, "status": TaskStatus.RUNNING}
                    self.request.sendall(json.dumps(msg))
            else:
                msg = {"code": ReturnCode.SUCCESSED, "status": TaskStatus.NOT_STARTED}
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


def clean():
    print "[clean] kill all processes and clean all tmp files"
    for tmp_file in os.listdir('/tmp'):
        if tmp_file.startswith("pid_benchmark_") or tmp_file.startswith("result_benchmark_"):
            file_name = '/tmp/' + tmp_file
            if os.path.isfile(file_name):
                if "pid_benchmark_" in file_name:
                    # kill process
                    with open(file_name, 'r') as f:
                        pid = f.readline()
                        try:
                            print "[clean] kill process(%)" % pid
                            os.kill(int(pid), signal.SIGTERM)
                        except:
                            print "pid: %s not exists" % pid
                print "[clean]      remove file: %s" % file_name
                os.remove(file_name)


def get_ips():
    cmd = "/sbin/ip a | awk '/inet /{print substr($2,0,20)}' | " \
          "grep -v 127.0.0.1"
    ip_info_output = subprocess.check_output([cmd], shell=True)
    ips = []
    for ip in ip_info_output.split('\n'):
        if "127.0.0.1" not in ip:
            ips.append(ip)
            replace_slash = ip.replace("/", "_")
    return "[local info] " + "-".join(ips)


def install_packages(packages):
    for package in packages:
        existed_command = "rpm -qa | grep %s" % package
        try:
            subprocess.check_output([existed_command], shell=True)
        except:
            print "%s is not installed, install it" % package
            cmd = "yum -y install %s" % package
            print cmd
            output = subprocess.check_output([cmd], shell=True)
            print output


if __name__ == "__main__":
    """
    you should run this script as root, or the kill command will fail and the status
    will always be running
    """
    packages = ['epel-release', 'sysbench', 'fio', 'iperf', 'tree', 'pciutils', 'net-tools', 'htop', 'nload']
    install_packages(packages)

    clean()
    print "[local info] " + socket.gethostname()
    print get_ips()
    server = SocketServer.TCPServer((listen_ip, listen_port), TCPHandler)
    server.serve_forever()
