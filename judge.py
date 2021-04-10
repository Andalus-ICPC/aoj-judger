import CommandRunner
import os
import uuid
import shutil
import json
from multiprocessing import Pool
import hashlib
import psutil

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
	def judge(src_code, language, testcase_id, max_cpu_time=None, max_real_time=None, max_output_size=None, max_memory=CommandRunner.UNLIMITED ):
		# first step compile source code and get the returned executable path
		submission_id = uuid.uuid4().hex
		test_case_dir = os.path.join(TEST_CASE_DIR, testcase_id)
		
		with WorkingEnv(WORKING_SPACE, submission_id) as submission_dir:
			compile_config = language_config[language]['compile']
			run_config = language_config[language]['run']['run_command']
			src_path = os.path.join(submission_dir, compile_config['src_name'])
			# write source code into file
			with open(src_path, "w", encoding="utf-8") as f:
				f.write(src_code)
			exe_path = Compiler.compile(src_path=src_path, compile_config=compile_config, output_dir=submission_dir)

			judger = Judger(exe_path=exe_path, run_config=run_config, test_case_dir=test_case_dir, submission_dir=submission_dir,
									max_cpu_time=max_cpu_time, max_output_size=max_output_size, max_real_time=max_real_time, max_memory=max_memory
			)
			return judger.run()


def run_testcase(instance, testcase):
	return instance._judge(testcase)


class Judger:
	def __init__(self, exe_path, run_config, test_case_dir, submission_dir,
					 max_cpu_time, max_output_size, max_real_time, max_memory):
		self._exe_path = exe_path
		self._run_config = run_config
		self._testcase_dir = test_case_dir
		self._submission_dir = submission_dir
		self._max_cpu_time = max_cpu_time
		self._max_output_size = max_output_size
		self._max_real_time = max_real_time
		self._max_memory = max_memory
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
		command = command.format(exe_path=self._exe_path).split(" ")
		env = ["PATH=" + os.getenv("PATH")]

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
				)
		user_sha256 = self._get_sha256(user_code_output)
		if run_result['result'] == CommandRunner.SUCCESS:
			testcase_sha256 = testcase['data']['sha256_output']
			testcase_result_accepted = user_sha256 == testcase_sha256
			if not testcase_result_accepted:
				run_result['result'] = CommandRunner.WRONG_ANSWER
		run_result['testcase'] = testcase['id']
		return run_result




	def run(self):
		result_objs = []
		results = []
		with Pool(psutil.cpu_count()) as pool:
			for id, testcase in self._testcase_info['testcases'].items():
				if 'sha256_output' not in testcase:
					self._set_sha256_output()
				result_objs.append(pool.apply_async(run_testcase,(self, {"id": id, "data": testcase})))
			pool.close()
			pool.join()
			results = [result.get() for result in result_objs]
		return results