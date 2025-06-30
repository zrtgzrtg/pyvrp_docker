
import copy
import rapidjson
import shutil
import csv
import os

class Circuity():
    def __init__(self,constantPath,DMDIR):
        self.constantPath  = constantPath
        self.DMDir = DMDIR
        self.diffDir = None
        self.pathList = None
        self.percentList = [(5, '5Percent'),
(10, '10Percent'),
(15, '15Percent'),
(20, '20Percent'),
(25, '25Percent'),
(30, '30Percent'),
(35, '35Percent'),
(40, '40Percent'),
(45, '45Percent'),
(50, '50Percent')]
    

    def importFiles(self):
        with open(self.constantPath,newline='') as f:
            reader = csv.reader(f)
            differencesDir = {}
            for i,row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    differencesDir[row[0]] = [row[1],row[2]]
            
            self.diffDir = differencesDir
            
    def collectFilePaths(self):
        self.importFiles()
        for path in os.listdir(self.DMDir):
            id = os.path.basename(path)[2:]
            self.diffDir[id].append(os.path.join(self.DMDir,path))
    

    def copyEuc(self):
        self.collectFilePaths()
        for i,entry in enumerate(self.diffDir):
            if i > 0:
                break
            dirpath = self.diffDir[entry][2]
            for case in os.listdir(dirpath):
                if case == "normalCase":
                    filepath = os.path.join(dirpath,case)
                    for files in os.listdir(filepath):
                        filepaths = os.path.join(filepath,files)
                        if "Ec2d" in filepaths:
                            cpPath = f"{dirpath}/specialCases/"
                            name = os.path.basename(filepaths)
                            name2 = f"circuity{name}"
                            factor = float(self.diffDir[entry][0])
                            circuityPath = f"{cpPath}{name2}"
                            shutil.copy(filepaths,f"{cpPath}{name}")

                            shutil.copy(filepaths,circuityPath)
                            with open(circuityPath,"r") as f:
                                eucDM = rapidjson.load(f)
                                cpList = []
                                copyDir = {}
                                for element in eucDM:
                                    length = element["Total_Length"]
                                    lengthMod = length*factor
                                    print(lengthMod)
                                    copyDir["OriginID"] = element["OriginID"]
                                    copyDir["DestinationID"] = element["DestinationID"]
                                    copyDir["Total_Length"] = lengthMod
                                    cpList.append(copy.deepcopy(copyDir))
                            with open(circuityPath,"w") as f2:
                                rapidjson.dump(cpList,f2,indent=4)
                                
                                
                else:
                    filepath = os.path.join(dirpath,case)
                    for files in os.listdir(filepath):
                        filepaths = os.path.join(filepath,files)
                        if "Ec2dWithRealDepotSampleMunich" in filepaths:
                            pass
                            os.remove(filepaths)


    
    
    
    
if __name__ == "__main__":
    c = Circuity("circuity_factor_dir/Munich_1000x100_Demand1_Cap10_InputvsOutputDif.csv","data/distance_matrices/100x100MunichTest_circuity_test/")
    c.copyEuc()