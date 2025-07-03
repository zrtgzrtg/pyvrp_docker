
import re
import os
import csv

def importFile(path):
    with open(path,newline='') as f:
        reader = csv.reader(f)
        rowlist = []
        for i,row in enumerate(reader):
            if i == 0:
                pass
            else:
                rowlist.append([row[0],row[1]])
        return rowlist
def importFileOther(path):
    with open(path,newline='') as f:
        reader = csv.reader(f)
        rowlist = []
        for i,row in enumerate(reader):
            if i == 0:
                pass
            else:
                rowlist.append([row[0],row[3]])
        return rowlist


def filterIntoCats(rowList):
    roadcomb = 0
    euccomb = 0
    circuitycomb = 0
    elemCount = 0


    print(rowList[:2])
    for elem in rowList:
        if "RoadData" in elem[0]:
            roadcomb += float(elem[1])
        elif ("CircuityData" in elem[0]):
            circuitycomb += float(elem[1])
        elif ("EuclideanData"in elem[0]):
            print(elem[0])
            euccomb += float(elem[1])
        elemCount +=1
    print(elemCount)
    print(roadcomb)
    print(euccomb)
    print(circuitycomb)

            
def filterIntoCatsOther(rowList):
    roadcomb = 0
    euccomb = 0
    circuitycomb = 0
    elemCount = 0


    inpCheck = {}
    for elem in rowList:
        filename = elem[0]
        match = re.search(r"ID(\d+)", filename)
        id_num = match.group(1)
        inpCheck.setdefault(id_num, 0)
        inpCheck[id_num] += 1
        if "RoadData" in elem[0]:
            roadcomb += float(elem[1])
        elif ("CombinedData" in elem[0]):
            circuitycomb += float(elem[1])
        elif ("EuclideanData"in elem[0]):
            euccomb += float(elem[1])
        elemCount +=1
    elemCountAdj = elemCount/8
    print(elemCountAdj)
    roadcombAvg = (roadcomb/(elemCountAdj*6))
    euccombAvg = (euccomb/(elemCountAdj*2))
    combcombAvg = (circuitycomb/(elemCountAdj*8))
    print(roadcombAvg)
    print(euccombAvg)
    print(combcombAvg)
    print(combcombAvg/euccombAvg)

 


if __name__ == "__main__":
    #importFile("Total_Route_Lengths_Munich_1000x100_circuityFactor_Demand1_Cap10_filtered.csv")
    rowlist = importFile("Total_Route_Lengths_Munich_1000x100_circuityFactor_Demand1_Cap10_filtered.csv")
    filterIntoCats(rowlist)