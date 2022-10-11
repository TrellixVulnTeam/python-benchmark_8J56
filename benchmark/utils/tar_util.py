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
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, extract_path)

    # eg: input, testfile.tar.gz; output, testfile
    extract_dir_name = os.path.splitext(
        os.path.splitext(os.path.basename(tar_file_path))[0])[0]

    return "%s/%s" % (extract_path, extract_dir_name)
