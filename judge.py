import CommandRunner
import os
import uuid
import shutil
import json
from multiprocessing import Pool
import hashlib
import psutil
import math
from config import language_config, TEST_CASE_DIR, WORKING_SPACE, DEBUG, JUDGER_LOG_PATH
from exception import JudgeRuntimeError
from compiler import Compiler
from helpers import logger



class WorkingEnv(object):
	def __init__(self, working_space, submission_id):
		self.work_dir = os.path.join(working_space, submission_id)
	
	def __enter__(self):
		try:
			os.makedirs(self.work_dir)
		except Exception as e:
			logger.exception(e)
			raise JudgeRuntimeError("Failed to create runtime directory work_space")
		return self.work_dir


	def __exit__(self, exc_type, exc_val, exc_tb):
		if not DEBUG: # if not on DEBUG mode clean every code
			try:
				shutil.rmtree(self.work_dir)
			except Exception as e:
				print('Failed: cleaning runtime directory ' + e)
				logger.exception(e)
				raise JudgeRuntimeError("Failed to clean runtime directory work_space")




class JudgeServer:
	def judge(src_code, language, submission_id, testcase_id, absolute_error, max_cpu_time=None, max_real_time=None, max_output_size=None, max_memory=CommandRunner.UNLIMITED ):
		# first step compile source code and get the returned executable path
		# submission_id = uuid.uuid4().hex
		test_case_dir = os.path.join(TEST_CASE_DIR, testcase_id)
		
		with WorkingEnv(WORKING_SPACE, submission_id) as submission_dir:
			compile_config = language_config[language]['compile']
			run_config = language_config[language]['run']['run_command']
			src_path = os.path.join(submission_dir, compile_config['src_name'])
			if language == "Java":
				class_name = java_class_name_find(src_code)
			else:
				class_name = None
			# write source code into file
			with open(src_path, "w", encoding="utf-8") as f:
				f.write(src_code)
			exe_path = Compiler.compile(src_path=src_path, compile_config=compile_config, output_dir=submission_dir)

			judger = Judger(exe_path=exe_path, run_config=run_config, class_name=class_name, test_case_dir=test_case_dir, submission_dir=submission_dir,
									max_cpu_time=max_cpu_time, max_output_size=max_output_size, max_real_time=max_real_time, max_memory=max_memory,
									absolute_error=absolute_error
			)
			return judger.run()


def run_testcase(instance, testcase):
	return instance._judge(testcase)


def java_class_name_find(source):

	ind  = source.find('public static void main')
	if ind == -1:
		return None

	text = source[:ind]
	ind  = text.rfind('class')
	if ind == -1:
		return None

	text = text[ind + len('class'):]

	ind1  = text.find('{')
	if ind == -1:
		return None

	class_name = text[:ind1]
	class_name = class_name.replace(' ', '')
	class_name = class_name.replace('\n', '')
	if not class_name:
		return None
	return class_name


class Judger:
	def __init__(self, exe_path, run_config, class_name, test_case_dir, submission_dir,
					 max_cpu_time, max_output_size, max_real_time, max_memory, absolute_error):
		self._exe_path = exe_path
		self._run_config = run_config
		self._class_name = class_name
		self._testcase_dir = test_case_dir
		self._submission_dir = submission_dir
		self._max_cpu_time = max_cpu_time
		self._max_output_size = max_output_size
		self._max_real_time = max_real_time
		self._max_memory = max_memory
		self._absolute_error = absolute_error
		self._testcase_info = self._get_testcase_info()

	def _get_testcase_info(self):
		try:
			with open(os.path.join(self._testcase_dir, "info")) as f:
					return json.load(f)
		except IOError:
			raise JudgeRuntimeError("Test case not found")
		except ValueError:
			raise JudgeRuntimeError("Bad test case config")
	
	# make sure the testcase info has each sha256  hash for optimization and remove this func
	def _set_sha256_output(self):
		new_testcase_info = self._testcase_info
		for id, testcase in self._testcase_info['testcases'].items():
			with open(os.path.join(self._testcase_dir, testcase['output_name']), 'rb') as f:
				content = f.read()
				# while True:
				# 	data = f.read(BUF_SIZE)
				# 	if not data:
				# 		break
				# 	sha256.update(data)
			
			hash_result = hashlib.sha256(content.rstrip()).hexdigest()
			new_testcase_info['testcases'][id]['sha256_output'] = hash_result
			
		with open(os.path.join(self._testcase_dir, 'info'), 'w') as f:
			json.dump(new_testcase_info, f)
				
	def _get_sha256(self, user_code_output):
		with open(user_code_output, 'rb') as f:
			content = f.read()
		return hashlib.sha256(content.rstrip()).hexdigest()


		

	def _judge(self, testcase):
		
		input_testcase = os.path.join(self._testcase_dir, testcase["data"]['input_name'])
		output_testcase = testcase["data"]['output_name']
		user_code_output = os.path.join(self._submission_dir, testcase["id"] + '.out')
		command = self._run_config
		command = command.format(exe_path=self._exe_path, class_name=self._class_name).split(" ")
		env = ["PATH=" + os.getenv("PATH")]
		
		_seccomp_rule = "general" #  general, c_cpp, c_cpp_file_io
		if command[0] == "/usr/bin/java":
			_seccomp_rule = None
		run_result = CommandRunner.run(
					max_real_time=self._max_real_time,
					max_cpu_time=self._max_cpu_time,
					max_output_size=self._max_output_size,
					max_memory=self._max_memory,
					exe_path=command[0],
					args=command[1::],
					log_path=JUDGER_LOG_PATH,
					env=env,
					input_path=input_testcase,
					output_path=user_code_output,
					error_path=user_code_output,
					seccomp_rule=_seccomp_rule	
				)
		# print(run_result)
		user_sha256 = self._get_sha256(user_code_output)
		if run_result['result'] == CommandRunner.SUCCESS:
			if self._absolute_error <= 1e-20:
				testcase_sha256 = testcase['data']['sha256_output']
				testcase_result_accepted = user_sha256 == testcase_sha256
				if not testcase_result_accepted:
					run_result['result'] = CommandRunner.WRONG_ANSWER
			else:
				testcase_output_path = os.path.join(self._testcase_dir, testcase['data']["output_name"])
				run_result['result'] = self.check_absolute_error(testcase_output_path, user_code_output, self._absolute_error)
		run_result['testcase'] = testcase['id']
		return run_result



	def check_absolute_error(self, correct_answer_file, user_answer_file, error):
		try:
			correct_answer = open(correct_answer_file, 'r')
			user_answer = open(user_answer_file, 'r')
		except FileNotFoundError:
			return CommandRunner.WRONG_ANSWER

		correct_answer_list = []
		user_answer_list = []
		for j in correct_answer:
			x = j.rstrip()
			correct_answer_list.append(x)
		for j in user_answer:
			x = j.rstrip()
			user_answer_list.append(x)
		while correct_answer_list:
			if correct_answer_list[-1]:
				break
			correct_answer_list.pop()

		while user_answer_list:
			if user_answer_list[-1]:
				break
			user_answer_list.pop()
		correct_answer.close()
		user_answer.close()

		if correct_answer_list and not user_answer_list:
			return CommandRunner.NO_OUTPUT
		if len(correct_answer_list) != len(user_answer_list):
			return CommandRunner.WRONG_ANSWER
		for testcase_line, user_line in zip(correct_answer_list, user_answer_list):
			correct_line = testcase_line.split()
			user_answer_line = user_line.split()
			if len(correct_line) != len(user_answer_line):
				return CommandRunner.WRONG_ANSWER
			for each_correct_answer, each_user_answer in zip(correct_line, user_answer_line):
				if each_correct_answer == each_user_answer:
					continue
				try:
					each_correct_answer = float(each_correct_answer)
					each_user_answer = float(each_user_answer)
				except ValueError:
					return CommandRunner.WRONG_ANSWER
				if math.fabs(each_correct_answer - each_user_answer) > error:
					return CommandRunner.WRONG_ANSWER

		return CommandRunner.SUCCESS



	def run(self):
		result_objs = []
		results = []
		result_and_path = {"results": None, "user_output_path": None}
		with Pool(psutil.cpu_count()) as pool:
			for id, testcase in self._testcase_info['testcases'].items():
				if 'sha256_output' not in testcase:
					self._set_sha256_output()
				result_objs.append(pool.apply_async(run_testcase,(self, {"id": id, "data": testcase})))
			pool.close()
			pool.join()
			results = [result.get() for result in result_objs]
			# result_and_path["result"] = results
			# result_and_path["user_output_path"] = self._submission_path
		return results