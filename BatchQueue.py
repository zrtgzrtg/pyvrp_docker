
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
    

    # This is a help method to only sample ID0 since all are runtime restricted!!!
    # Only change is the if statement

    def getDMpathsOnlyID0(self,dirpath):
        parentpath = "data/distance_matrices/"
        path = os.path.join(parentpath,dirpath)
        dmPathList = []
        
        for dirs in os.listdir(path):
            if dirs == "ID0":
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
            else:
                pass
        return dmPathList
    

    # Again just a copy with small changes from createRunningFile since Runtime restriction

    def createRunningFile(self,dirpath,X_set,numClients,numThreads,numRealDM,numIterations,name):
        fullList = []
        dmPathList = self.getDMpaths(dirpath)
        print(dmPathList)
        inputs={
            "dm":"placeholder", # THIS IS NOT USED ANYMORE!!!! DONT DELETE IT THO
            "X_set":X_set, # Instead of debug boolean assign debug.vrp here
            "numClients": numClients 
            }
        for case in dmPathList:
            print(case)
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

        
        os.makedirs("data/runFiles",exist_ok=True)
        output_path = os.path.join("data/runFiles",f"{name}.json")
        with open(output_path,"w") as f:
            rapidjson.dump(fullList,f,indent=4)

   
    
    def createRunningFileOnlyID0(self,dirpath,X_set,numClients,numThreads,numRealDM,numIterations,name):
        fullList = []
        dmPathList = self.getDMpathsOnlyID0(dirpath)
        inputs={
            "dm":"placeholder", # THIS IS NOT USED ANYMORE!!!! DONT DELETE IT THO
            "X_set":X_set, # Instead of debug boolean assign debug.vrp here
            "numClients": numClients 
            }
        vrp_path = "data/Vrp-Set-X/X"
        x_set_list = []
        for file in os.listdir(vrp_path):
            if file != "debug.vrp":
                x_set_list.append(file)
            else:
                pass
        
        for case in dmPathList:
            for vrpFile in x_set_list:
                inputs["X_set"] = vrpFile

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
    

def print_distance_matrix_info(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
        for obj in data:
            for obj2 in obj:
                print(obj2["RealDM"], obj2["Ec2DDM"], obj2["inputs"]["X_set"])




            



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
    #bq.createRunningFileOnlyID0("50x100MunichTest","placeholder",99,8,6,500,"50xSampleRunWithID0andAllX_sets")
    #bq.createRunningFile("3x100MunichWithPercent","debug",99,8,8,500,"3x100MunichWithPercent")
    bq.runRunningFile("100x100MunichWithPercentDebug")
    #print_distance_matrix_info("data/runFiles/50xSampleRunWithID0andAllX_sets.json")


    
    

