import subprocess

ib_main = subprocess.Popen(["python", "ib_main.py"]) 
dash_main = subprocess.Popen(["python", "dash_main.py"])

ib_main.wait()
dash_main.wait()