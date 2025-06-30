
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
    elemCountAdj = elemCount/8
    roadcombAvg = (roadcomb/(elemCountAdj*8))
    euccombAvg = (euccomb/(elemCountAdj*8))
    combcombAvg = (circuitycomb/(elemCountAdj*8))
    
    improvementRoad = (1-(roadcombAvg/euccombAvg))*100
    improvementCombined = (1-(combcombAvg/euccombAvg))*100

    return [roadcombAvg,euccombAvg,combcombAvg,improvementRoad,improvementCombined]
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
    roadcombAvg = (roadcomb/(elemCountAdj*6))
    euccombAvg = (euccomb/(elemCountAdj*2))
    combcombAvg = (circuitycomb/(elemCountAdj*8))
    
    improvementRoad = (1-(roadcombAvg/euccombAvg))*100
    improvementCombined = (1-(combcombAvg/euccombAvg))*100

    return [roadcombAvg,euccombAvg,combcombAvg,improvementRoad,improvementCombined]
    print(roadcombAvg)
    print(euccombAvg)
    print(combcombAvg)
    print(combcombAvg/euccombAvg)

def transform2col(path):

    header = ["Case","AVG RoadLength","AVG Ec2dLength","AVG Ec2DWithRealDepotLength","AVG Road Improvement (%)","AVG Ec2dWithRealDepot Improvement (%)"]
    with open("Result2col.csv",mode="w",newline='') as f1:
        writer = csv.writer(f1)
        writer.writerow(header)
    for dir in os.listdir(path):
        if dir.endswith(".csv"):
            filepath = os.path.join(path,dir)
            rowlist = importFile(filepath)
            avgList = filterIntoCatsOther(rowlist)
            c1 = dir.removeprefix("Total_Route_Lengths_Munich_")
            c2 = c1.removesuffix(".csv")
            row = [c2] + avgList
            with open(f"Result2col.csv",mode="a",newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)
        else:
            pass
def importPercent(path):
    with open(path,newline='') as f:
        reader = csv.reader(f)
        rowlist = []
        for i,row in enumerate(reader):
            if i == 0:
                pass
            else:
                rowlist.append([row[0],row[1]])
        return rowlist
def givePercentRow(rowlist):
    percentList = ['5Percent', '10Percent', '15Percent', '20Percent', '25Percent',
                    '30Percent', '35Percent', '40Percent', '45Percent', '50Percent']

    combDict = {}
    counter = 0
    for ent in rowlist:
        if "RealSample" in ent[0]:
            combDict.setdefault("RealSample", 0)
            combDict["RealSample"] += float(ent[1])
        elif "h5Percent" in ent[0]:
            combDict.setdefault("h5Percent", 0)
            combDict["h5Percent"] += float(ent[1])
        elif "10Percent" in ent[0]:
            combDict.setdefault("10Percent", 0)
            combDict["10Percent"] += float(ent[1])
        elif "15Percent" in ent[0]:
            combDict.setdefault("15Percent", 0)
            combDict["15Percent"] += float(ent[1])
        elif "20Percent" in ent[0]:
            combDict.setdefault("20Percent", 0)
            combDict["20Percent"] += float(ent[1])
        elif "25Percent" in ent[0]:
            combDict.setdefault("25Percent", 0)
            combDict["25Percent"] += float(ent[1])
        elif "30Percent" in ent[0]:
            combDict.setdefault("30Percent", 0)
            combDict["30Percent"] += float(ent[1])
        elif "35Percent" in ent[0]:
            combDict.setdefault("35Percent", 0)
            combDict["35Percent"] += float(ent[1])
        elif "40Percent" in ent[0]:
            combDict.setdefault("40Percent", 0)
            combDict["40Percent"] += float(ent[1])
        elif "45Percent" in ent[0]:
            combDict.setdefault("45Percent", 0)
            combDict["45Percent"] += float(ent[1])
        elif "50Percent" in ent[0]:
            combDict.setdefault("50Percent", 0)
            combDict["50Percent"] += float(ent[1])
        elif "Ec2dWithRealDepotSampleMunich" in ent[0]:
            combDict.setdefault("Ec2dWithRealDepotSampleMunich", 0)
            combDict["Ec2dWithRealDepotSampleMunich"] += float(ent[1])
        elif "100Ec2dSampleMunichSpecial" in ent[0]:
            combDict.setdefault("100Ec2dSampleMunichSpecial", 0)
            combDict["100Ec2dSampleMunichSpecial"] += float(ent[1])
        counter += 1
    print(counter)
    rowlist = []
    for elem in combDict:
        combDict[elem] = combDict[elem]/800
    for el in combDict:
        rowlist.append([el,combDict[el],1-(combDict[el]/combDict["100Ec2dSampleMunichSpecial"])])
    return rowlist

 


def transformPercent(path):

    header = ["Case","AVG","Improvement to Ec2d (%)"]
    with open("ResultsPercentCase.csv",mode="w",newline='') as f1:
        writer = csv.writer(f1)
        writer.writerow(header)
    for dir in os.listdir(path):
        if dir.endswith(".csv"):
            filepath = os.path.join(path,dir)
            rowlist = importPercent(filepath)
            rowNumbers = givePercentRow(rowlist)
            print(rowNumbers)
            with open("ResultsPercentCase.csv",mode="a",newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rowNumbers)


    
    



 


if __name__ == "__main__":
    #importFile("Total_Route_Lengths_Munich_1000x100_circuityFactor_Demand1_Cap10_filtered.csv")
    #rowlist = importFile("allCsv/2col/Total_Route_Lengths_Munich_1000x100_circuityFactor_Demand1_Cap10.csv")
    #print(filterIntoCats(rowlist))
    #transform2col("allCsv/2col")
    transformPercent("allCsv/2col/percentCase/")
