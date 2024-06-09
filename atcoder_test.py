from Tools.atcoder_sample_test import execute_with_argument

while True:
    command = input().split()
    if len(command) < 1:
        continue
    if command[0] == "exit":
        break
    execute_with_argument(command)
