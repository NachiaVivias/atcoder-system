from Tools.config_cpp import *


import pickle
import os
import requests
import getpass
from bs4 import BeautifulSoup as bs4


def ensured_directory(name, do_clear = False):
    os.makedirs(name, exist_ok=True)
    if do_clear:
        import shutil
        shutil.rmtree(name)
        os.makedirs(name, exist_ok=True)
    return name

def save_session(session : requests.Session):
    if not os.path.isdir(COOKIE_DIR):
        os.mkdir(COOKIE_DIR)
    with open(COOKIE_PATH, 'wb') as f:
        pickle.dump(session.cookies, f)

def login_to_atcoder_with_user_input():
    
    print("AtCoder Username : ", end="", flush=True)
    atcoder_username = input()
    atcoder_password = getpass.getpass(prompt='AtCoder Password : ', stream=None)

    session = requests.session()
    html = session.get("https://atcoder.jp/login")
    soup_pre = bs4(html.content, "html.parser")
    
    csrf_token_val = soup_pre.find(attrs={"name": "csrf_token"}).attrs["value"]

    # Atcoder Login
    payload = {
    "username": atcoder_username,
    "password": atcoder_password,
    "csrf_token": csrf_token_val,
    "submit": "ログイン"
    }
    login_response = session.post('https://atcoder.jp/login', data=payload)
    return session

def get_login_to_atcoder():

    session = None

    if not os.path.isdir(COOKIE_DIR):
        os.mkdir(COOKIE_DIR)
    if not os.path.isfile(COOKIE_PATH):
        session = login_to_atcoder_with_user_input()
        save_session(session)
        return session

    with open(COOKIE_PATH, 'rb') as f:
        c = pickle.load(f)
        session = requests.session()
        session.cookies.update(c)

    return session

def read_all_from_a_file(fname):
    return open(fname).read()
def write_all_to_a_file(s, fname):
    print(s, file=open(fname,"w"), end='')

def load_testcase_mapping():
    if not os.path.isdir(TSETCASE_DIR):
        os.mkdir(TSETCASE_DIR)
    if not os.path.isfile(TASK_MAPPING_FNAME):
        print("", end="", file=open(TASK_MAPPING_FNAME, "w"))
    lines = open(TASK_MAPPING_FNAME, "r").read().splitlines()
    res1 = {}
    for s in lines:
        q = list(s.split(' '))
        if len(q) != 2:
            continue
        res1[q[0]] = q[1]
    return res1

def save_testcase_mapping(mapping1):
    if not os.path.isdir(TSETCASE_DIR):
        os.mkdir(TSETCASE_DIR)
    with open(TASK_MAPPING_FNAME, "w") as file:
        for u in mapping1:
            print(u, mapping1[u], file=file)

def get_next_mapped_name():
    import time
    t = int(time.time() * 1000)
    k = 0
    def get_mapped_name_with_k():
        return str(t) + '_' + str(k)
    while os.path.isdir(TSETCASE_DIR + '/' + get_mapped_name_with_k()):
        k += 1
    return get_mapped_name_with_k()

def extract_sample_test_data(html_content, case_dir):

    def extract_examples(soup):
        examples_input = []
        examples_output = []

        part_example = soup.select(".part")

        inputs = [elem for elem in part_example if 'Sample Input' in elem.find('h3').text]

        for elem in inputs:
            s = elem.find('pre').get_text()
            s.replace('\n\n', '\n')
            examples_input.append(s)

        outputs = [elem for elem in part_example if 'Sample Output' in elem.find('h3').text]

        for elem in outputs:
            examples_output.append(elem.find('pre').get_text())

        return list(zip(examples_input, examples_output))

    soup = bs4(html_content, 'html.parser')
    examples = extract_examples(soup)
    
    id = 0
    for data_in, data_out in examples:
        case_in_fname = case_dir + f'/sample_{id}.in'
        case_out_fname = case_dir + f'/sample_{id}.out'
        write_all_to_a_file(data_in, case_in_fname)
        write_all_to_a_file(data_out, case_out_fname)
        id += 1

def load_testcase_from_url(url):
    session = get_login_to_atcoder()
    
    url_to_dir = load_testcase_mapping()
    dir = None
    if dir is None and url in url_to_dir:
        dir_tmp = url_to_dir[url]
        if os.path.isdir(TSETCASE_DIR + '/' + dir_tmp):
            dir = dir_tmp
    if dir is None:
        mapped_name = get_next_mapped_name()
        dir_tmp = ensured_directory(TSETCASE_DIR + '/' + mapped_name)
        dir = mapped_name
        url_to_dir[url] = mapped_name
    
        html = session.get(url)
        extract_sample_test_data(html.content, TSETCASE_DIR + '/' + dir)

        save_testcase_mapping(url_to_dir)

    return dir


def run_contestant_exe(contestant_exe_fname, in_file_name, workspace, time_limit = TIME_LIMIT):
    import subprocess

    EXECUTE_COMMAND = [contestant_exe_fname]
    CUT_OUTOUT_COMMAND = ["Tools/cut_output.exe"]
    
    out_txt_fname = workspace + "/out.txt"
    err_txt_fname = workspace + "/err.txt"

    tle_flag = False
    ole_flag_stderr = False
    ole_flag_stdout = False

    with open(err_txt_fname, "wb") as err_txt_file :
        with open(out_txt_fname, "wb") as out_txt_file :
            with open(in_file_name,"rb") as in_txt_file :
                exec_process = subprocess.Popen(EXECUTE_COMMAND, stdin=in_txt_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                cutout_process = subprocess.Popen(CUT_OUTOUT_COMMAND, stdin=exec_process.stdout, stdout=out_txt_file, stderr=subprocess.PIPE)
                cuterr_process = subprocess.Popen(CUT_OUTOUT_COMMAND, stdin=exec_process.stderr, stdout=err_txt_file, stderr=subprocess.PIPE)
                try:
                    exec_process.wait(time_limit)
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
        ole_flag_stdout = cod >= 2
    if cuterr_process.returncode == 0 :
        cod = int(cuterr_process.stderr.read(1).decode("utf-8"))
        ole_flag_stderr = cod >= 2
    
    cutout_process.stderr.close()
    cuterr_process.stderr.close()

    if ole_flag_stdout :
        return 3
    if ole_flag_stderr :
        return 3
    if tle_flag :
        return 2
    if exec_process.returncode != 0 :
        return 1
    return 0



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

CUT_OUTOUT_COMMAND = ["Tools/cut_output"]
BUNDLE_COMMAND = ["oj-bundle", SOURCE_PATH]
ERASE_LINE_COMMAND = ["Tools/erase_line_line"]

JUDGE_SPACE_PATH = 'Tools/judge_space'

def sample_test(url):
    mapped_name = load_testcase_from_url(url)

    case_dir = TSETCASE_DIR + '/' + mapped_name
    
    case_fnames = os.listdir(case_dir)
    
    import subprocess
    import pyperclip

    bundled_file = open("Tools/Bundled.cpp","wb")
    bundle_process = subprocess.Popen(BUNDLE_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    erase_line_process = subprocess.Popen(ERASE_LINE_COMMAND, stdin=bundle_process.stdout, stdout=bundled_file, stderr=subprocess.DEVNULL)

    with open(COMPILE_ERR_FILE, "wb") as ce_file :
        compile_res = subprocess.run(COMPILE_COMMAND, stdout=subprocess.PIPE, stderr=ce_file)
    if compile_res.returncode != 0 :
        print("\033[33mCompilation Error\033[0m", flush=True)
        return
    else :
        print("\033[34mCompilation Finished\033[0m", flush=True)
    
    ensured_directory(JUDGE_SPACE_PATH)
    
    import threading
    threads : list[(str, threading.Thread)] = []

    case_names = []
    
    for case_fname in case_fnames:
        if not case_fname.endswith('.in'):
            continue
        case_names.append(case_fname[:-3])
    case_names.sort()

    def judge_for_a_case(case_name):
        in_fpath = case_dir + '/' + case_name + '.in'
        case_workspace_dir = ensured_directory(JUDGE_SPACE_PATH + '/' + case_name)
        verdict_id = run_contestant_exe(EXEFILENAME, in_fpath, case_workspace_dir, TIME_LIMIT)
        if verdict_id == 3 :
            print(f"{case_name} : \033[33mOutput Limit Exceeded\033[0m", flush=True)
        if verdict_id == 2 :
            print(f"{case_name} : \033[33mTime Limit Exceeded\033[0m", flush=True)
        if verdict_id == 1 :
            print(f"{case_name} : \033[33mRuntime Error\033[0m", flush=True)
        if verdict_id == 0 :
            print(f"{case_name} : \033[34mOK\033[0m")

    for case_name in case_names:
        th = threading.Thread(target=judge_for_a_case, args=[case_name], daemon=True)
        th.start()
        threads.append((case_name, th))
    
    with open(STDOUT_FILE, 'w') as out_txt:
        with open(STDERR_FILE, 'w') as err_txt:

            for case_name, th in threads:
                th.join()
                out_txt_fname = JUDGE_SPACE_PATH + '/' + case_name + "/out.txt"
                err_txt_fname = JUDGE_SPACE_PATH + '/' + case_name + "/err.txt"
                out_data = read_all_from_a_file(out_txt_fname)
                print(out_data, file=out_txt, end='\n')
                err_data = read_all_from_a_file(err_txt_fname)
                print(err_data, file=err_txt, end='\n')
    
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



def compile_judge_resource():
    import os
    os.system("g++ Tools/cut_output.cpp -o Tools/cut_output.exe -O2")
    os.system("g++ Tools/erase_line_line.cpp -o Tools/erase_line_line.exe -O2")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="target url to scrape")
    args = parser.parse_args()

    url = args.url
    sample_test(url)

def execute_with_argument(command):
    if len(command) < 1:
        return
    elif command[0] == "compile":
        compile_judge_resource()
    elif command[0] == "clean":
        ensured_directory(TSETCASE_DIR, True)
        ensured_directory(JUDGE_SPACE_PATH, True)
    else:
        sample_test(command[0])
