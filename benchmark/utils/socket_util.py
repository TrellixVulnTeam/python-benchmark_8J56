import json
import socket
import traceback

from benchmark.constant.return_code import ReturnCode
from benchmark.utils import log_util
from benchmark.utils import config_util

LOG = log_util.get_logger(__name__)
CONFIG = config_util.get_config()


def send_request(ip, port, message_str):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))

        LOG.debug("send request to %s:  %s" % (ip, message_str))
        sock.sendall(message_str + "\n")

        response = sock.recv(8192).strip()
        LOG.debug("get response from %s: %s" % (ip, response))
        return response
    except Exception, exception:
        LOG.exception(exception)
        LOG.error("get response from %s failed" % ip)
        return json.dumps({"code": ReturnCode.FAILED,
                           "message_str": traceback.format_exc()})


def rpc_call(ip, message_dict):
    agent_port = CONFIG.get_int_opt("agent_port", "agent")
    message = json.dumps(message_dict)
    response_str = send_request(ip, agent_port, message)
    return json.loads(response_str)
