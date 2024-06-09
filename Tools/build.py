from config_cpp import *

COMPILE_COMMAND = [
    "g++", SOURCE_PATH, "-m64", "-std=gnu++17", "-O2",
    "-o", EXEFILENAME, "-Wall",
    "-Wl,-stack,104857600", "-static"
]
for libpath in LIBRARY_PATH:
    COMPILE_COMMAND.append("-I")
    COMPILE_COMMAND.append(libpath)
for specialdef in SPECIAL_DEFINE:
    COMPILE_COMMAND.append("-D")
    COMPILE_COMMAND.append(specialdef)

EXECUTE_COMMAND = [EXEFILENAME]
CUT_OUTOUT_COMMAND = ["Tools/cut_output"]
BUNDLE_COMMAND = ["oj-bundle", SOURCE_PATH]
ERASE_LINE_COMMAND = ["Tools/erase_line_line"]

import subprocess
import pyperclip

bundled_file = open("Tools/Bundled.cpp","wb")
bundle_process = subprocess.Popen(BUNDLE_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
erase_line_process = subprocess.Popen(ERASE_LINE_COMMAND, stdin=bundle_process.stdout, stdout=bundled_file, stderr=subprocess.DEVNULL)

with open(COMPILE_ERR_FILE, "wb") as ce_file :
    compile_res = subprocess.run(COMPILE_COMMAND, stdout=subprocess.PIPE, stderr=ce_file)
if compile_res.returncode != 0 :
    print("\033[33mCompilation Error\033[0m", flush=True)
    exit()
else :
    print("\033[34mCompilation Finished\033[0m", flush=True)

tle_flag = False
cutoff_flag_stdout = False
ole_flag_stdout = False
cutoff_flag_stderr = False
ole_flag_stderr = False
limit_error = False

def run_contestant():
    global tle_flag, cutoff_flag_stdout, ole_flag_stdout, cutoff_flag_stderr, ole_flag_stderr, limit_error
    with open(STDERR_FILE, "wb") as err_txt_file :
        with open(STDOUT_FILE, "wb") as out_txt_file :
            with open(STDIN_FILE,"rb") as in_txt_file :
                exec_process = subprocess.Popen(EXECUTE_COMMAND, stdin=in_txt_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cutout_process = subprocess.Popen(CUT_OUTOUT_COMMAND, stdin=exec_process.stdout, stdout=out_txt_file, stderr=subprocess.PIPE)
                cuterr_process = subprocess.Popen(CUT_OUTOUT_COMMAND, stdin=exec_process.stderr, stdout=err_txt_file, stderr=subprocess.PIPE)
                try:
                    exec_process.wait(TIME_LIMIT)
                except subprocess.TimeoutExpired:
                    tle_flag = True
                    exec_process.terminate()
                    exec_process.wait()
                cutout_process.wait(1)
                cuterr_process.wait(1)
                cutout_process.terminate()
                cuterr_process.terminate()
                cutout_process.wait()
                cuterr_process.wait()
    if cutout_process.returncode == 0 :
        cod = int(cutout_process.stderr.read(1).decode("utf-8"))
        cutoff_flag_stdout = cod >= 1
        ole_flag_stdout = cod >= 2
    if cuterr_process.returncode == 0 :
        cod = int(cuterr_process.stderr.read(1).decode("utf-8"))
        cutoff_flag_stderr = cod >= 1
        ole_flag_stderr = cod >= 2
    
    cutout_process.stderr.close()
    cuterr_process.stderr.close()
    return exec_process.returncode

return_code = run_contestant()

if cutoff_flag_stdout :
    print("\033[32mOutput Is Cut Off (stdout)\033[0m", flush=True)
if cutoff_flag_stderr :
    print("\033[32mOutput Is Cut Off (stderr)\033[0m", flush=True)
if ole_flag_stdout :
    print("\033[33mOutput Limit Exceeded (stdout)\033[0m", flush=True)
    limit_error = True
if ole_flag_stderr :
    print("\033[33mOutput Limit Exceeded (stderr)\033[0m", flush=True)
    limit_error = True
if tle_flag :
    print("\033[33mTime Limit Exceeded\033[0m", flush=True)
    print("\033[32mOutput may be Cut Off (stdout)\033[0m", flush=True)
    print("\033[32mOutput may be Cut Off (stderr)\033[0m", flush=True)
    limit_error = True
if limit_error :
    exit()
if return_code != 0 :
    print("\033[33mRuntime Error\033[0m", flush=True)
    print(f"return code = {return_code}", flush=True)
    exit()
    
print("\033[34mOK\033[0m")

bundle_process.wait()
erase_line_process.wait()
bundled_file.close()

if bundle_process.returncode != 0 :
    print("\033[33mBundle Failed\033[0m", flush=True)
else :
    print("\033[34mBundle OK\033[0m", flush=True)
    with open("Tools/Bundled.cpp","rb") as bundled_file :
        bundled = bundled_file.read()
    pyperclip.copy(bundled.decode('utf-8'))
    print("\033[34mCopied to clipboard!\033[0m", flush=True)
