from ProblemDataGenerator import ProblemDataGenerator
import sys
from create_data_for_api import DataCreator
import json
import orjson
import os

class Res_Builder():
    def __init__(self,inputs,resDictName):
        self.inputs = inputs
        self.resDictName = resDictName
        self.genRealDM = ProblemDataGenerator(self.inputs["Realdm"],self.inputs["X_set"],self.inputs["numClients"])
        self.genEc2D = ProblemDataGenerator(self.inputs["Ec2Ddm"],self.inputs["X_set"],self.inputs["numClients"])
        

    def getProblemData(self,isRealDM:bool):
        if isRealDM:
            return self.genRealDM
        else:
            return self.genEc2D

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
        with open(self.resDictName,"rb") as f:
            data = orjson.loads(f.read())
        combinedFeasList = []
        for entry in data:
            if entry.get("isFeasible",True):
                combinedFeasList.append(entry)
            else:
                pass

        combinedRealDM =[]
        combindedEc2D = []
        for ent in combinedFeasList:
            if ent.get("DMUsedName", self.inputs["Realdm"]):
                combinedRealDM.append(self.returnRes(ent,True))
            else:
                combindedEc2D.append(self.returnRes(ent,False))
        return combinedRealDM,combindedEc2D

    def findBestinList(self,resList):
        for index, res in enumerate(resList):
            currentBest = sys.maxsize -1
            currentBestIndex = None
            if res.best.objective() > currentBest:
                currentBest = res.best.objective()
                currentBestIndex = index
        print(f"Best Val is: {currentBest} at listIndex: {currentBestIndex}")
        return currentBest,currentBestIndex


            

    
        




if __name__ == "__main__":
    inputs={
        "Realdm":"Chicago_100x100_RoadData", # THIS IS THE DM USED FOR PROBLEMDATA!!! ALWAYS MAKE SURE YOU IMPORT EUCLIDIAN OR REALDM
        "Ec2Ddm":"Chicago_100x100_EuclideanData",
        "X_set":"X-n101-k25",
        "numClients":"99"
        }
    #builder = Res_Builder(inputs,"f")
    #builder.retSplitJsonTEST("Import_loc_for_resDict/combinedresDict24k.json")


    resB = Res_Builder(inputs, "Import_loc_for_resDict/64Threads150kChicago.json")
    resListRealDM,resListEc2D = resB.runRebuildCombinedResDict()

    bestRealDMRes,bestRealDMResIndex = resB.findBestinList(resListRealDM)
    bestEc2DRes, bestEc2DResIndex = resB.findBestinList(resListEc2D)
    print(bestRealDMRes.best)
    print("\n\n")
    print(bestEc2DRes.best)

