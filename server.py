from flask import Flask, request
import os, shutil

from helpers import get_server_info, logger
from judge import JudgeServer
from submission import submission_detail
from config import DEBUG, TEST_CASE_DIR, WORKING_SPACE
from exception import *
from zipfile import ZipFile

app = Flask(__name__)
app.debug = DEBUG


@app.route('/judge')
def judge():
	_token = request.headers.get("X-AOJ-Server-Token")
	try:
		data = request.json
		result_and_path = JudgeServer.judge(**data)
		result = result_and_path['result']
		user_output_path = result_and_path['user_output_path']
		return {"success": True, "data": result, "user_output_path": user_output_path, "error": None}
	except (CompileError, TokenVerificationFailed, JudgeRuntimeError) as e:
		logger.exception(e)
		# print(7777777777)
		return {"success": False, "error": e.__class__.__name__, "message": e.message, "user_output_path": None}
	except Exception as e:
		# print(888888888888)
		return {"success": False, "error": e.__class__.__name__, "message": str(e), "user_output_path": None}
		

@app.route('/info')
def info():
	return get_server_info()


@app.route("/upload_testcase", methods=["POST"])
def upload():
	if request.method == 'POST':
		f = request.files['file']
		file_path = os.path.join(TEST_CASE_DIR, request.form['testcase_id'])
		zip_file_path = os.path.join(TEST_CASE_DIR, 'temp_zip_folder')
		if os.path.exists(file_path):
			# return {"error": "Duplicate testcase name", "message": "The testcase name already exists for problem %s" % request.form['testcase_id']}
			shutil.rmtree(file_path)
		f.save(zip_file_path)

		try:
			with ZipFile(zip_file_path, 'r') as zipObj:
				zipObj.extractall(file_path)
		except Exception as e:
			if os.path.exists(zip_file_path):
				os.remove(zip_file_path)
			return {"error": e.__class__.__name__, "message": str(e)}
		if os.path.exists(zip_file_path):
			os.remove(zip_file_path)
		return {"data": "upload successfully"}


@app.route("/remove_testcase", methods=["POST"])
def remove_testcase():
	if request.method == 'POST':
		file_path = os.path.join(TEST_CASE_DIR, request.form['testcase_id'])
		if os.path.exists(file_path):
			shutil.rmtree(file_path)
		return {"data": "remove successfully"}


if DEBUG:
    logger.info("DEBUG=ON")



@app.route("/submission_output")

def submission_output():
	_token = request.headers.get("X-AOJ-Server-Token")
	data = request.json
	file_path = os.path.join(WORKING_SPACE, data['sudmission_dir'])
	testcase_path = os.path.join(TEST_CASE_DIR, data['testcase_id'])
	sample_output = submission_detail(file_path, testcase_path)
	return sample_output


