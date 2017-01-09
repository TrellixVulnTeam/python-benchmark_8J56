from fabric.api import env
from fabric.api import run
from fabric.tasks import execute


def wrapper_run(command, key_file=None):
    env.key_filename = key_file
    run(command)


def wrapper_execute(host_config, command, key_file=None):
    execute(wrapper_run, command, key_file, host=host_config)


def execute_remote_command_one_host(ip, user, port, command,
                                    key_file=None):
    host_string = "%s@%s:%s" % (user, ip, port)
    wrapper_execute(host_string, command, key_file)


def execute_remote_command_multiple_hosts(ips, users, ports, command,
                                          key_files=None):
    count = len(ips)
    for i in xrange(count):
        ip = ips[i]
        user = users[i]
        port = ports[i]
        key_file = key_files[i]
        execute_remote_command_one_host(ip, user, port, command, key_file)
