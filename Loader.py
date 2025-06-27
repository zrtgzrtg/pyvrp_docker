
import shutil
import re
import zipfile
import os
from data.city_matrices import city_matrices

class Loader():
    def __init__(self,dirpath):
        self.dirpath = dirpath
        pass

    def findAndExtractFiles(self):
        for path in os.listdir(self.dirpath):
            zippath = os.path.join(self.dirpath,path)
            for innerPath in os.listdir(zippath):
                filename = innerPath
                filepath = os.path.join(zippath,innerPath)
                with zipfile.ZipFile(filepath,"r") as f:
                    f.extractall(zippath)
    def createEntryInDistance_Matrices(self,importName):
        dirpath = f"data/distance_matrices/{importName}"
        os.makedirs(dirpath,exist_ok=True)
        for path in os.listdir(self.dirpath):
            zippath = os.path.join(self.dirpath,path)
            name = os.path.basename(zippath)
            match = re.search(r'ID\d+', name)
            strID = match.group()
            mainDir = os.path.join(zippath,strID)
            os.makedirs(mainDir,exist_ok=True)
            
            normalPath = os.path.join(mainDir,"normalCase")
            specialPath = os.path.join(mainDir,"specialCases")

            os.makedirs(normalPath,exist_ok=True)
            os.makedirs(specialPath,exist_ok=True)

            for idpath in os.listdir(zippath):
                fullpath = os.path.join(zippath,idpath)
                print(fullpath)
                if "Real" in idpath and "Ec2d" in idpath:
                    os.rename(fullpath,os.path.join(zippath,f"{strID}/specialCases",idpath))
                elif ("Real" in idpath and "Ec2d" not in idpath):
                    os.rename(fullpath,os.path.join(zippath,f"{strID}/normalCase",idpath))
                elif ("Real" not in idpath and "Ec2d" in idpath and "Special" not in idpath):
                    os.rename(fullpath,os.path.join(zippath,f"{strID}/normalCase",idpath))
                elif ("Percent" in idpath or "Special" in idpath):
                    os.rename(fullpath,os.path.join(zippath,f"{strID}/specialCases",idpath))
            shutil.move(mainDir,dirpath)






if __name__=="__main__":
    l = Loader("SamplesUSED/3x100MunichWithPercent")
    l.findAndExtractFiles()
    l.createEntryInDistance_Matrices("3x100MunichWithPercent")