import subprocess
from benchmark.utils import log_util
from benchmark import constants


LOG = log_util.get_logger(__name__)

def install_packages(packages):
    for package in packages:
        existed_command = "rpm -qa | grep %s" % package
        try:
            subprocess.check_output([existed_command], shell=True)
        except:
            LOG.debug("%s is not installed, install it" % package)
            sudo = "sudo" if constants.run_command_as_sudo else ""
            cmd = "%s yum -y install %s" % (sudo, package)
            LOG.debug(cmd)
            subprocess.check_output([cmd], shell=True)
