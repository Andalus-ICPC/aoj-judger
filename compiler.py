import CommandRunner
import os

from config import COMPILER_LOG_PATH
from exception import *

class Compiler:
   def compile(src_path, compile_config, output_dir):
      command = compile_config
      exe_path = os.path.join(output_dir, command["exe_name"])
      compiler_output = os.path.join(output_dir, 'compiler.out')
      command = command['compile_command']
      command = command.format(src_path=src_path, exe_path=exe_path)
      env = ["PATH=" + os.getenv("PATH")]
      command = command.split(" ")
      result = CommandRunner.run(
         exe_path=command[0],
         args=command[1::],
         log_path=COMPILER_LOG_PATH,
         env=env,
         error_path=compiler_output
      )
      if result['result'] == CommandRunner.SUCCESS:
         os.remove(compiler_output)
         return exe_path
      else:
         if os.path.exists(compiler_output):
            with open(compiler_output, encoding='utf-8') as f:
               error = f.read().strip()
               print(error)
               os.remove(compiler_output)
               if error:
                  raise CompileError(error)


