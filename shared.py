
import os
import json

def setResDict(new_resDict):
    with open("debug.log", "w")as log_file:
        log_file.write("REACHED setResDict")
    with open("IPC/resDict.json", "w") as resDict_file:
        json.dump(new_resDict, resDict_file)
    with open("debug.log", "a") as log_file2:
        log_file2.write("END of json.dump and setResDict")
def setResDictThread(new_resDict,threadID):
    basedir = "resDictThreads"
    locationDir = f"solver_{threadID}_output"
    dirpath = os.path.join(basedir,locationDir,f"solver_{threadID}_resDict.json")
    with open(dirpath, "w") as output_f:
        json.dump(new_resDict,output_f)