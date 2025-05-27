from ProblemDataGenerator import ProblemDataGenerator
import pickle
import shutil
import zipfile
import sys
from create_data_for_api import DataCreator
import json
import rapidjson
import os
from data.city_matrices import city_matrices

class Res_Builder():
    def __init__(self,inputs,resDictPathtmp,inputHTMLpassObj):
        self.inputs = inputs
        self.resDictPathtmp = resDictPathtmp
        self.resDictName = os.path.basename(resDictPathtmp)
        self.genRealDM = ProblemDataGenerator(self.inputs["Realdm"],self.inputs["X_set"],self.inputs["numClients"])
        self.genEc2D = ProblemDataGenerator(self.inputs["Ec2Ddm"],self.inputs["X_set"],self.inputs["numClients"])
        self.inputHTML = inputHTMLpassObj
        

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
        for ent in combinedFeasList:
            print(ent.get("DMUsedName"))
            if ent.get("DMUsedName") == self.inputs.get("Realdm"):
                print("reached Real")
                print(ent.get("DMUsedName"))
                combinedRealDM.append(self.returnRes(ent,True))
            else:
                print("reached ec2d")
                print(ent.get("DMUsedName"))
                combindedEc2D.append(self.returnRes(ent,False))
        return combinedRealDM,combindedEc2D,self.inputHTML

def findBestinList(resList):
    for index, res in enumerate(resList):
        sorted_list = sorted(resList, key=lambda x: x.best.distance())
        currentBest = sorted_list[0].best.distance()
    print(f"Best Val is: {currentBest}")
    return sorted_list
    

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

    rB = Res_Builder(inputs,resDictpath,inputHTML)
    return rB
def appendResListDictToPickle(importName,listRealDMSorted,listEc2DSorted,inputHTML):
    dbLocation = "pickleDB/db.pkl"
    dict = {
            "SortedRealDM": listRealDMSorted,
            "SortedEc2D": listEc2DSorted,
            "inputHTML": inputHTML
        }
    if os.path.exists(dbLocation):
        with open(dbLocation, "rb") as f:
            db = pickle.load(f)
        if importName in db:
                print(f"No save possible! Key: {importName} already exists in db!")
                return importName,listRealDMSorted,listEc2DSorted,inputHTML
        else:
                print(f"Saving under the name {importName}")
                db[f"{importName}"] = dict
                with open(dbLocation,"wb") as f2:
                    pickle.dump(db,f2)
    else:
        saveAsBackup(importName,listRealDMSorted,listEc2DSorted,inputHTML)

def saveAsBackup(importName,listRealDMSorted,listEc2DSorted,inputHTML):
    dict = {
                "SortedRealDM": listRealDMSorted,
                "SortedEc2D": listEc2DSorted,
                "inputHTML": inputHTML
            }
    os.makedirs("pickleDB/backups",exist_ok=True)
    with open(f"pickleDB/backups/{importName}.pkl", "wb") as f:
            pickle.dump(dict, f)


def getDB():
    with open("pickleDB/db.pkl", "rb") as f:
        db = pickle.load(f)
    return db
def importAndSaveToDB(zipName):
    importZipPathfirst = "Import_loc_for_resDict"
    # in importZiptpath put the name f the imported zip
    zipNameadded = f"{zipName}.zip"
    importZipPath = os.path.join(importZipPathfirst,zipNameadded)
    resBuilder = Res_Builder_Factory(importZipPath)
    resListRealDM, resListEc2D,inputHTML = resBuilder.runRebuildCombinedResDict()
    #for res in resListRealDM:
    #    print(res)
    #for res in resListEc2D:
    #    print(res)
    resListRealDMSorted = findBestinList(resListRealDM)
    resListEc2DSorted = findBestinList(resListEc2D)
    print(resListRealDMSorted[0])
    print("\n\n")
    print(resListEc2DSorted[0])
    nameInDB = os.path.splitext(os.path.basename(importZipPath))[0]
    print(nameInDB)
    saveAsBackup(nameInDB,resListRealDMSorted,resListEc2DSorted,inputHTML)

def loadPickleBackup(zipName,indexRealDM,indexEc2D):
    with open(f"pickleDB/backups/{zipName}.pkl", "rb") as f:
        data = pickle.load(f)
    print("-----------INPUTS-----------\n")
    print(f"{data['inputHTML']}\n")
    print("-----------BESTREALDM-----------\n")
    print(f"{data['SortedRealDM'][indexRealDM]}\n")
    print("-----------BESTEC2D-----------\n")
    print(data["SortedEc2D"][indexEc2D])
 

if __name__ == "__main__":
    zipName = "32x20kChicago"
    #importAndSaveToDB(zipName)

    loadPickleBackup("32x20kChicago",0,0)
   

   
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

