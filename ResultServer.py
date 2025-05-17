
import zipfile
import json
from create_data_for_api import DataCreator
import os




class Result_Server():
    def __init__(self):
        pass

    def combineJSONS(self):
        parent_dir = "resDictThreads"
        combined = []
        for dir in os.listdir(parent_dir):
            subdir_path = os.path.join(parent_dir,dir)
            if os.path.isdir(subdir_path):
                for outputresDict in os.listdir(subdir_path):
                    if outputresDict.endswith(".json"):
                        filepath = os.path.join(subdir_path,outputresDict)
                        with open(filepath,"r") as f:
                            combined.append(json.load(f))
        filepath_FINAL = "IPC/resDict.json"
        with open(filepath_FINAL, "w") as output_file:
            json.dump(combined, output_file)
        return filepath_FINAL
    
    def giveZipresDict(self):
        filepath = "IPC/combined_resDict.zip"
        filepathJson = self.combineJSONS()
        with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filepathJson)
    