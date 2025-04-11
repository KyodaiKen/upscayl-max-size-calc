import argparse
import datetime
from directory_utils import find_files
from termcolor import colored
import subprocess
from time_utils import estimate_time_left

parser = argparse.ArgumentParser(
    prog="autoscaledir",
    description="Uses autoscale to resize a directory of images to the maximum size Upscayl supports."
)
parser.add_argument("path", help="Input Path")
parser.add_argument("--upscayl-path", help="Upscayl path", default="python \"d:\\data\\GIT\\upscayl-max-size-calc\\autoscale.py\"")
parser.add_argument("-p", "--pattern", help="File pattern", default="*.jpg;*.jpeg;*.png;*.webp")
parser.add_argument("-R", "--recursive", action="store_true", help="Recusrive file search")
parser.add_argument("-b", "--batch", action="store_true", help="Create a batch script only")
parser.add_argument("-s", "--simulation", action="store_true", help="Simulate only")
parser.add_argument("-U", "--upscayl-parameters", help="Upscayl parameter list")

args = parser.parse_args()
parsed_args_dict = vars(args)

# Print args
if args.batch == False:
    print(colored("Autoscale for upscayl! ==== ", 'light_cyan') + colored(f"UPSCAYL A DIRECTORY", 'light_yellow') + colored("=================", 'light_cyan'))
    print("=> Parameters used:")
    for key, value in parsed_args_dict.items():
        key = key.upper()
        print(f"{key:>10}: {value}")
    print("")

    print("=> Building file list")
file_list = find_files(args.path, args.pattern, args.recursive)
num_files = len(file_list)

if args.upscayl_parameters != None:
    up_parms = args.upscayl_parameters + " "
else:
    up_parms = ""

f=0
if args.batch:
    print("@ECHO OFF")
    for file in file_list:
        f+=1
        percent = (f-1)/num_files
        print("ECHO " + f"=> Processing file {f} / {num_files}, {percent:.2%} done.")
        print(f"{args.upscayl_path} {up_parms}\"{file}\"")
    print("ECHO " + f"=> Processed file {f} / {num_files}, 100% done.")
    exit(0)

print(f"=> Found {num_files} files.")

start_datetime = datetime.datetime.now()
print(colored(f"=> START: {start_datetime}"), 'light_yellow')

f=0
for file in file_list:
    f+=1
    percent = (f-1)/num_files
    current_time = datetime.datetime.now()
    ETL = estimate_time_left(start_datetime, f-1, num_files)
    print(colored(f"=> Processing file {f} / {num_files}, {percent:.2%} done.", 'light_cyan') + " " + colored(f"Estimated time left: {ETL}",'light_magenta'))
    command = f"{args.upscayl_path} {up_parms}\"{file}\""
    if args.simulation:
        print(command)
    else:
        ret_code = subprocess.call(command, shell=True)
        if ret_code > 0:
            print(colored(f"The process returned the error code {ret_code}", 'light_red'))

print(colored(f"=> Processed file {f} / {num_files}, 100.00% done.", 'light_cyan'))
datetime_end = datetime.datetime.now()
print(colored(f"JOB END . : {datetime_end}", 'light_green'))
print(colored(f"TIME TAKEN: {datetime_end - start_datetime}", 'light_green'))
