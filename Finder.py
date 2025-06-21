
import csv
import os
import rapidjson

class Finder():
    def __init__(self,realDM,ec2dDM):
        self.dmPath = "data/distance_matrices"
        self.realDM = realDM
        self.ec2dDM = ec2dDM

    def importMatrices(self):
        pathRealDM = os.path.join(self.dmPath,self.realDM)
        pathEc2dDM = os.path.join(self.dmPath,self.ec2dDM)
        with open(pathRealDM,"r") as f:
            dataRealDM = rapidjson.load(f)
        with open(pathEc2dDM,"r") as f1:
            dataEc2DDM = rapidjson.load(f1)
        
        lookupDictReal = {}
        lookupDictEuc = {}
        for objR in dataRealDM:
            key = (objR["OriginID"],objR["DestinationID"])
            val = objR["Total_Length"]
            lookupDictReal[key] = val
        for objE in dataEc2DDM:
            key = (objE["OriginID"],objE["DestinationID"])
            val = objE["Total_Length"]
            lookupDictEuc[key] = val



        return lookupDictReal,lookupDictEuc
    
    def retBiggestDifferenceFile(self,name):
        tuple3List = []
        realDM,eucDM = self.importMatrices()
        for objE in eucDM:
            print(objE)
            res = (objE[0],objE[1],(realDM[objE]-eucDM[objE]))
            tuple3List.append(res)
        
        sorted_data = sorted(tuple3List, key=lambda x: x[2], reverse=True)


        os.makedirs("finderResDir",exist_ok=True)
        with open(f"finderResDir/{name}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["OriginID", "DestinationID", "Difference"]) 
            writer.writerows(sorted_data)

        # test for symmetry. All our dms are symmetrical
        #for entry in eucDM.keys():
        #    swapEntry = (entry[1],entry[0])
        #    diff = abs(eucDM[entry] - eucDM[swapEntry])
        #    if diff > 0.1:
        #        print(entry,diff)
        #    else:
        #        pass



        



if __name__ == "__main__":
    f = Finder("Utah_GroceryStores_1161x1161_RoadData.json","Utah_GroceryStores_1161x1161_EuclideanData.json")
    #f = Finder("Munich_DHL_10x10_RoadData.json","Munich_DHL_10x10_EuclideanData.json")
    f.retBiggestDifferenceFile("UtahBigDifferences")




