from ProblemDataGenerator import ProblemDataGenerator
from create_data_for_api import DataCreator
import json
import os

class Res_Builder():
    def __init__(self,inputs,resDictName):
        self.inputs = inputs
        self.resDictName = resDictName

    def getProblemData(self):
        gen = ProblemDataGenerator(self.inputs["dm"],self.inputs["X_set"],self.inputs["numClients"])
        problemData = gen.getProblemData()
        return problemData

    def returnRes(self):
        dataCFAKE = DataCreator("placerholder returnRes","placerholder returnRes","placerholder returnRes","placerholder returnRes")
        resDictRebuild = dataCFAKE.build_from_resdict(self.import_resDict(), self.getProblemData())
        return resDictRebuild
    
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
            return json_data
    
    
        




if __name__ == "__main__":
    inputs={
        "dm":"Munich_DHL_1747x1747_RoadData",
        "X_set":"X-n1001-k43",
        "numClients":"1746"
        }
    resB = Res_Builder(inputs, "Munich23k.json")
    print(resB.returnRes())