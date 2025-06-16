
import copy
import rapidjson
from ResultServer import Result_Server
from data.city_matrices import city_matrices
import json
import sys
import os
from pathlib import Path
import subprocess

class BatchQueue():
    def __init__(self):
        pass
    # structure of inputsHTMLlist
    #realDM =  sys.argv[1][0]
    #Ec2DDM=  sys.argv[1][1]
    #inputs=  sys.argv[1][2]
    #numThreads=  sys.argv[1][3]
    #numEc2D=  sys.argv[1][4]
    #numRealDM=  sys.argv[1][5]
    #numIterations =  sys.argv[1][6]

    def startJob(self, inputsHTMLList):
        inputsHTMLListSTR = json.dumps(inputsHTMLList)
        with open("batchprogress.log", "w") as f:
            p = subprocess.Popen(["python3", "distmainBatch.py", inputsHTMLListSTR,],
                                  stdout=f,
                                  stderr=f
                                  )
        p.wait()
        # 10 runs of N*10



    def allVrpSetsOneCity(self,inputsHTMLList):
        listallVrpFiles = []
        for index, dir in enumerate(os.listdir("data/Vrp-Set-X/X/")):
            print(f"index:{index} and dir: {dir}")
            base, ext = os.path.splitext(dir)
            if base != "debug":
                listallVrpFiles.append(base)
        for vrpfile in listallVrpFiles:
            inputsHTMLList[2]["X_set"] = vrpfile
            # Blocks until the subprocess is done
            self.startJob(inputsHTMLList)
            os.makedirs("BatchDIR", exist_ok=True)
            saveDir = "BatchDIR"
            rs = Result_Server()
            rs.giveZipresDict()
            # Now the is IPC/combined_resDict.json
            os.rename("IPC/combined_resDict.zip",f"{os.path.join(saveDir,vrpfile)}.zip")
    def fourSpecialCase(self, TaskPath):
        inputdict = "dict_batchQueue"
        os.makedirs("dict_batchQueue/results", exist_ok=True)
        
        with open(f"{inputdict}/{TaskPath}","r") as f:
            inputList = json.load(f)
        for i, lists in enumerate(inputList):
            x = list(lists.values())
            self.startJob(x)
            saveDir = "BatchCustom"
            os.makedirs(saveDir,exist_ok=True)
            rs = Result_Server()
            rs.giveZipresDict()
            # Now the is IPC/combined_resDict.json
            os.rename("IPC/combined_resDict.zip",f"{os.path.join(saveDir,str(i))}.zip")
    def getDMpaths(self,dirpath):
        parentpath = "data/distance_matrices/"
        path = os.path.join(parentpath,dirpath)
        dmPathList = []
        
        for dirs in os.listdir(path):
            realDM = ""
            ec2dDM = ""
            specialCaseList = []
            fullpath = os.path.join(path,dirs)
            for caseDir in os.listdir(fullpath):
                casepath = os.path.join(fullpath,caseDir)
                if caseDir == "normalCase":
                    for dm in os.listdir(casepath):
                        filepath = os.path.join(casepath,dm)
                        parts = filepath.split(os.sep)
                        new_filepath = os.path.join(*parts[2:])
                        if "Real" in dm:
                            realDM = new_filepath
                        else:
                            ec2dDM = new_filepath
                elif (caseDir == "specialCases"):
                    for dm in os.listdir(casepath):
                        filepath = os.path.join(casepath,dm)
                        parts = filepath.split(os.sep)
                        new_filepath = os.path.join(*parts[2:])
                        specialCaseList.append(new_filepath)
            ScenarioForOneID = {
                "realDM": realDM,
                "ec2dDM": ec2dDM,
                "special": specialCaseList
            }
            dmPathList.append(ScenarioForOneID)
        return dmPathList
    
    def createRunningFile(self,dirpath,X_set,numClients,numThreads,numRealDM,numIterations,name):
        fullList = []
        dmPathList = self.getDMpaths(dirpath)
        inputs={
            "dm":"placeholder", # THIS IS NOT USED ANYMORE!!!! DONT DELETE IT THO
            "X_set":X_set, # Instead of debug boolean assign debug.vrp here
            "numClients": numClients 
            }
        for case in dmPathList:
            caseList = []
            writeFile = {
            "RealDM": "",
            "Ec2DDM": "",
            "inputs": inputs,
            "numThreads": numThreads,
            "numEc2D": numThreads-numRealDM,
            "numRealDM": numRealDM,
            "numIterations": numIterations 
            }
            writeFile["RealDM"] = case["realDM"]
            writeFile["Ec2DDM"] = case["ec2dDM"]
            caseList.append(copy.deepcopy(writeFile))

            for dm in case["special"]:
                writeFile["RealDM"] = dm
                writeFile["Ec2DDM"] = dm
                caseList.append(copy.deepcopy(writeFile))
            fullList.append(caseList)

        
        output_path = os.path.join("data/runFiles",f"{name}.json")
        with open(output_path,"w") as f:
            rapidjson.dump(fullList,f,indent=4)
            
    def runRunningFile(self,name):
        runfilePath = os.path.join("data/runFiles", f"{name}.json")
        with open(runfilePath,"r") as f:
            cases = rapidjson.load(f)
        for i,run in enumerate(cases):
            pathList = []
            for x, process in enumerate(run):
                inputList = list(process.values())
                self.startJob(inputList)
                rs = Result_Server()
                output_path = rs.combineJSONS()
                output_path = Path(output_path)

                new_path = output_path.with_name(f"{x}_{output_path.name}")
                output_path.rename(new_path)
                pathList.append(new_path)
            os.makedirs("BatchCustom",exist_ok=True)
            dirpath = f"BatchCustom/{i}"
            os.makedirs(os.path.join("BatchCustom",str(i)),exist_ok=True)
            for path in pathList:
                os.rename(path,os.path.join(dirpath,os.path.basename(path)))


            






    
        


                
        
    


        
    def readPOSTrequestToList(self,inputsHTMLstr):
        inputsHTML = json.loads(inputsHTMLstr)
        inputs={
            "dm":"placeholder", # THIS IS NOT USED ANYMORE!!!! DONT DELETE IT THO
            "X_set":inputsHTML["vrp-file"], # Instead of debug boolean assign debug.vrp here
            "numClients": inputsHTML["numClients"]
            }
        inputsHTMLList = []
        inputsHTMLList.append(city_matrices[f"{inputsHTML['city']}"][0])
        inputsHTMLList.append(city_matrices[f"{inputsHTML['city']}"][1])
        inputsHTMLList.append(inputs)
        inputsHTMLList.append(inputsHTML["numThreads"])
        inputsHTMLList.append(inputsHTML["numEc2D"])
        inputsHTMLList.append(inputsHTML["numRealDM"])
        inputsHTMLList.append(inputsHTML["numIterations"])
        return inputsHTMLList
    





            



if __name__ == "__main__":
    # old main
    #inputsHTMLstr = sys.argv[1]
    #bq = BatchQueue()
    #inputsHTMList = bq.readPOSTrequestToList(inputsHTMLstr)
    
    #    ## inputs at index [2]
    #bq = BatchQueue()
    #bq.allVrpSetsOneCity(inputsHTMList)
    #bq.fourSpecialCase("berkeRequest.json")

    # new main

    bq = BatchQueue()
    # outputs to data/runFiles und given name
    bq.createRunningFile("100x500MunichTest","debug",499,8,6,500,"500xSampleRun")
    #bq.runRunningFile("200xSampleRun")


    
    

