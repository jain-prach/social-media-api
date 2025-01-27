import os
import glob

for f in glob.glob(f"{os.getcwd()}/**/*.pyc", recursive=True):
    os.remove(f)