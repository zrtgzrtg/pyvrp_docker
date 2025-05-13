
import json

def setResDict(new_resDict):
    with open("debug.log", "w")as log_file:
        log_file.write("REACHED setResDict")
    with open("IPC/resDict.json", "w") as resDict_file:
        json.dump(new_resDict, resDict_file)
    with open("debug.log", "a") as log_file2:
        log_file2.write("END of json.dump and setResDict")