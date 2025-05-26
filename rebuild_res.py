from ProblemDataGenerator import ProblemDataGenerator
import shutil
import zipfile
import sys
from create_data_for_api import DataCreator
import json
import rapidjson
import os
from data.city_matrices import city_matrices

class Res_Builder():
    def __init__(self,inputs,resDictPathtmp):
        self.inputs = inputs
        self.resDictPathtmp = resDictPathtmp
        self.resDictName = os.path.basename(resDictPathtmp)
        self.genRealDM = ProblemDataGenerator(self.inputs["Realdm"],self.inputs["X_set"],self.inputs["numClients"])
        self.genEc2D = ProblemDataGenerator(self.inputs["Ec2Ddm"],self.inputs["X_set"],self.inputs["numClients"])
        

    def getProblemData(self,isRealDM:bool):
        if isRealDM:
            return self.genRealDM.getProblemData()
        else:
            return self.genEc2D.getProblemData()

    #only help method for combined json now
    def returnRes(self,resDict,isRealDm):
        dataCFAKE = DataCreator("placerholder returnRes","placerholder returnRes","placerholder returnRes","placerholder returnRes","f")
        resDictRebuild = dataCFAKE.build_from_resdict(resDict, self.getProblemData(isRealDm))
        return resDictRebuild
    
    #only help method for combined json now
    def import_resDict(self):
        json_data = None
        current_dir = os.path.dirname(__file__)
        location = f"Import_loc_for_resDict/{self.resDictName}"
        filepath = os.path.join(current_dir,location)
        if not os.path.isfile(filepath):
            raise ValueError("resDictName is not a valid file. Please recreate class!!!")
        else :
            with open(filepath,"r") as resDict:
                json_data = json.load(resDict)
        if json_data is None:
            raise ValueError("json_data not imported correctly. It is still None!!")
        else:
            if not json_data.get("isFeasible",False):
                print("Solution is marked as infeasible. Rebuild will be wrong")
                return json_data
    # ignore entirely
    def retSplitJsonTEST(self, bigJsonPath):
        with open(bigJsonPath, "r") as f:
            combined = json.load(f)

        with open("Import_loc_for_resDict/1_24k.json","w") as f1:
            json.dump(combined[0],f1)
    
        with open("Import_loc_for_resDict/2_24k.json","w") as f2:
            json.dump(combined[1],f2)
    # use this
    def runRebuildCombinedResDict(self):
        with open(self.resDictPathtmp,"r") as f:
            data = rapidjson.load(f, allow_nan=True)
        combinedFeasList = []
        for entry in data:
            if entry.get("isFeasible",True):
                combinedFeasList.append(entry)
            else:
                pass

        combinedRealDM =[]
        combindedEc2D = []
        print(f"{self.inputs['Realdm']} showcase")
        for ent in combinedFeasList:
            print(ent.get("DMUsedName"))
            if ent.get("DMUsedName", self.inputs["Realdm"]):
                print("reached Real")
                combinedRealDM.append(self.returnRes(ent,True))
            else:
                print("reached ec2d")
                combindedEc2D.append(self.returnRes(ent,False))
        return combinedRealDM,combindedEc2D

def findBestinList(resList):
    for index, res in enumerate(resList):
        currentBest = sys.maxsize -1
        currentBestIndex = None
        if res.best.distance() > currentBest:
            currentBest = res.best.distance()
            currentBestIndex = index
    print(f"Best Val is: {currentBest} at listIndex: {currentBestIndex}")
    
    return currentBest,currentBestIndex

def importInputData(filepath):
    with open(filepath,"r") as f:
        inputHTML = json.load(f)
    return inputHTML

def Res_Builder_Factory(zipfilepath):
    os.makedirs("tmpZip/", exist_ok=True)
    name = os.path.basename(zipfilepath)
    filepathExtract = f"tmpZip/"
    with zipfile.ZipFile(zipfilepath,"r") as f:
        f.extractall(filepathExtract)
    inputHTMLpath = os.path.join(filepathExtract,"inputsHTML.json")
    resDictpath = os.path.join(filepathExtract,"resDict.json")
    inputHTML = importInputData(inputHTMLpath)
    RealDMname, Ec2DName = city_matrices[inputHTML["city"]]
    inputs = {
        "Realdm": RealDMname,
        "Ec2Ddm": Ec2DName,
        "X_set": f"{inputHTML['vrp-file']}",
        "numClients": inputHTML["numClients"]
    }

    rB = Res_Builder(inputs,resDictpath)
    return rB




    
    


        

            

    
        

if __name__ == "__main__":

    importZipPathfirst = "Import_loc_for_resDict"
    # in importZiptpath put the name f the imported zip
    importZipPath = os.path.join(importZipPathfirst,"combined_resDict_M40k.zip")
    resBuilder = Res_Builder_Factory(importZipPath)
    resListRealDM, resListEc2D = resBuilder.runRebuildCombinedResDict()
    for res in resListEc2D:
        print(res)
   
    #builder = Res_Builder(inputs,"f")
    #builder.retSplitJsonTEST("Import_loc_for_resDict/combinedresDict24k.json")


    #resB = Res_Builder(inputs,importZipPath) 
    #resListRealDM,resListEc2D = resB.runRebuildCombinedResDict()
    inputs={
           "Realdm":"Chicago_100x100_RoadData", # THIS IS THE DM USED FOR PROBLEMDATA!!! ALWAYS MAKE SURE YOU IMPORT EUCLIDIAN OR REALDM
           "Ec2Ddm":"Chicago_100x100_EuclideanData",
           "X_set":"X-n101-k25",
           "numClients":"99"
           }

    #resZ = ProblemDataGenerator(inputs["Realdm"], inputs["X_set"],inputs["numClients"])
    #problemData = resZ.getProblemData()

