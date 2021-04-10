import CommandRunner
import os
import psutil
import socket
import logging

from config import SERVER_LOG_PATH
from exception import TokenVerificationFailed

logger = logging.getLogger(__name__)
handler = logging.FileHandler(SERVER_LOG_PATH)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)




def get_token():
	TOKEN = os.environ.get('TOKEN')
	if not TOKEN:
		raise TokenVerificationFailed("Error no TOKEN was found!")
	else:
		return TOKEN

def get_server_info():
	version = CommandRunner.VERSION
	server_info = {
		"hostname": socket.gethostname(),
		"cpu": psutil.cpu_percent(),
		"cpu_core": psutil.cpu_count(),
		# "memory": psutil.virtual_memory().cpu_percent,
		"CommandRunner_version": version,
	}
	return server_info


# TOKEN = get_token()