# -*- coding: utf-8 -*-
import mongo_util
import process_util
from benchmark import settings


def init_servers():
    """
    初始化servers,如果server id已经存在,会更新MongoDB里面的数据.
    """
    # qcloud
    servers = []
    server1 = {"id": 1, "ip": "10.0.246.150/24", "company": "qcloud",
               "series": "系列1", "type": "高IO型I1", "core": 8, "memory": 16,
               "data_disk_type": "local_ssd"}
    servers.append(server1)

    server2 = {"id": 2, "ip": "10.0.246.23/24", "company": "qcloud",
               "series": "系列2", "type": "标准型S2", "core": 8, "memory": 16,
               "data_disk_type": "cloud"}
    servers.append(server2)

    server3 = {"id": 3, "ip": "10.0.246.132/24", "company": "qcloud",
               "series": "系列2", "type": "标准型S2", "core": 8, "memory": 16,
               "data_disk_type": "cloud_ssd"}
    servers.append(server3)

    server4 = {"id": 4, "ip": "10.0.246.94/24", "company": "qcloud",
               "series": "系列2", "type": "内存型M2", "core": 2, "memory": 16,
               "data_disk_type": "cloud"}
    servers.append(server4)

    server5 = {"id": 5, "ip": "10.0.246.90/24", "company": "qcloud",
               "series": "系列2", "type": "计算型C2", "core": 8, "memory": 16,
               "data_disk_type": "cloud_ssd"}
    servers.append(server5)

    # aliyun
    server6 = {"id": 6, "ip": "10.100.5.6/24", "company": "aliyun",
               "series": "系列II", "type": "独享型sn1", "core": 8, "memory": 16,
               "data_disk_type": "cloud"}
    servers.append(server6)

    server7 = {"id": 7, "ip": "10.100.5.7/24", "company": "aliyun",
               "series": "系列II", "type": "独享型sn1", "core": 8, "memory": 16,
               "data_disk_type": "cloud_ssd"}
    servers.append(server7)

    server8 = {"id": 8, "ip": "10.100.5.8/24", "company": "aliyun",
               "series": "系列III", "type": "通用型n4", "core": 8, "memory": 16,
               "data_disk_type": "cloud"}
    servers.append(server8)

    server9 = {"id": 9, "ip": "10.100.5.9/24", "company": "aliyun",
               "series": "系列III", "type": "通用型n4", "core": 8, "memory": 16,
               "data_disk_type": "cloud_ssd"}
    servers.append(server9)

    server10 = {"id": 10, "ip": "10.100.5.10/24", "company": "aliyun",
                "series": "系列III", "type": "内存型e4", "core": 2, "memory": 16,
                "data_disk_type": "cloud"}
    servers.append(server10)

    server11 = {"id": 11, "ip": "10.100.5.11/24", "company": "aliyun",
                "series": "系列III", "type": "内存型e4", "core": 2, "memory": 16,
                "data_disk_type": "cloud_ssd"}
    servers.append(server11)

    # aws
    server12 = {"id": 12, "ip": "10.30.0.66/24", "company": "aws",
                "series": "计算型", "type": "C3", "core": 8, "memory": 15,
                "data_disk_type": "GP2"}
    servers.append(server12)

    server13 = {"id": 13, "ip": "10.30.0.86/24", "company": "aws",
                "series": "计算型", "type": "C4", "core": 8, "memory": 15,
                "data_disk_type": "ssd"}
    servers.append(server13)

    server14 = {"id": 14, "ip": "10.30.0.131/24", "company": "aws",
                "series": "内存型", "type": "R4", "core": 4, "memory": 30.5,
                "data_disk_type": "GP2"}
    servers.append(server14)

    server15 = {"id": 15, "ip": "10.30.0.28/24", "company": "aws",
                "series": "存储型", "type": "I2", "core": 4, "memory": 30.5,
                "data_disk_type": "ssd"}
    servers.append(server15)

    mongo_util.insert_many_server(servers)


def init_charts():
    """
    初始化图表,如果chart id已经存在,会更新MongoDB里面的数据.
    """
    charts = []
    chart1 = {"id": 1, "title": "CPU计算能力", "servers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
              "sub_title": "相对性能 = (20w)/(计算20w内最大素数时间),越大性能越好。命令: sysbench --num-threads=64 --test=cpu --cpu-max-prime=200000 run",
              "x_axis": "", "y_axis": "相对性能(20w/计算20内最大素数所花时间)",
              "key":"cpu", "x_axis_names": ["company", "series", "type", "core", "memory"],
              "unit": ""
              }
    charts.append(chart1)

    chart2 = {"id": 2, "title": "内存-传输速率", "servers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
              "sub_title": "sysbench --test=memory --num-threads=1 --memory-block-size=4096 --memory-total-size=4G run",
              "x_axis": "", "y_axis": "传输速率(MB/s)",
              "key": "memory/transferred_mb_per_second", "x_axis_names": ["company", "series", "type", "core", "memory"],
              "unit": "MB/s"
              }
    charts.append(chart2)

    chart3 = {"id": 3, "title": "内存-operations per second",
              "servers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
              "sub_title": "sysbench --test=memory --num-threads=1 --memory-block-size=4096 --memory-total-size=4G run",
              "x_axis": "", "y_axis": "operations per second",
              "key": "memory/ops_per_second",
              "x_axis_names": ["company", "series", "type", "core", "memory"],
              "unit": ""
              }
    charts.append(chart3)

    chart4 = {"id": 4, "title": "数据盘IOPS测试(4k随机写)", "servers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
              "sub_title": "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=test --bs=4k --iodepth=64 --size=4G --readwrite=randwrite",
              "x_axis": "", "y_axis": "iops",
              "key": "io/data_disk_4k_rand_write/iops", "x_axis_names": ["company", "series", "type", "core", "memory", "data_disk_type"],
              "unit": ""
              }
    charts.append(chart4)

    chart5 = {"id": 5, "title": "数据盘吞吐测试(64k顺序读)", "servers": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
              "sub_title": "fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=/dev/vdb --bs=64k --iodepth=64 --size=20G --readwrite=read --runtime=600",
              "x_axis": "", "y_axis": "数据盘吞吐速率(MB/s)",
              "key": "io/data_disk_64k_seq_read/bw_kb_per_sec", "x_axis_names": ["company", "series", "type", "core", "memory", "data_disk_type"],
              "unit": "MB/s"
              }
    charts.append(chart5)

    mongo_util.insert_many_charts(charts)


if __name__ == '__main__':
    mongo_util.truncate_charts()
    mongo_util.truncate_servers()
    mongo_util.truncate_test_results()

    init_servers()
    init_charts()
    process_util.process_all_tars(settings.result_dir)

