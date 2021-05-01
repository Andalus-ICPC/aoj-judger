import os, shutil
from config import DEBUG, TEST_CASE_DIR, WORKING_SPACE
from exception import *
import json


def testcase_info(testcase_dir):
    try:
        with open(os.path.join(testcase_dir, "info")) as f:
            info = []
            content = json.load(f)
            # print(content)
            for test in content["testcases"]:
                info.append(test)
            return info
    except IOError:
        raise JudgeRuntimeError("Test case not found")
    except ValueError:
        raise JudgeRuntimeError("Bad test case config")



def read_from_file(path):
    try:
        max_byte = 50
        files = open(path, mode='r')
        try:
            # file_list = files.readlines(max_byte)
            N = 100
            file_list = [line for line in [files.readline()
                                        for _ in range(N)] if len(line)]

        except UnicodeDecodeError:
            file_list = []
        submit_file = ''
        for i in file_list:
            submit_file += i
        files.seek(0, os.SEEK_END)
        file_size = files.tell()
        files.close()
        if file_size > max_byte:
            submit_file += "\n..."
        # print(files, file_list)
        return submit_file
    except FileNotFoundError:
        return None


def submission_detail(output_path, testcase_path):
    testcase_list = testcase_info(testcase_path)
    output_dict = {}
    for test in testcase_list:
        sample_output = read_from_file(os.path.join(output_path, test + '.out')).strip().split('\n')
        if sample_output:
            output_dict[test] = {"data": sample_output, "path": os.path.join(output_path, test + '.out')}
    # print(output_dict)
    return output_dict