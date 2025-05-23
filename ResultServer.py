
import zipfile
import json
from create_data_for_api import DataCreator
import os




class Result_Server():
    def __init__(self):
        self.parent_dir = "IPC/resDictThreads"
        self.output_json_path = "IPC/resDict.json"
        self.output_zip_path = "IPC/combined_resDict.zip"

    def combineJSONS(self):
            os.makedirs("IPC", exist_ok=True)
            with open(self.output_json_path, "w") as output_file:
                output_file.write("[\n")
                first = True

                for dir_name in os.listdir(self.parent_dir):
                    subdir_path = os.path.join(self.parent_dir, dir_name)
                    if not os.path.isdir(subdir_path):
                        continue

                    for filename in os.listdir(subdir_path):
                        if filename.endswith(".json"):
                            filepath = os.path.join(subdir_path, filename)
                            try:
                                with open(filepath, "r") as f:
                                    content = json.load(f)
                                if not first:
                                    output_file.write(",\n")
                                else:
                                    first = False
                                json.dump(content, output_file)
                            except Exception as e:
                                print(f"Error reading {filepath}: {e}")

                output_file.write("\n]\n")
            return self.output_json_path

    def giveZipresDict(self):
        filepath_json = self.combineJSONS()
        with zipfile.ZipFile(self.output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filepath_json, arcname=os.path.basename(filepath_json))
        return self.output_zip_path
    #def combineJSONS(self):
    #    parent_dir = "resDictThreads"
    #    combined = []
    #    for dir in os.listdir(parent_dir):
    #        subdir_path = os.path.join(parent_dir,dir)
    #        if os.path.isdir(subdir_path):
    #            for outputresDict in os.listdir(subdir_path):
    #                if outputresDict.endswith(".json"):
    #                    filepath = os.path.join(subdir_path,outputresDict)
    #                    with open(filepath,"r") as f:
    #                        combined.append(json.load(f))
    #    filepath_FINAL = "IPC/resDict.json"
    #    with open(filepath_FINAL, "w") as output_file:
    #        json.dump(combined, output_file)
    #    return filepath_FINAL
    
    #def giveZipresDict(self):
    #    filepath = "IPC/combined_resDict.zip"
    #    filepathJson = self.combineJSONS()
    #    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
    #        zipf.write(filepathJson)
    