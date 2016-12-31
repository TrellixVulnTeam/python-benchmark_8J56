import os
import shutil
import subprocess
import unittest

import utils.tar_util as tar_util


class TestTarUtil(unittest.TestCase):
    def setUp(self):
        self.test_path = "/tmp/test_tar"
        if not os.path.exists(self.test_path):
            os.mkdir(self.test_path)
        subprocess.check_output(["echo hello > %s/hello.txt" % self.test_path],
                                shell=True)

        self.tar_file = ""
        self.decompressed_dir_path = ""

    def tearDown(self):
        if os.path.exists(self.test_path):
            shutil.rmtree(self.test_path)
        if os.path.exists(self.tar_file):
            os.remove(self.tar_file)
        if os.path.exists(self.decompressed_dir_path):
            shutil.rmtree(self.decompressed_dir_path)

    def test_compress(self):
        tar_file = tar_util.compress(self.test_path)
        self.assertTrue(os.path.exists(tar_file))

    def test_depress(self):
        self.tar_file = tar_util.compress(self.test_path)
        shutil.rmtree(self.test_path)
        self.extracted_dir_path = tar_util.extract_to_dir(self.tar_file)
        self.assertTrue(os.path.exists(self.extracted_dir_path))
