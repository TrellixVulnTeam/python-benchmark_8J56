import tarfile

import os


def compress(dir_path):
    compressed_file = "%s/%s.tar.gz" % (os.path.dirname(dir_path),
                                        os.path.basename(dir_path))
    with tarfile.open(compressed_file, "w:gz") as tar:
        tar.add(dir_path, arcname=os.path.basename(dir_path))
    return compressed_file


def extract_to_dir(tar_file_path):
    extract_path = os.path.dirname(tar_file_path)
    with tarfile.open(tar_file_path) as tar:
        tar.extractall(extract_path)

    # eg: input, testfile.tar.gz; output, testfile
    extract_dir_name = os.path.splitext(
        os.path.splitext(os.path.basename(tar_file_path))[0])[0]

    return "%s/%s" % (extract_path, extract_dir_name)
