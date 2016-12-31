import unittest

import utils.process_util as process_util


class TestProcessUtil(unittest.TestCase):
    def setUp(self):
        self.all_tars_dir = "/tmp/benchmark_result"
        self.result_tar_file = "/tmp/benchmark_result/" \
                               "10.0.246.132_24-2016-12-28-22-05-02.tar.gz"
        self.result_path = "./files"

    def tearDown(self):
        pass

    def test_get_all_tar_files(self):
        files = process_util.get_all_tar_files()
        for file_name in files:
            print file_name

    def test_get_ip_time_from_dir(self):
        ip, time_str = process_util.get_ip_time_from_tar_path(
            self.result_tar_file)
        print ip
        print time_str

    def test_get_cpu_result(self):
        cpu_test_result_file = "%s/cpu_test.txt" % self.result_path
        cpu_test_result = process_util.get_cpu_result(cpu_test_result_file)
        print cpu_test_result

    def test_get_memory_result(self):
        memory_test_result_file = "%s/memory_test.txt" % self.result_path
        memory_test_result = process_util.get_memory_result(
            memory_test_result_file)
        print memory_test_result

    def test_get_one_io_result(self):
        path = "%s/%s" % (self.result_path,
                          "io_test_data_disk_4k_rand_write.txt")
        result = process_util.get_one_io_result(path)
        print result

    def test_get_all_io_result(self):
        result = process_util.get_all_io_result(self.result_path)
        print result

    def test_process_one_result(self):
        process_util.process_one_result(self.result_tar_file)

    def test_process_all_tars(self):
        process_util.process_all_tars(self.all_tars_dir)
