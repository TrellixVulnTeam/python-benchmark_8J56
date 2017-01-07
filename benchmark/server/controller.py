import json
import socket
import time
from benchmark_worker import TaskStatus
from benchmark_worker import OperateType
import benchmark_worker

listen_port = benchmark_worker.listen_port
bandwidth_testing_time = 10  # default 120
pps_testing_time = 10   # default 120
pps_testing_mms = 88  # the value of 'iperf3 -M', maximum segment size
latency_testing_packaet_count = 10  # default 600
requery_delay = 5  # default 30
wait_for_task_stopped_time = 5

iperf_report_interval_plus = 5

def send_msg(ip, msg):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, listen_port))
        sock.sendall(msg + "\n")
        received = sock.recv(8192).strip()
        # print received
        return received
    except:
        print "get data from %s failed." % ip


def get_status(ip, task_id=1):
    msg = {"operate": OperateType.STATUS, "task_id": task_id}
    received = send_msg(ip, json.dumps(msg))
    # print received
    return json.loads(received)


def start(ip, command, task_id=1):
    msg = {"operate": OperateType.START,
           "command": command,
           "task_id": task_id}
    received = send_msg(ip, json.dumps(msg))
    return json.loads(received)


def stop(ip, task_id=1):
    msg = {"operate": OperateType.STOP, "task_id": task_id}
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
    command = "ifconfig | grep -A 3 %s" % ip
    output = execute_command(ip, command).get("output", "")
    for line in output.split('\n'):
        if "RX packets" in line:
            print line
            rx_packets = float(line.strip().split(' ')[2])
            return rx_packets
    raise Exception("cannto get rx from ifconfig")


def get_latency_in_ping_output(master, slave):
    command = "ping -q -c %s %s" % (latency_testing_packaet_count, slave)
    output = execute_command(master, command).get("output", "")
    for line in output.split('\n'):
        # print line
        if "rtt min/avg/max/mdev" in line:
            latency = float(line.strip().split('=')[1].split('/')[1])
            return latency


def get_incoming_bandwidth(servers_config):
    """
    get incoming bandwidth
    :param servers_config: eg:
    {"master": "10.0.0.1", "slaves": ["10.0.0.2", "10.0.0.3"]}
    :return: incoming bandwidth
    """
    master = servers_config["master"]

    # clean env on master
    clean(master)

    # clean env on slaves
    for slave in servers_config["slaves"]:
        clean(slave)

    # start master
    command = "iperf3 -s -f m -i %s" % (bandwidth_testing_time+iperf_report_interval_plus)
    # print "start %s with command: %s" % (master, command)
    start(master, command)

    for slave in servers_config["slaves"]:
        agent_status = get_status(slave)
        if agent_status["status"] == TaskStatus.NOT_STARTED:
            command = "iperf3 -f m -i %s -c %s -t %s" % \
                      ((bandwidth_testing_time+iperf_report_interval_plus), master, bandwidth_testing_time)
            start(slave, command)
    time.sleep(bandwidth_testing_time + requery_delay)

    # are all slave work done
    is_all_slave_work_done = False
    while not is_all_slave_work_done:
        master_status = get_status(master)
        if master_status["status"] == TaskStatus.RUNNING:
            stopped_count = 0
            for slave in servers_config["slaves"]:
                agent_status = get_status(slave)
                if agent_status["status"] == TaskStatus.FINISHED:
                    stopped_count += 1
                    if stopped_count == len(servers_config["slaves"]):
                        is_all_slave_work_done = True
        time.sleep(requery_delay)

    # stop master and get status
    # print "stop %s running by command: %s" % (master, command)
    stop(master)
    while True:
        master_status = get_status(master)
        if master_status["status"] == TaskStatus.FINISHED:
            result = master_status["result"]
            break
        time.sleep(wait_for_task_stopped_time)

    total_incoming_band_width = 0
    # print "result is: \n"
    for line in result.split("\n"):
        print line
        if "/sec" in line and "receiver" in line:
            str_value = line.split('Mbits/sec')[0].strip().split(' ')[-1]
            # print str_value
            value = float(str_value)
            total_incoming_band_width += value
    print "[%s] total_incoming_band_width : %s Mbps" % \
          (master, total_incoming_band_width)
    return total_incoming_band_width


def get_outgoing_bandwidth(servers_config):
    """
    get outgoing bandwidth
    :param servers_config: eg:
    {"master": "10.0.0.1", "slaves": ["10.0.0.2", "10.0.0.3"]}
    :return: outgoing bandwidth
    """
    master = servers_config["master"]
    # clean env on master
    clean(master)

    # clean env on slaves
    for slave in servers_config["slaves"]:
        clean(slave)

    # run 'iperf3 -s -f m ' on slaves
    for slave in servers_config["slaves"]:
        agent_status = get_status(slave)
        if agent_status["status"] == TaskStatus.NOT_STARTED:
            command = "iperf3 -s -f m -i %s " % (bandwidth_testing_time+iperf_report_interval_plus)
            start(slave, command)

    task_id = 1
    for slave in servers_config["slaves"]:
        command = "iperf3 -f m -i %s -c %s -t %s" % \
                  ((bandwidth_testing_time+iperf_report_interval_plus), slave, bandwidth_testing_time)
        start(master, command, task_id)
        task_id += 1
    time.sleep(bandwidth_testing_time + requery_delay)

    all_master_tasks_done = False

    while not all_master_tasks_done:
        task_id = 1
        stopped_count = 0
        for slave in servers_config["slaves"]:
            task_status = get_status(master, task_id)
            if task_status["status"] == TaskStatus.FINISHED:
                stopped_count += 1
            task_id += 1
        if stopped_count == len(servers_config["slaves"]):
            all_master_tasks_done = True
        time.sleep(requery_delay)

    # stop agnet
    for slave in servers_config["slaves"]:
        stop(slave)

    total_outgoing_band_width = 0
    task_id = 1
    for slave in servers_config["slaves"]:
        task_status = get_status(master, task_id)
        result = task_status["result"]
        # print "result [%s]: \n" % task_id
        for line in result.split("\n"):
            if "/sec" in line and "sender" in line:
                print line
                str_value = line.split('Mbits/sec')[0].strip().split(' ')[-1]
                print str_value
                value = float(str_value)
                total_outgoing_band_width += value
        task_id += 1
    print "[%s] total_outgoing_band_width : %s Mbps" % \
          (master, total_outgoing_band_width)
    return total_outgoing_band_width


def get_pps(servers_config):
    """
    get package per second
    :param servers_config: eg:
    {"master": "10.0.0.1", "slaves": ["10.0.0.2", "10.0.0.3"]}
    :return: packets per second
    """
    master = servers_config["master"]

    # clean env on master
    clean(master)

    # clean env on slaves
    for slave in servers_config["slaves"]:
        clean(slave)

    # start master
    start_rx = get_rx(master)
    start(master, "iperf3 -f m -i %s -s" % (iperf_report_interval_plus+pps_testing_time))

    for slave in servers_config["slaves"]:
        agent_status = get_status(slave)
        if agent_status["status"] == TaskStatus.NOT_STARTED:
            command = "iperf3 -f m -i %s -c %s -t %s -M %s" % \
                      ((iperf_report_interval_plus+pps_testing_time), master,
                       pps_testing_time, pps_testing_mms)
            start(slave, command)
    time.sleep(pps_testing_time + requery_delay)

    # are all slave work done
    is_all_slave_work_done = False
    while not is_all_slave_work_done:
        master_status = get_status(master)
        if master_status["status"] == TaskStatus.RUNNING:
            stopped_count = 0
            for slave in servers_config["slaves"]:
                agent_status = get_status(slave)
                if agent_status["status"] == TaskStatus.FINISHED:
                    stopped_count += 1
                    if stopped_count == len(servers_config["slaves"]):
                        is_all_slave_work_done = True
        time.sleep(requery_delay)

    # stop master and get status
    stop(master)
    end_rx = get_rx(master)

    pps = (end_rx - start_rx) / pps_testing_time
    print "[%s] pps : %s" % (master, pps)
    return pps


def get_latency(servers_config):
    latencies = []
    avg_latency = 0
    master = servers_config["master"]

    # clean env on master
    clean(master)

    # clean env on slaves
    for slave in servers_config["slaves"]:
        latency = get_latency_in_ping_output(master, slave)
        latencies.append(latency)
    if len(latencies) != 0:
        avg_latency = sum(latencies) / len(latencies)
    print "[%s] avg latency : %s" % (master, avg_latency)


if __name__ == "__main__":
    bandwidth_10_12_10_52 = {"master": "10.12.10.52",
                             "slaves": ["10.12.10.53"]}
    pps_10_12_10_52 = {"master": "10.12.10.52", "slaves": ["10.12.10.53"]}
    latency_10_12_10_52 = {"master": "10.12.10.52",
                           "slaves": ["10.12.10.53"]}

    get_incoming_bandwidth(bandwidth_10_12_10_52)
    # get_outgoing_bandwidth(bandwidth_10_12_10_52)
    # get_pps(pps_10_12_10_52)
    # get_latency(latency_10_12_10_52)

    # ip_10_12_10_53 = {"master": "10.12.10.52", "slaves": ["10.12.10.53"]}
    # get_incoming_bandwidth(ip_10_12_10_53)
    # get_outgoing_bandwidth(ip_10_12_10_53)

    # bandwidth = {"master": "10.200.6.46",
    #              "slaves": ["10.200.8.12",
    #                         "10.200.8.28",
    #                         "10.200.8.38",
    #                         "10.200.10.12"]}
    # pps = {"master": "10.200.6.46", "slaves": ["10.200.8.12"]}
    # latency = {"master": "10.200.6.46",
    #            "slaves": ["10.200.6.46", "10.200.8.28"]}
    #
    # get_incoming_bandwidth(bandwidth)
    # get_outgoing_bandwidth(bandwidth)
    # get_pps(pps)
    # get_latency(latency)
