
import csv
import os

class Transformer():
    def __init__(self,file):
        self.file = file
    
    def importFile(self):
        with open(self.file,newline='') as f:
            reader = csv.reader(f)
            
            with open("transformerInputDir/results","w") as x:
                pass
            for row in reader:
                filename = row[0]
                value = row[1]
                X_set = row[0].split('_')[-1].replace('.shp', '')
                with open("transformerInputDir/results","a") as w:
                    writer = csv.writer(w)
                    writer.writerow([filename,value,X_set])

            
                


                

            


if __name__ == "__main__":
    t = Transformer("transformerInputDir/csv_files_analysis/Total_Route_Lengths_Munich_1000x100_allXSets.csv")
    t.importFile()