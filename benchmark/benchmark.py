#!/usr/bin/python

import os
import subprocess
from datetime import datetime
import tarfile
import shutil

# cpu tests arguments
cpu_num_threads = 64
cpu_max_prime = 200000  # default value: 200000(20w)

# io tests arguments
io_test_run_time = 900  # default value 900
io_size = "4G"  # default value: 4G
io_data_disk_size = "20G"  # default value: 20G

# memory tests arguments
memory_block_size = 4096
memory_total_size = "4G"

# global config
ip_info_file_name = "ip_info.txt"
start_time_file_name = "start_time.txt"
end_time_file_name = "end_time.txt"
hardware_cpu_file_name = "hardware_cpu.txt"
hardware_memory_file_name = "hardware_memory.txt"
hardware_dmidecode_file_name = "hardware_dmidecode.txt"
hardware_lspci_file_name = "hardware_lspci.txt"
hardware_fdisk_file_name = "hardware_fdisk.txt"
hardware_df_file_name = "hardware_df.txt"

# test file location
cpu_test_file_name = "cpu_test.txt"
memory_test_file_name = "memory_test.txt"

io_test_rootfs_4k_rand_write_file = "io_test_rootfs_4k_rand_write.txt"
io_test_rootfs_4k_rand_read_file = "io_test_rootfs_4k_rand_read.txt"
io_test_rootfs_64k_seq_write_file = "io_test_rootfs_64k_seq_write.txt"
io_test_rootfs_64k_seq_read_file = "io_test_rootfs_64k_seq_read.txt"

io_test_data_disk_4k_rand_write_file = "io_test_data_disk_4k_rand_write.txt"
io_test_data_disk_4k_rand_read_file = "io_test_data_disk_4k_rand_read.txt"
io_test_data_disk_64k_seq_write_file = "io_test_data_disk_64k_seq_write.txt"
io_test_data_disk_64k_seq_read_file = "io_test_data_disk_64k_seq_read.txt"


def write_str_to_file(file_name, string):
    with open(file_name, 'wt') as f:
        f.write(string)


def get_ip_list_dir_name():
    ip_info_output = subprocess.check_output(
        ["/sbin/ip a | awk '/inet /{print substr($2,0,20)}' | grep -v 127.0.0.1"],
        shell=True)
    ips = []
    for ip in ip_info_output.split('\n'):
        if "127.0.0.1" not in ip:
            replace_slash = ip.replace("/", "_")
            ips.append(replace_slash)
    time_str = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')
    return ("-".join(ips)) + time_str


def get_data_disk():
    lsblk_output = subprocess.check_output(
        ["lsblk | awk '/vdb /{print $1}'"],
        shell=True)
    disk_name = lsblk_output.strip()
    disk_path = "/dev/%s" % disk_name
    return disk_path


def write_ip_to_file(file_name):
    # output ip info to file
    ip_output = subprocess.check_output(["/sbin/ip a"], shell=True)
    print ip_output
    write_str_to_file(file_name, ip_output)


def write_time_to_file(file_name):
    # output ip info to file
    output = subprocess.check_output(["date -u"], shell=True)
    write_str_to_file(file_name, output)


def write_hardware_info_to_fine(dir_name):
    output = subprocess.check_output(["sudo cat /proc/cpuinfo"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_cpu_file_name), output)

    output = subprocess.check_output(["sudo free"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_memory_file_name), output)

    output = subprocess.check_output(["sudo dmidecode"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_dmidecode_file_name),
                      output)

    output = subprocess.check_output(["sudo lspci"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_lspci_file_name), output)

    output = subprocess.check_output(["sudo fdisk -l"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_fdisk_file_name), output)

    output = subprocess.check_output(["sudo df -lTh"], shell=True)
    write_str_to_file("%s/%s" % (dir_name, hardware_df_file_name), output)


def install_packages(packages):
    for package in packages:
        cmd = "sudo yum -y install %s" % package
        print cmd
        output = subprocess.check_output([cmd], shell=True)
        print output


def cpu_test(file_name):
    cmd = "sysbench  --num-threads=%d --test=cpu --cpu-max-prime=%d run" \
          % (cpu_num_threads, cpu_max_prime)
    print "cpu test"
    print cmd
    cpu_output = subprocess.check_output([cmd], shell=True)
    print cpu_output
    write_str_to_file(file_name, cpu_output)


def memory_test(file_name):
    cmd = "sysbench --test=memory --num-threads=1 --memory-block-size=%d " \
          "--memory-total-size=%s run" % \
          (memory_block_size, memory_total_size)
    print "memory test"
    print cmd
    memory_output = subprocess.check_output([cmd], shell=True)
    print memory_output
    write_str_to_file(file_name, memory_output)


def io_test_rootfs(result_dir):
    print("rootfs 4k_rand_write")
    cmd_4k_rand_write = "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 " \
                        "--gtod_reduce=1 --name=test --filename=test --bs=4k " \
                        "--iodepth=64 --size=%s --readwrite=randwrite " \
                        "--runtime=%s > " \
                        "%s/%s" % (io_size,
                                   io_test_run_time,
                                   result_dir,
                                   io_test_rootfs_4k_rand_write_file)
    print cmd_4k_rand_write
    subprocess.check_output([cmd_4k_rand_write], shell=True)

    print("rootfs 4k_rand_read")
    cmd_4k_rand_read = "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 " \
                       "--gtod_reduce=1 --name=test --filename=test --bs=4k " \
                       "--iodepth=64 --size=%s --readwrite=randread " \
                       "--runtime=%s > " \
                       "%s/%s" % (io_size,
                                  io_test_run_time,
                                  result_dir,
                                  io_test_rootfs_4k_rand_read_file)
    print cmd_4k_rand_read
    subprocess.check_output([cmd_4k_rand_read], shell=True)

    print("rootfs 64k_seq_write")
    cmd_64k_seq_write = "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 " \
                        "--gtod_reduce=1 --name=test --filename=test " \
                        "--bs=64k --iodepth=64 --size=%s --readwrite=write " \
                        "--runtime=%s > " \
                        "%s/%s" % (io_size,
                                   io_test_run_time,
                                   result_dir,
                                   io_test_rootfs_64k_seq_write_file)
    print cmd_64k_seq_write
    subprocess.check_output([cmd_64k_seq_write], shell=True)

    print("rootfs 64k_seq_read")
    cmd_64k_seq_read = "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 " \
                       "--gtod_reduce=1 --name=test --filename=test " \
                       "--bs=64k --iodepth=64 --size=%s --readwrite=read " \
                       "--runtime=%s > " \
                       "%s/%s" % (io_size,
                                  io_test_run_time,
                                  result_dir,
                                  io_test_rootfs_64k_seq_read_file)
    print cmd_64k_seq_read
    subprocess.check_output([cmd_64k_seq_read], shell=True)


# def io_test_rootfs_4k_rand_write(file_name):
#     subprocess.check_output([
#         "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=%s --readwrite=randwrite > %s" % (
#             io_size, file_name)],
#         shell=True)
#
#
# def io_test_rootfs_4k_rand_read(file_name):
#     subprocess.check_output([
#         "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 "
#         "--name=test --filename=test --bs=4k --iodepth=64 --size=%s --readwrite=randread > %s" % (
#             io_size, file_name)],
#         shell=True)
#
#
# def io_test_rootfs_64k_seq_write(file_name):
#     subprocess.check_output([
#         "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=64k --iodepth=64 --size=%s --readwrite=write > %s" % (
#             io_size, file_name)],
#         shell=True)
#
#
# def io_test_rootfs_64k_seq_read(file_name):
#     subprocess.check_output([
#         "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=64k --iodepth=64 --size=%s --readwrite=read > %s" % (
#             io_size, file_name)],
#         shell=True)


def io_test_data_disk(result_dir):
    data_disk_path = get_data_disk()
    print(data_disk_path + "  4k_rand_write")
    cmd_4k_rand_write = "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 " \
                        "--gtod_reduce=1 --name=test --filename=%s " \
                        "--bs=4k --iodepth=64 --size=%s " \
                        "--readwrite=randwrite --runtime=%s > " \
                        "%s/%s" % (data_disk_path,
                                   io_data_disk_size,
                                   io_test_run_time,
                                   result_dir,
                                   io_test_data_disk_4k_rand_write_file)
    print cmd_4k_rand_write
    subprocess.check_output([cmd_4k_rand_write], shell=True)

    print(data_disk_path + "  4k_rand_read")
    cmd_4k_rand_read = "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 " \
                       "--gtod_reduce=1 --name=test --filename=%s " \
                       "--bs=4k --iodepth=64 --size=%s " \
                       "--readwrite=randread --runtime=%s > " \
                       "%s/%s" % (data_disk_path,
                                  io_data_disk_size,
                                  io_test_run_time,
                                  result_dir,
                                  io_test_data_disk_4k_rand_read_file)
    print cmd_4k_rand_read
    subprocess.check_output([cmd_4k_rand_read], shell=True)

    print(data_disk_path + "  64k_seq_write")
    cmd_64k_seq_write = "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 " \
                        "--gtod_reduce=1 --name=test --filename=%s " \
                        "--bs=64k --iodepth=64 --size=%s " \
                        "--readwrite=write --runtime=%s > " \
                        "%s/%s" % (data_disk_path,
                                   io_data_disk_size,
                                   io_test_run_time,
                                   result_dir,
                                   io_test_data_disk_64k_seq_write_file)
    print cmd_64k_seq_write
    subprocess.check_output([cmd_64k_seq_write], shell=True)

    print(data_disk_path + "  64k_seq_read")
    cmd_64k_seq_read = "sudo fio --randrepeat=1 --ioengine=libaio --direct=1 " \
                       "--gtod_reduce=1 --name=test --filename=%s " \
                       "--bs=64k --iodepth=64 --size=%s " \
                       "--readwrite=read --runtime=%s > " \
                       "%s/%s" % (data_disk_path,
                                  io_data_disk_size,
                                  io_test_run_time,
                                  result_dir,
                                  io_test_data_disk_64k_seq_read_file)
    print cmd_64k_seq_read
    subprocess.check_output([cmd_64k_seq_read], shell=True)


def compress_dir(src_path):
    compressed_file = "%s/%s.tar.gz" % (os.path.dirname(src_path),
                            os.path.basename(src_path))
    with tarfile.open(compressed_file, "w:gz") as tar:
        tar.add(src_path, arcname=os.path.basename(src_path))
    shutil.rmtree(src_path)
    return compressed_file


if __name__ == '__main__':
    packages = ['sysbench', 'fio', 'iperf', 'tree', 'pciutils']
    install_packages(packages)

    path = "/tmp/%s" % get_ip_list_dir_name()
    os.mkdir(path)
    print "create path: %s" % path

    hardware_dir = "%s/hardware" % path
    os.mkdir(hardware_dir)
    write_hardware_info_to_fine(hardware_dir)
    print "create hardware_dir: %s" % hardware_dir

    write_ip_to_file("%s/%s" % (path, ip_info_file_name))
    write_time_to_file("%s/%s" % (path, start_time_file_name))

    result_dir = "%s/result" % path
    os.mkdir(result_dir)

    cpu_test("%s/%s" % (result_dir, cpu_test_file_name))
    memory_test("%s/%s" % (result_dir, memory_test_file_name))

    # rootfs test
    io_test_rootfs(result_dir)

    # data disk test
    io_test_data_disk(result_dir)

    write_time_to_file("%s/%s" % (path, end_time_file_name))

    # compress result
    compressed_file = compress_dir(path)

    # todo send tar file to server
