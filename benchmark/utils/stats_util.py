import mongo_util


def avg(values):
    # print values
    if len(values) == 0:
        return 0
    return sum(values, 0.0) / len(values)


def get_one_statistics_avg(ip):
    # print ip
    results = mongo_util.find_test_results(ip)
    cpu_values = []
    memory_ops_per_second_values = []
    memory_transferred_mb_per_second = []

    # bandwidth
    io_rootfs_4k_rand_read_bw = []
    io_rootfs_4k_rand_write_bw = []
    io_rootfs_64k_seq_read_bw = []
    io_rootfs_64k_seq_write_bw = []
    io_data_disk_4k_rand_read_bw = []
    io_data_disk_4k_rand_write_bw = []
    io_data_disk_64k_seq_read_bw = []
    io_data_disk_64k_seq_write_bw = []

    # iops
    io_rootfs_4k_rand_read_iops = []
    io_rootfs_4k_rand_write_iops = []
    io_rootfs_64k_seq_read_iops = []
    io_rootfs_64k_seq_write_iops = []
    io_data_disk_4k_rand_read_iops = []
    io_data_disk_4k_rand_write_iops = []
    io_data_disk_64k_seq_read_iops = []
    io_data_disk_64k_seq_write_iops = []

    for result in results:
        cpu_values.append(float(result["cpu"]))
        memory_ops_per_second_values.append(
            float(result["memory"]["ops_per_second"]))
        memory_transferred_mb_per_second.append(
            float(result["memory"]["transferred_mb_per_second"]))

        # rootfs
        io_rootfs_4k_rand_read_bw.append(
            float(result["io"]["rootfs_4k_rand_read"]["bw_kb_per_sec"]))
        io_rootfs_4k_rand_read_iops.append(
            float(result["io"]["rootfs_4k_rand_read"]["iops"]))

        io_rootfs_4k_rand_write_bw.append(
            float(result["io"]["rootfs_4k_rand_write"]["bw_kb_per_sec"]))
        io_rootfs_4k_rand_write_iops.append(
            float(result["io"]["rootfs_4k_rand_write"]["iops"]))

        io_rootfs_64k_seq_read_bw.append(
            float(result["io"]["rootfs_64k_seq_read"]["bw_kb_per_sec"]))
        io_rootfs_64k_seq_read_iops.append(
            float(result["io"]["rootfs_64k_seq_read"]["iops"]))

        io_rootfs_64k_seq_write_bw.append(
            float(result["io"]["rootfs_64k_seq_write"]["bw_kb_per_sec"]))
        io_rootfs_64k_seq_write_iops.append(
            float(result["io"]["rootfs_64k_seq_write"]["iops"]))

        # data disk
        io_data_disk_4k_rand_read_bw.append(
            float(result["io"]["data_disk_4k_rand_read"]["bw_kb_per_sec"]))
        io_data_disk_4k_rand_read_iops.append(
            float(result["io"]["data_disk_4k_rand_read"]["iops"]))

        io_data_disk_4k_rand_write_bw.append(
            float(result["io"]["data_disk_4k_rand_write"]["bw_kb_per_sec"]))
        io_data_disk_4k_rand_write_iops.append(
            float(result["io"]["data_disk_4k_rand_write"]["iops"]))

        io_data_disk_64k_seq_read_bw.append(
            float(result["io"]["data_disk_64k_seq_read"]["bw_kb_per_sec"]))
        io_data_disk_64k_seq_read_iops.append(
            float(result["io"]["data_disk_64k_seq_read"]["iops"]))

        io_data_disk_64k_seq_write_bw.append(
            float(result["io"]["data_disk_64k_seq_write"]["bw_kb_per_sec"]))
        io_data_disk_64k_seq_write_iops.append(
            float(result["io"]["data_disk_64k_seq_write"]["iops"]))

    return {
            "ip": ip,
            "cpu": avg(cpu_values),
            "memory": {"ops_per_second": avg(memory_ops_per_second_values),
                       "transferred_mb_per_second":
                           avg(memory_transferred_mb_per_second)},
            "io": {
                "rootfs_4k_rand_read": {
                    "bw_kb_per_sec": avg(io_rootfs_4k_rand_read_bw),
                    "iops": avg(io_rootfs_4k_rand_read_iops)},
                "rootfs_4k_rand_write": {
                    "bw_kb_per_sec": avg(io_rootfs_4k_rand_write_bw),
                    "iops": avg(io_rootfs_4k_rand_write_iops)},
                "rootfs_64k_seq_read": {
                    "bw_kb_per_sec": avg(io_rootfs_64k_seq_read_bw),
                    "iops": avg(io_rootfs_64k_seq_read_iops)},
                "rootfs_64k_seq_write": {
                    "bw_kb_per_sec": avg(io_rootfs_64k_seq_write_bw),
                    "iops": avg(io_rootfs_64k_seq_write_iops)},

                "data_disk_4k_rand_read": {
                    "bw_kb_per_sec": avg(io_data_disk_4k_rand_read_bw),
                    "iops": avg(io_data_disk_4k_rand_read_iops)},
                "data_disk_4k_rand_write": {
                    "bw_kb_per_sec": avg(io_data_disk_4k_rand_write_bw),
                    "iops": avg(io_data_disk_4k_rand_write_iops)},
                "data_disk_64k_seq_read": {
                    "bw_kb_per_sec": avg(io_data_disk_64k_seq_read_bw),
                    "iops": avg(io_data_disk_64k_seq_read_iops)},
                "data_disk_64k_seq_write": {
                    "bw_kb_per_sec": avg(io_data_disk_64k_seq_write_bw),
                    "iops": avg(io_data_disk_64k_seq_write_iops)}

            }
            }


def get_all_statistics_avg():
    servers = mongo_util.get_all_servers()
    all_statistics = []
    for server in servers:
        statistics = get_one_statistics_avg(server["ip"])
        all_statistics.append(statistics)
    return all_statistics


def get_statistics_by_server_id(server_id):
    server = mongo_util.get_server("id", server_id)
    ip = server["ip"]
    return get_one_statistics_avg(ip)



