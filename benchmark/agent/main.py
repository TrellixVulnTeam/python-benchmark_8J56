import sys
import SocketServer
from benchmark.utils import config_util


def run():
    print 'abc'
    if len(sys.argv) == 1:
        agent_ini_path = "/etc/benchmark/agent.ini"
    else:
        agent_ini_path = sys.argv[1]

    CONFIG = config_util.get_config()
    CONFIG.parse_ini(agent_ini_path)

    from benchmark.utils import log_util

    LOG = log_util.get_logger(__name__)

    try:
        # clean()
        # install_packages(packages)
        # LOG.info("[local info(hostname)] " + socket.gethostname())
        # LOG.info(local_ips())
        listen_ip = CONFIG.get_opt("listen_ip", "agent")
        listen_port = CONFIG.get_int_opt("listen_port", "agent")
        LOG.info("listen on %s:%s" % (listen_ip, listen_port))
        from benchmark.agent.handler import Handler
        server = SocketServer.TCPServer((listen_ip, listen_port), Handler)
        server.serve_forever()
    except Exception, exception:
        LOG.exception(exception)

if __name__ == "__main__":
    run()
