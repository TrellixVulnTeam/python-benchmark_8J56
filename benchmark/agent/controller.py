import json
import socket
import time


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


server_port = 9898

# bandwidth_task = {"tested_server_id": 1, "agent_ids": [2, 3, 4]}
bandwidth_task = {"tested_server_ip": "10.12.10.52",
                  "agent_ips": ["10.12.10.53", "10.12.10.54", "10.12.10.57",
                                "10.12.10.58"]}



def send_msg(ip, port, msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(msg + "\n")

    received = sock.recv(4096)
    return received


def get_status(ip, port, task_id=1):
    msg = {"operate": OperateType.STATUS, "task_id": task_id}
    received = send_msg(ip, port, json.dumps(msg))
    return json.loads(received)


def start(ip, port, command, task_id=1):
    msg = {"operate": OperateType.START, "command": command, "task_id": task_id}
    received = send_msg(ip, port, json.dumps(msg))
    # return json.loads(received)


def stop(ip, port, task_id=1):
    msg = {"operate": OperateType.KILL, "task_id": task_id}
    received = send_msg(ip, port, json.dumps(msg))
    return json.loads(received)


def clean(ip, port):
    msg = {"operate": OperateType.CLEAN}
    received = send_msg(ip, port, json.dumps(msg))
    # return json.loads(received)


def test_incoming_bandwidth():
    tested_server_ip = bandwidth_task["tested_server_ip"]

    clean(tested_server_ip, server_port)
    for agent_ip in bandwidth_task["agent_ips"]:
        print "clean %s" % agent_ip
        clean(agent_ip, server_port)

    agent_all_stopped = False
    while not agent_all_stopped:
        tested_server_status = get_status(tested_server_ip, server_port)
        if tested_server_status["status"] == TaskStatus.NOT_STARTED:
            command = "iperf -s"
            start(tested_server_ip, server_port, command)
        elif tested_server_status["status"] == TaskStatus.RUNNING:
            stopped_count = 0
            for agent_ip in bandwidth_task["agent_ips"]:
                agent_status = get_status(agent_ip, server_port)
                if agent_status["status"] == TaskStatus.NOT_STARTED:
                    command = "iperf -c %s -t 20" % (tested_server_ip)
                    start(agent_ip, server_port, command)
                elif agent_status["status"] == TaskStatus.STOPPED:
                    stopped_count += 1
                    if stopped_count == len(bandwidth_task["agent_ips"]):
                        agent_all_stopped = True
        time.sleep(10)

    stop(tested_server_ip, server_port)
    tested_server_status = get_status(tested_server_ip, server_port)
    if tested_server_status["status"] == TaskStatus.STOPPED:
        result = tested_server_status["result"]

    total_incoming_band_width = 0
    print "result is: \n"
    for line in result:
        if "/sec" in line:
            print line
            splits = line.strip().split(' ')
            unit = splits[-1]
            value = float(splits[-2])
            if "Gbits" in unit:
                value = 1024 * float(splits[-2])
            total_incoming_band_width += value
    print "total_incoming_band_width : %s" % total_incoming_band_width


def test_outgoing_bandwidth():
    tested_server_ip = bandwidth_task["tested_server_ip"]

    clean(tested_server_ip, server_port)
    for agent_ip in bandwidth_task["agent_ips"]:
        print "clean %s" % agent_ip
        clean(agent_ip, server_port)

    # launch multi client on server.

    # run 'iperf -s' on agents
    for agent_ip in bandwidth_task["agent_ips"]:
        agent_status = get_status(agent_ip, server_port)
        if agent_status["status"] == TaskStatus.NOT_STARTED:
            command = "iperf -s"
            start(agent_ip, server_port, command)

    task_id = 1
    for agent_ip in bandwidth_task["agent_ips"]:
        command = "iperf -c %s -t 20" % agent_ip
        start(tested_server_ip, server_port, command, task_id)
        task_id += 1

    all_server_tasked_stopped = False

    while not all_server_tasked_stopped:
        task_id = 1
        stopped_count = 0
        for agent_ip in bandwidth_task["agent_ips"]:
            task_status = get_status(tested_server_ip, server_port, task_id)
            if task_status["status"] == TaskStatus.STOPPED:
                stopped_count += 1
            task_id += 1
        if stopped_count == len(bandwidth_task["agent_ips"]):
            all_server_tasked_stopped = True
        time.sleep(10)

    # stop agnet
    for agent_ip in bandwidth_task["agent_ips"]:
        stop(agent_ip, server_port)

    total_outgoing_band_width = 0
    task_id = 1
    for agent_ip in bandwidth_task["agent_ips"]:
        task_status = get_status(tested_server_ip, server_port, task_id)
        result = task_status["result"]
        print "result [%s]: \n" % task_id
        for line in result:
            if "/sec" in line:
                print line
                splits = line.strip().split(' ')
                unit = splits[-1]
                value = float(splits[-2])
                if "Gbits" in unit:
                    value = 1024 * float(splits[-2])
                total_outgoing_band_width += value
        task_id += 1

    print "total_outgoing_band_width : %s" % total_outgoing_band_width

if __name__ == "__main__":
    test_incoming_bandwidth()
    test_outgoing_bandwidth()
