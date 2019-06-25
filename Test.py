import subprocess

args = ["E:\programers_files\Projects\IncomeBot\\venv\Scripts\python.exe", "config.py"]
process = subprocess.Popen(args, stdout=subprocess.PIPE)

data = process.communicate()
for line in data:
    print(line)






