
from ResultServer import Result_Server
from data.city_matrices import city_matrices
import json
import sys
import os
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
    #inputsHTMLstr = sys.argv[1]
    bq = BatchQueue()
    #inputsHTMList = bq.readPOSTrequestToList(inputsHTMLstr)
    
        ## inputs at index [2]
    #bq = BatchQueue()
    #bq.allVrpSetsOneCity(inputsHTMLList)
    bq.fourSpecialCase("berkeRequest.json")


    
    

