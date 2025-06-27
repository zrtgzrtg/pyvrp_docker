
import re
import csv
import os


class Scanner():
    def __init__(self,subDir,filename):
        self.mainPath = "scannerInputDir/csv_files_analysis"
        self.csv = self.importCsv(subDir,filename)
        self.dict = None
    

    def importCsv(self,subDir,filename):
        join = os.path.join(self.mainPath,subDir,filename)
        path = f"{join}.csv"

        with open(path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            return list(reader)
    def addX_setColumn(self):

    
    def convertToDict(self):
        pass






if __name__ == "__main__":
    s = Scanner("allXSetsUpdated","Total_Route_Lengths_Munich_1000x100_allXSets_Updated")
    # From csv[x][y] x iterates through entries and y through the entries there. [3] is the distance
    print(s.csv[1][3])