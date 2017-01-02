# import ftplib
# import os
# filename = "/tmp/hello.txt"
# ftp = ftplib.FTP("ip")
# ftp.set_debuglevel(2)
# # ftp.set_pasv(1)
# ftp.login("user", "pwd")
# print ftp.getwelcome()
# print ftp.dir()
# # ftp.cwd("/home/bmark/benchmark_results")
# # os.chdir(os.path.dirname(filename))
# # myfile = open(filename, 'rb')
# # ftp.storbinary('RETR %s' % os.path.dirname(filename), myfile)
# # # ftp.storlines('STOR ' + filename, myfile)
# # myfile.close()
