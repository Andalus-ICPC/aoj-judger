import os

import CommandRunner
import pwd
import grp

# default_env = ["LANG=en_US.UTF-8", "LANGUAGE=en_US:en", "LC_ALL=en_US.UTF-8"]

# DEBUG = os.environ.get('DEBUG') == "1"
DEBUG = 1

BASE_DIR = 'AOJ'

LOG_BASE = os.path.join(BASE_DIR, 'log')
WORKING_SPACE = os.path.join(BASE_DIR, 'working_space')
TEST_CASE_DIR = os.path.join(BASE_DIR, 'test_cases')

if not os.path.exists(LOG_BASE):
   os.makedirs(LOG_BASE)
if not os.path.exists(WORKING_SPACE):
   os.makedirs(WORKING_SPACE)
if not os.path.exists(TEST_CASE_DIR):
   os.makedirs(TEST_CASE_DIR)

COMPILER_LOG_PATH = os.path.join(LOG_BASE, 'compiler.log')
JUDGER_LOG_PATH = os.path.join(LOG_BASE, 'judger.log')
SERVER_LOG_PATH = os.path.join(LOG_BASE, 'server.log')




language_config = {
   'C++': {
      'compile': {
         "src_name": "solution.cpp",
         "exe_name": "solution",
         "compile_command": "/usr/bin/g++ -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c++14 {src_path} -lm -o {exe_path}",
      },
      'run': {
         'run_command': "{exe_path}"
      }
   },
   'C': {
      'compile': {
         "src_name": "solution.c",
         "exe_name": "solution",
         "compile_command": "/usr/bin/gcc -DONLINE_JUDGE -O2 -w -fmax-errors=3 -std=c11 {src_path} -lm -o {exe_path}",
      },
      'run': {
         'run_command': "{exe_path}"
      }
   },
   'Python3': {
      'compile': {
         'src_name': 'solution.py',
         'exe_name': '__pycache__/solution.cpython-36.pyc',
         'compile_command': "/usr/bin/python3 -m py_compile {src_path}"
      },
      'run': {
         'run_command': '/usr/bin/python3 {exe_path}',
      }
   },
   'Python2': {
      'compile': {
         'src_name': 'solution.py',
         'exe_name': 'solution.pyc',
         'compile_command': "/usr/bin/python2 -m py_compile {src_path}"
      },
      'run': {
         'run_command': '/usr/bin/python2 {exe_path}',
      }
   },
   'Java': {
      'compile': {
         'src_name': 'solution.java',
         'exe_name': 'solution',
         "compile_command": "/usr/bin/javac {src_path} -d {exe_path} -encoding UTF8"
      },
      'run' : {
         "run_command": "/usr/bin/java -cp {exe_path} {class_name} -Djava.security.manager -Dfile.encoding=UTF-8 -Djava.security.policy==/etc/java_policy -Djava.awt.headless=true"

      }
   }

}


# java version 11.0.11
# gcc versoin 7.5.0
# g++ version 7.5.0
# python2 2.7.15
# python3 3.6.9