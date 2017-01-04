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
    RUNNING = "0"
    NOT_STARTED = "1"
    STOPPED = "2"


class OperateType:
    START = "0"
    KILL = "1"
    STATUS = "2"
    CLEAN = "3"

class ReturnCode:
    SUCCESSED = "0"
    FAILED = "1"

pid_file = "/tmp/pid_benchmark_"
result_file = "/tmp/result_benchmark_"

wait_task_start_time = 1 # seconds


def execute_command(cmd, task_id):
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    print "writting pid(%s) to file %s" % (process.pid, pid_file+str(task_id))
    with open(pid_file+str(task_id), "w") as f:
        f.write(str(process.pid) + "")

    output = ""
    while True:
        out = process.stdout.read(1)
        if out == '' and process.poll() != None:
            break
        if out != '':
            output += out
            # sys.stdout.write(out)
            sys.stdout.flush()
    print "writting results to file %s" % (result_file+str(task_id))
    with open(result_file+str(task_id), "w") as f:
        f.writelines(output)


class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        print "received: %s" % data
        msg = json.loads(data)
        operate = msg.get("operate", "")
        if operate == OperateType.START:
            command = msg["command"]
            task_id = msg["task_id"]
            thread = threading.Thread(target=execute_command, args=(command,task_id))
            thread.start()
        elif operate == OperateType.KILL:
            task_id = msg["task_id"]
            with open(pid_file+str(task_id), "r") as f:
                pid = f.readline()
                print "kill pid: %s " % pid
            os.kill(int(pid), signal.SIGTERM)

            # send result to client
            msg = {"code": ReturnCode.SUCCESSED}
            self.request.sendall(json.dumps(msg))
        elif operate == OperateType.STATUS:
            task_id = msg["task_id"]
            if os.path.exists(pid_file+str(task_id)):
                if os.path.exists(result_file+str(task_id)):
                    with open(result_file+str(task_id), 'r') as f:
                        result = f.readlines()
                    msg = {"code": "0", "status": TaskStatus.STOPPED, "result": result}
                else:
                    msg = {"code": "0", "status": TaskStatus.RUNNING}
            else:
                msg = {"code": "0", "status": TaskStatus.NOT_STARTED}
            self.request.sendall(json.dumps(msg))
        elif operate == OperateType.CLEAN:
            print "clean"
            clean()
        else:
            print "opertion type: %s not found" % operate


# start msg:
# {"operate": "0", "command": "ping -c 50 www.baidu.com", "ip": "10.12.10.52"}
# {"operate": "0", "command": "iperf -s", "ip": "10.12.10.52"}
# {"operate": "1", "command": "iperf -s", "ip": "10.12.10.52"}

# kill msg:
# {"operate": "1", "command": "ping -c 50 www.baidu.com", "ip": "10.12.10.52"}

def clean():
    for tmp_file in os.listdir('/tmp'):
        # todo : kill process in pid file. if exists
        if tmp_file.startswith("pid_benchmark_") or tmp_file.startswith("result_benchmark_"):
            if os.path.isfile('/tmp/' + tmp_file):
                os.remove('/tmp/' + tmp_file)



if __name__ == "__main__":
    clean()
    print socket.gethostname()
    HOST, PORT = "0.0.0.0", 9898
    print PORT
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
