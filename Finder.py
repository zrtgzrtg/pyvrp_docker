
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
            res = (objE[0],objE[1],(realDM[objE]-eucDM[objE]))
            tuple3List.append(res)
        
        sorted_data = sorted(tuple3List, key=lambda x: x[2], reverse=True)


        os.makedirs("finderResDir",exist_ok=True)
        with open(f"finderResDir/{name}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["OriginID", "DestinationID", "Difference"]) 
            writer.writerows(sorted_data)
        
        return sorted_data
    
    def findBiggestDifference(self,numIDs):
        sortedList = self.retBiggestDifferenceFile("tmp")
        combinedDiffDict = {}
        for entry in sortedList:
            if f"{entry[0]}" not in combinedDiffDict:
                combinedDiffDict[f"{entry[0]}"] = 0
            combinedDiffDict[f"{entry[0]}"] += entry[2]
        tuple_list = list(combinedDiffDict.items())
        sorted_tuple_list = sorted(tuple_list, key=lambda x: x[1], reverse=True)

        retList = []
        retListIDs = []
        for i in range(numIDs):
            retList.append(sorted_tuple_list[i])
            retListIDs.append(sorted_tuple_list[i][0])
        

        return retListIDs,retList

        
        


        # test for symmetry. All our dms are symmetrical
        #for entry in eucDM.keys():
        #    swapEntry = (entry[1],entry[0])
        #    diff = abs(eucDM[entry] - eucDM[swapEntry])
        #    if diff > 0.1:
        #        print(entry,diff)
        #    else:
        #        pass



        



if __name__ == "__main__":
    f = Finder("Munich_DHL_1747x1747_RoadData.json","Munich_DHL_1747x1747_EuclideanData.json")
    #f = Finder("Munich_DHL_10x10_RoadData.json","Munich_DHL_10x10_EuclideanData.json")
    #f.retBiggestDifferenceFile("UtahBigDifferencesUpdate")
    resListIDS, resList = f.findBiggestDifference(10)
    print(resList)
    




