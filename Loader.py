
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
    def createEntry(self):
        pass






if __name__=="__main__":
    l = Loader("SamplesUSED/100x100MunichSamplesTEST2")
    l.findFiles()