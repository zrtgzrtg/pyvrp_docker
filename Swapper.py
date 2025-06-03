
import rapidjson
import os


class Swapper():
    def __init__(self,matrix_name1,matrix_name2=None):
        self.path1 = os.path.join("data/distance_matrices",f"{matrix_name1}.json")
        self.path2 = os.path.join("data/distance_matrices",f"{matrix_name2}.json")
        self.matrix_name1 = matrix_name1
        self.matrix_name2 = matrix_name2
        self.data1 = "NOT ASSIGNED YET"
        self.data2 = "NOT ASSIGNED YET"
        self.swapResult = "NOT ASSIGNED YET"
        os.makedirs("swapperResDir", exist_ok=True)
        self.resDir = "swapperResDir"
    
    def importMatrix(self,matrix_num=1):
        data = None
        path = self.getPath(matrix_num)
        data = self.getData(matrix_num)
        try:
            with open(path,"r") as f:
                data = rapidjson.load(f)
                self.setData(data,matrix_num)
        except Exception as e:
            print(e)
            print("\n")
            print(f"Path doesnt exist. Currently Path: {path}")
        

    def getPath(self,matrix_num):
        if matrix_num == 1:
            return self.path1
        else: 
            return self.path2
    
    def getData(self,matrix_num):
        if matrix_num == 1:
            return self.data1
        else:
            return self.data2
    def setData(self,data,matrix_num):
        if matrix_num == 1:
            self.data1 = data
        else:
            self.data2 = data

        

    def findEntriesByOriginID(self,OriginID,matrix_num=1):
        allConnections = []
        for entry in self.data1:
            if entry["OriginID"] == OriginID:
                allConnections.append(entry)
            else:
                pass
        return allConnections
    def findEntriesByDestinationID(self,DestinationID,matrix_num=1):
        allConnections = []
        for entry in self.data1:
            if entry["DestinationID"] == DestinationID:
                allConnections.append(entry)
            else:
                pass
        return allConnections
    
    def swapDistancesREALEC2DforEntry(self,OriginID):
        realDMOrigin = self.findEntriesByOriginID(OriginID,1)
        realDMDestination = self.findEntriesByDestinationID(OriginID,1)
        ec2dDMOrigin = self.findEntriesByOriginID(OriginID,2)
        ec2dDMDestination = self.findEntriesByDestinationID(OriginID,2)
        
        swapDict = {}

        for i,entEc2DDMOrigin in enumerate(ec2dDMOrigin):
            entEc2DDMOrigin["Total_Length"] = realDMOrigin[i]["Total_Length"]
        for i,entEc2DDMDestination in enumerate(ec2dDMDestination):
            entEc2DDMDestination["Total_Length"] = realDMDestination[i]["Total_Length"]
        
        for x in ec2dDMOrigin:
            key = (x["OriginID"],x["DestinationID"])
            swapDict[key] = x["Total_Length"]
        for y in ec2dDMDestination:
            key = (y["OriginID"],y["DestinationID"])
            swapDict[key] = y["Total_Length"]

        return swapDict
    
    def fillSwapResult(self,OriginID):
        with open(self.path2,"r") as f:
            self.swapResult = rapidjson.load(f)
        swapDict = self.swapDistancesREALEC2DforEntry(OriginID)
        self.writeEntries(swapDict)
    
    def writeEntries(self,swapDict):
        for idx, swapEnt in enumerate(self.swapResult):
            swapEntTouple = (swapEnt["OriginID"],swapEnt["DestinationID"])
            if  swapEntTouple in swapDict:
                self.swapResult[idx]["Total_Length"] = swapDict[swapEntTouple]

    def writeToFile(self,name):
        with open(os.path.join(self.resDir, f"{name}.json"),"w") as f:
            rapidjson.dump(self.swapResult,f,indent=4)
    
    def fullSwapFile(self,OriginID,name):
        self.importMatrix(1)
        self.importMatrix(2)
        self.fillSwapResult(OriginID)
        self.writeToFile(name)
    
    def testSwapFile(self,OriginID,name):
        data = None
        with open(os.path.join("swapperResDir",f"{name}.json"), "r") as f:
            data = rapidjson.load(f)

        data1dict = {}
        data2dict = {}

        for x in self.data1:
            key = (x["OriginID"],x["DestinationID"])
            data1dict[key] = x["Total_Length"]
        for y in self.data2:
            key = (y["OriginID"],y["DestinationID"])
            data2dict[key] = y["Total_Length"]
        
        for dir in data:
            if dir["OriginID"] == OriginID or dir["DestinationID"] == OriginID:
                assert dir["Total_Length"] == data1dict[(dir["OriginID"],dir["DestinationID"])], f"Failed on Change in OriginID: {dir['OriginID']} and DestinationID: {dir['DestinationID']} \n"
                print(f"Success in ChangeToRealDM for {(dir['OriginID'],dir['DestinationID'])}")
            else:
                assert dir["Total_Length"] == data2dict[(dir["OriginID"],dir["DestinationID"])], f"Failed on Base in OriginID: {dir['OriginID']} and DestinationID: {dir['DestinationID']} \n"
                print(f"Success in StayEc2D for {(dir['OriginID'],dir['DestinationID'])}")
        print("\n")
        print("----------ALL_TESTS_PASSED----------\n")






if __name__ == "__main__":
    s = Swapper("Munich_DHL_10x10_RoadData","Munich_DHL_10x10_EuclideanData")
    name = "firstTest"
    s.fullSwapFile(1,name)
    s.testSwapFile(1,name)
