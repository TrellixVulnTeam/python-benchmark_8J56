import benchmark.utils.process_util as process_util


if __name__ == '__main__':
    result_tars = process_util.get_all_tar_files()
    for result_tar in result_tars:
        process_util.process_one_result(result_tar)
