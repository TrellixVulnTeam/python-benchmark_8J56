import json
import socket
import time
from benchmark_worker import TaskStatus
from benchmark_worker import OperateType
from benchmark_worker import ReturnCode
import benchmark_worker

listen_port = benchmark_worker.listen_port
bandwidth_testing_time = 10 # default 120
pps_testing_time = 120
latency_testing_time = 600
requery_delay = 5 # default 30
wait_for_task_stopped_time = 5

def send_msg(ip, msg):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, listen_port))
    sock.sendall(msg + "\n")

    received = sock.recv(8192).strip()
    # print received
    return received


def get_status(ip, task_id=1):
    msg = {"operate": OperateType.STATUS, "task_id": task_id}
    received = send_msg(ip, json.dumps(msg))
    return json.loads(received)


def start(ip, command, task_id=1):
    msg = {"operate": OperateType.START, "command": command, "task_id": task_id}
    received = send_msg(ip, json.dumps(msg))
    return json.loads(received)


def stop(ip, task_id=1):
    msg = {"operate": OperateType.KILL, "task_id": task_id}
    received = send_msg(ip, json.dumps(msg))
    return json.loads(received)


def clean(ip):
    msg = {"operate": OperateType.CLEAN}
    received = send_msg(ip, json.dumps(msg))
    return json.loads(received)


def execute_command(ip, command):
    msg = {"operate": OperateType.DIRECT_COMMAND, "command": command}
    received = send_msg(ip, json.dumps(msg))
    return json.loads(received)


def get_rx(ip):
    command = "ifconfig"
    output = execute_command(ip, command)
    print output


def get_incoming_bandwidth(servers_config):
    """
    get incoming bandwidth
    :param servers_config: eg: {"master": "10.0.0.1", "slaves": ["10.0.0.2", "10.0.0.3"]}
    :return:
    """
    master = servers_config["master"]

    # clean env on master
    clean(master)

    # clean env on slaves
    for slave in servers_config["slaves"]:
        clean(slave)

    # start master
    command = "iperf -s"
    # print "start %s with command: %s" % (master, command)
    start(master, command)

    # are all slave work done
    is_all_slave_work_done = False
    while not is_all_slave_work_done:
        master_status = get_status(master)
        if master_status["status"] == TaskStatus.RUNNING:
            stopped_count = 0
            for slave in servers_config["slaves"]:
                agent_status = get_status(slave)
                if agent_status["status"] == TaskStatus.NOT_STARTED:
                    command = "iperf -c %s -t %s" % (master, bandwidth_testing_time)
                    start(slave, command)
                elif agent_status["status"] == TaskStatus.STOPPED:
                    stopped_count += 1
                    if stopped_count == len(servers_config["slaves"]):
                        is_all_slave_work_done = True
        time.sleep(bandwidth_testing_time + requery_delay)

    # stop master and get status
    # print "stop %s running by command: %s" % (master, command)
    stop(master)
    while True:
        master_status = get_status(master)
        if master_status["status"] == TaskStatus.STOPPED:
            result = master_status["result"]
            break
        time.sleep(wait_for_task_stopped_time)

    total_incoming_band_width = 0
    # print "result is: \n"
    for line in result:
        if "/sec" in line:
            print line
            splits = line.strip().split(' ')
            unit = splits[-1]
            value = float(splits[-2])
            if "Gbits" in unit:
                value = 1024 * float(splits[-2])
            total_incoming_band_width += value
    print "[%s] total_incoming_band_width : %s" % (master, total_incoming_band_width)


def get_outgoing_bandwidth(servers_config):
    """
    get outgoing bandwidth
    :param servers_config: eg: {"master": "10.0.0.1", "slaves": ["10.0.0.2", "10.0.0.3"]}
    """
    master = servers_config["master"]
    # clean env on master
    clean(master)

    # clean env on slaves
    for slave in servers_config["slaves"]:
        clean(slave)

    # run 'iperf -s' on slaves
    for slave in servers_config["slaves"]:
        agent_status = get_status(slave)
        if agent_status["status"] == TaskStatus.NOT_STARTED:
            command = "iperf -s"
            start(slave, command)

    task_id = 1
    for slave in servers_config["slaves"]:
        command = "iperf -c %s -t %s" % (slave, bandwidth_testing_time)
        start(master, command, task_id)
        task_id += 1

    all_master_tasks_done = False

    while not all_master_tasks_done:
        task_id = 1
        stopped_count = 0
        for slave in servers_config["slaves"]:
            task_status = get_status(master, task_id)
            if task_status["status"] == TaskStatus.STOPPED:
                stopped_count += 1
            task_id += 1
        if stopped_count == len(servers_config["slaves"]):
            all_master_tasks_done = True
        time.sleep(bandwidth_testing_time + requery_delay)

    # stop agnet
    for slave in servers_config["slaves"]:
        stop(slave)

    total_outgoing_band_width = 0
    task_id = 1
    for slave in servers_config["slaves"]:
        task_status = get_status(master, task_id)
        result = task_status["result"]
        # print "result [%s]: \n" % task_id
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

    print "[%s] total_outgoing_band_width : %s" % (master, total_outgoing_band_width)


def get_pps(servers_config):
    """
    get package per second
    :param servers_config: eg: {"master": "10.0.0.1", "slaves": ["10.0.0.2", "10.0.0.3"]}
    :return:
    """
    master = servers_config["master"]

    # clean env on master
    clean(master)

    # clean env on slaves
    for slave in servers_config["slaves"]:
        clean(slave)

    # start master
    start_rx = get_rx(master)
    start(master, "iperf -s")

    # are all slave work done
    is_all_slave_work_done = False
    while not is_all_slave_work_done:
        master_status = get_status(master)
        if master_status["status"] == TaskStatus.RUNNING:
            stopped_count = 0
            for slave in servers_config["slaves"]:
                agent_status = get_status(slave)
                if agent_status["status"] == TaskStatus.NOT_STARTED:
                    command = "iperf -c %s -t %s -M %s" % (master, bandwidth_testing_time, M)
                    start(slave, command)
                elif agent_status["status"] == TaskStatus.STOPPED:
                    stopped_count += 1
                    if stopped_count == len(servers_config["slaves"]):
                        is_all_slave_work_done = True
        time.sleep(bandwidth_testing_time + requery_delay)

    # stop master and get status
    stop(master)
    end_rx = get_rx(master)
    print "[%s] pps : %s" % (master, total_incoming_band_width) # end_rx - start_rx





if __name__ == "__main__":
    ip_10_12_10_52 = {"master": "10.12.10.52", "slaves": ["10.12.10.53"]}
    # get_incoming_bandwidth(ip_10_12_10_52)
    # get_outgoing_bandwidth(ip_10_12_10_52)
    get_pps(ip_10_12_10_52)

    # ip_10_12_10_53 = {"master": "10.12.10.52", "slaves": ["10.12.10.53"]}
    # get_incoming_bandwidth(ip_10_12_10_53)
    # get_outgoing_bandwidth(ip_10_12_10_53)



