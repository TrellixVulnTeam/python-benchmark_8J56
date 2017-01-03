# import subprocess
#
#
# cmd = 'ping -c 10 www.baidu.com'
# child = subprocess.Popen([cmd], shell=True)
# child.wait()
# print child.stdout
#

import subprocess
import sys

cmd = 'ping -c 5 www.baidu.com'
process = subprocess.Popen(
    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
)
print process.pid
str = ""
while True:
    out = process.stdout.read(1)
    if out == '' and process.poll() != None:
        break
    if out != '':
        str+=out
        # sys.stdout.write(out)
        sys.stdout.flush()

print str
