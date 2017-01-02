import os

import mongo_util
import tar_util
from benchmark import settings


def get_all_tar_files(all_tars_dir=settings.result_dir):
    files = []
    for file_name in os.listdir(all_tars_dir):
        if file_name.endswith(".tar.gz"):
            files.append("%s/%s" % (settings.result_dir, file_name))
    return files


def get_ip_time_from_tar_path(tar_path):
    base_name = os.path.basename(tar_path)
    file_name = base_name.strip(".tar.gz")
    ip_time = file_name.split('-', 1)
    ip = ip_time[0].replace('_', '/')
    time_str = ip_time[1]
    return ip, time_str


def import_hardware_info(extracted_result_path):
    pass


def get_cpu_result(cpu_result_file):
    with open(cpu_result_file) as f:
        for line in f.readlines():
            if "total time:" in line:
                cpu_result = line.split(':')[1].strip().replace('s', '')
                return 200000 / float(cpu_result)


def get_memory_result(memory_result_file):
    with open(memory_result_file) as f:
        for line in f.readlines():
            if "Operations performed:" in line:
                memory_ops_per_second_result = line.split('(')[1].replace(
                    'ops/sec)', '').strip()
            if "transferred (" in line:
                memory_trans_per_second_result = line.split('(')[1].replace(
                    'MB/sec)', '').strip()
    return {"ops_per_second": float(memory_ops_per_second_result),
            "transferred_mb_per_second": float(memory_trans_per_second_result)}


def get_all_io_result(io_result_path):
    # rootfs
    rootfs_4k_rand_read_file = "%s/io_test_rootfs_4k_rand_read.txt" \
                               % io_result_path
    rootfs_4k_rand_read_result = get_one_io_result(rootfs_4k_rand_read_file)

    rootfs_4k_rand_write_file = "%s/io_test_rootfs_4k_rand_write.txt" \
                                % io_result_path
    rootfs_4k_rand_write_result = get_one_io_result(rootfs_4k_rand_write_file)

    rootfs_64k_seq_read_file = "%s/io_test_rootfs_64k_seq_read.txt" \
                               % io_result_path
    rootfs_64k_seq_read_result = get_one_io_result(rootfs_64k_seq_read_file)

    rootfs_64k_seq_write_file = "%s/io_test_rootfs_64k_seq_write.txt" \
                                % io_result_path
    rootfs_64k_seq_write_result = get_one_io_result(rootfs_64k_seq_write_file)

    # data disk
    data_disk_4k_rand_read_file = "%s/io_test_data_disk_4k_rand_read.txt" \
                                  % io_result_path
    data_disk_4k_rand_read_result = get_one_io_result(
        data_disk_4k_rand_read_file)

    data_disk_4k_rand_write_file = "%s/io_test_data_disk_4k_rand_write.txt" \
                                   % io_result_path
    data_disk_4k_rand_write_result = get_one_io_result(
        data_disk_4k_rand_write_file)

    data_disk_64k_seq_read_file = "%s/io_test_data_disk_64k_seq_read.txt" \
                                  % io_result_path
    data_disk_64k_seq_read_result = get_one_io_result(
        data_disk_64k_seq_read_file)

    data_disk_64k_seq_write_file = "%s/io_test_data_disk_64k_seq_write.txt" \
                                   % io_result_path
    data_disk_64k_seq_write_result = get_one_io_result(
        data_disk_64k_seq_write_file)

    return {"rootfs_4k_rand_read": rootfs_4k_rand_read_result,
            "rootfs_4k_rand_write": rootfs_4k_rand_write_result,
            "rootfs_64k_seq_read": rootfs_64k_seq_read_result,
            "rootfs_64k_seq_write": rootfs_64k_seq_write_result,
            "data_disk_4k_rand_read": data_disk_4k_rand_read_result,
            "data_disk_4k_rand_write": data_disk_4k_rand_write_result,
            "data_disk_64k_seq_read": data_disk_64k_seq_read_result,
            "data_disk_64k_seq_write": data_disk_64k_seq_write_result
            }


def get_one_io_result(io_result_file):
    with open(io_result_file) as f:
        for line in f.readlines():
            if "io" in line and "bw" in line \
                    and "iops" in line and "runt" in line:
                sections = line.split(",")
                io_section = sections[0]
                bw_section = sections[1]
                iops_section = sections[2]
                runt_section = sections[3]

                type = io_section.split('=')[0].split(':')[0].strip()
                io = io_section.split('=')[1].replace('MB', '').strip()

                # eg:
                # bw=12047KB/s
                bw_with_unit = bw_section.split('=')[1]
                if "KB/s" in bw_with_unit:
                    bw = float(bw_with_unit.replace('KB/s', '').strip())
                elif "MB/s" in bw_with_unit:
                    bw = float(
                        bw_with_unit.replace('MB/s', '').strip()) * 1024.0
                elif "B/s" in bw_with_unit:
                    bw = float(
                        bw_with_unit.replace('B/s', '').strip()) / 1024.0

                iops = float(iops_section.split('=')[1].strip())
                runt = float(
                    runt_section.split('=')[1].replace('msec', '').strip())
                # convert the unit of bandwidth to MB
                return {"type": type, "io_mb": io,
                        "bw_kb_per_sec": bw / 1024.0,
                        "iops": iops, "runt_msec": runt}


def process_one_result(result_tar_path):
    ip, time_str = get_ip_time_from_tar_path(result_tar_path)
    # print "process %s %s" % (ip, time_str)
    # if result existed, return
    if mongo_util.result_existed(ip, time_str):
        return

    # extract tar
    extracted_result_path = tar_util.extract_to_dir(result_tar_path)

    # save hardware info
    import_hardware_info(extracted_result_path)

    cpu_result = get_cpu_result(
        "%s/result/cpu_test.txt" % extracted_result_path)
    memory_result = get_memory_result(
        "%s/result/memory_test.txt" % extracted_result_path)
    io_result = get_all_io_result("%s/result" % extracted_result_path)

    result = {"ip": ip, "time_str": time_str, "cpu": cpu_result,
              "memory": memory_result, "io": io_result}
    # insert to mongo
    mongo_util.insert_test_result(result)

    # delete extracted files
    # shutil.rmtree(extracted_result_path)


def process_all_tars(all_tars_dir):
    result_tars = get_all_tar_files(all_tars_dir)
    for result_tar in result_tars:
        process_one_result(result_tar)
