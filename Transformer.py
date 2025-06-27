
import re
import csv
import os

class Transformer():
    def __init__(self,file):
        self.file = file
    
    def importFile(self):
        with open(self.file,newline='') as f:
            reader = csv.reader(f)
            
            for row in reader:
                filename = row[0]
                capacityUsed = row[1]
                demandsUsed = row[2]
                value = row[3]
                X_set = row[0].split('_')[-1].replace('.shp', '')

                base, ext = os.path.splitext(self.file)

                with open(f"{base}.txt","a") as w:
                    writer = csv.writer(w)
                    writer.writerow([filename,capacityUsed,demandsUsed,value,X_set])
                os.rename(f"{base}.txt",self.file)
    
    def addIdColumn(self):
        input_file = self.file
        base, ext = os.path.splitext(self.file)
        output_file = os.path.join(f"{base}_res{ext}")

        # Read and write CSV
        with open(input_file, mode="r", newline="") as infile: 
            with open(output_file, mode="w", newline="") as outfile:
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames + ["ID"]  # Add new column
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    match = re.search(r"ID(\d+)", row["Simulation_Name"])
                    row["ID"] = match.group(1) if match else ""
                    writer.writerow(row)
    def verifyIDs(self,size,fd):
        l = []
        with open(self.file,newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                l.append(row[2])
        
        l_set = set(l)
        l_2 = sorted(list(l_set))
        inList = []
        notInList = []

        l_2_int = []

        for obj in l_2:
            if obj == "ID":
                pass
            else:
                l_2_int.append(int(obj))
        
        l_2_sorted = sorted(l_2_int)
        
        print("l_sorted_int\n",file=fd)
        print(l_2_sorted,file=fd)

        for i in range(size):
            if i in l_2_sorted:
                inList.append(i)
            else:
                notInList.append(i)


        print("inList:\n",file=fd)
        print(inList,file=fd)
        print("notInList:\n",file=fd)
        print(notInList,file=fd)



            
                


                

            


if __name__ == "__main__":
    path = "transformerInputDir/csv_files_analysis/debugDemand"
    for p in os.listdir(path):
        filepath = os.path.join(path,p)
        if "_res" in filepath:
            print(filepath)
            trans = Transformer(filepath)
            varInput = input(f"Enter for {filepath}:")

            varInputInt = int(varInput)

            base,ext = os.path.splitext(filepath)
            with open(f"{base}.txt","w") as f:
                trans.verifyIDs(varInputInt,f)
        
    #t = Transformer("transformerInputDir/csv_files_analysis/varying_demand/Total_Route_Lengths_Munich_100x500_varyingDemand_500X_n502_k39_res.csv")
    #t.addIdColumn()
    #t.verifyIDs(100)