from flask import Flask, request
import os, shutil

from helpers import get_server_info, logger
from judge import JudgeServer
from config import DEBUG, TEST_CASE_DIR
from exception import *
from zipfile import ZipFile

app = Flask(__name__)
app.debug = DEBUG


@app.route('/judge')
def judge():
	_token = request.headers.get("X-AOJ-Server-Token")
	try:
		data = request.json
		result = JudgeServer.judge(**data)
		return {"success": True, "data": result, "error": None}
	except (CompileError, TokenVerificationFailed, JudgeRuntimeError) as e:
		logger.exception(e)
		return {"success": False, "error": e.__class__.__name__, "message": e.message}
	except Exception as e:
		return {"error": e.__class__.__name__, "message": str(e)}
		

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
		return {"data": "upload successfull"}



if DEBUG:
    logger.info("DEBUG=ON")
