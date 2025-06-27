
from Finder import Finder
import zipfile
import json
import rapidjson
import os
import numpy as np
from data.city_matrices import city_matrices,city_sizes,city_matrices_TESTING,city_sizes_TESTING
from Swapper import Swapper



class Sampler():
    def __init__(self,city,sampleSize,isRealDM,saveName,specialDM=None,idSet=None,partnerSet=None):
        self.realDM = city_matrices[city][0]
        self.ec2dDM = city_matrices[city][1]
        self.citySize = city_sizes[city]
        self.sampleSize = sampleSize
        self.isRealDM = isRealDM
        self.saveName = saveName
        self.specialDM = city_matrices[specialDM][0]
        self.idSet = idSet
        self.partnerSet = partnerSet
        self.specialDMNames = {
            3:   "Munich5PercentForRoad",
            4:  "Munich10PercentForRoad",
            5:  "Munich15PercentForRoad",
            6:  "Munich20PercentForRoad",
            7:  "Munich25PercentForRoad",
            8:  "Munich30PercentForRoad",
            9:  "Munich35PercentForRoad",
            10: "Munich40PercentForRoad",
            11: "Munich45PercentForRoad",
            12: "Munich50PercentForRoad"
        }
        self.swapperDict = {}




    def sampleXamountID(self,x):
        rng = np.random.default_rng()
        ids = np.arange(2,self.citySize+1)
        sampled_ids_numpy = rng.choice(ids,size=x,replace=False)
        sampled_ids = sampled_ids_numpy.tolist()
        sampled_ids_set = set(sampled_ids)
        sampled_ids_set.add(1)
        return sampled_ids_set
    
    def findAllEntriesFromSampledID(self,sample_set,isRealDM):
        if self.swapperDict.get(isRealDM):
            s = self.swapperDict[isRealDM]
        else:
            if isRealDM == 1:
                s = Swapper(self.realDM)
            elif (isRealDM==0):
                s = Swapper(self.ec2dDM)
            elif(isRealDM==2):
                s = Swapper(self.specialDM)
            elif(isRealDM in self.specialDMNames):
                s = Swapper(self.specialDMNames[isRealDM])
            elif(isRealDM==13):
                s = Swapper(self.ec2dDM)
            self.swapperDict[isRealDM] = s
        idSet = sample_set
        print(f"idSet {idSet}")
        return s.retAllEntriesForSubset(idSet)
    
    def saveToFile(self,allEntries,dirpath):
        with open (f"{dirpath}.json","w") as f:
            rapidjson.dump(allEntries,f,indent=4)
        old_path = f"{dirpath}.json"
        dirname = os.path.dirname(old_path)
        basename = os.path.basename(old_path)
        os.makedirs(f"{dirpath}/{self.saveName}",exist_ok=True)

        
        new_path = os.path.join(dirpath, self.saveName,f"OrgIDS_{basename}")
        os.rename(old_path,new_path)
    
    def saveIDSet(self,dirpath,idSet):
        with open(f"{dirpath}.txt", "w") as f:
            rapidjson.dump(idSet,f)
        old_path = f"{dirpath}.txt"
        dirname = os.path.dirname(old_path)
        basename = os.path.basename(old_path)
        
        new_path = os.path.join(dirpath,self.saveName, f"OrgIDS_{basename}")
        os.rename(old_path,new_path)
    
    def saveXFile(self,X,path,name):
        with open(os.path.join(path,name), "w") as f:
            rapidjson.dump(X,f,indent=4)

    
    
    def findRenameForIDS(self,idSet):
        renameDict = {}
        renameDict[1] = 1
        idSet.remove(1)
        for i,id in enumerate(idSet,start=2):
            renameDict[id] = i
        # For some crazy javascript type reason python mutates the original IdSet in remove
        idSet.add(1)
        # converting numpy ints into normal json serializable ints
        #renameDict = {int(k): int(v) for k, v in renameDict.items()}
        os.makedirs("samplerHelpDir",exist_ok=True)

        with open("samplerHelpDir/partnerIDS","w") as f:
            json.dump(renameDict,f,indent=4)
        return renameDict
    
    def mutateSampledDMToUsableDM(self,entries,partnerSet):
        res = entries
        for entry in res:
            entry["OriginID"] = partnerSet[entry["OriginID"]]
            entry["DestinationID"] = partnerSet[entry["DestinationID"]]
        sorted_dm = sorted(res, key=lambda x: (x["OriginID"], x["DestinationID"]))
        return sorted_dm
    
    def rebuildDMasTupleDict(self,pathToDM):
        with open(pathToDM,"r") as f:
            data = rapidjson.load(f)
        tupleDict = {}
        for entry in data:
            tuple = (entry["OriginID"],entry["DestinationID"])
            tupleDict[tuple] = entry["Total_Length"]
        return tupleDict
    
    def reversePartnerSetDeepCopy(self,partner_set):
        res = {}
        for k,v in partner_set.items():
            res[v] = k
        return res


    
    def testSampledDM(self,new_dm,pathOldDM,partner_set):
        tupleDict = self.rebuildDMasTupleDict(pathOldDM)
        # needs to map back to original keys with deep copy of partner set
        reversePartnerSet = self.reversePartnerSetDeepCopy(partner_set)
        for entry in new_dm:
            valNew = entry["Total_Length"]
            tupleKey = (reversePartnerSet[entry["OriginID"]], reversePartnerSet[entry["DestinationID"]])
            valOld = tupleDict[tupleKey]
            assert valNew == valOld, f"Failed at tuple: {tupleKey} for entry Origin: {entry['OriginID']} and entry DestinationID: {entry['DestinationID']}"
        print("ALL TEST HAVE PASSED !!!! \n")

        




    def saveAllToZip(self):
        dir = "samplerResDir"
        os.makedirs(dir,exist_ok=True)
        os.makedirs(f"{dir}/{self.saveName}",exist_ok=True)
        dirpath = os.path.join(dir,self.saveName)


       

        sample_set = self.sampleXamountID(self.sampleSize)
        partnerSet = self.findRenameForIDS(sample_set)
        print(partnerSet)
        entries = self.findAllEntriesFromSampledID(sample_set,self.isRealDM)
        # python mutating original values in place. This is workaround dont change order!
        varOrgEntries = "OrgEntries.json"
        self.saveXFile(entries,dirpath,varOrgEntries)

        UsableDM = self.mutateSampledDMToUsableDM(entries,partnerSet)
        self.testSampledDM(UsableDM,os.path.join(dirpath,varOrgEntries),partnerSet)

        self.saveXFile(list(sample_set),dirpath,"ChosenIDs.json")
        partnerSetSaveable = {}
        for k,v in partnerSet.items():
            partnerSetSaveable[str(k)] = v
        self.saveXFile(partnerSetSaveable,dirpath,"PartnerIDS.json")
        self.saveXFile(UsableDM,dirpath,"NewSampledDM.json")
        
        self.zipAll(dirpath,self.saveName)

        # N*10 = 100 --> 1000 1000 --> 10000 --> 

        #self.saveToFile(entries,dirpath)
        #self.saveIDSet(dirpath,list(idSet))
    
    def zipAll(self,dirpath,zipname):
        zip_path = os.path.join(dirpath,f"{zipname}.zip")

        with zipfile.ZipFile(zip_path,"w", zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(dirpath):
                full_path = os.path.join(dirpath,file)

                if full_path == zip_path:
                    continue
                else:
                    zipf.write(full_path,arcname=file)
        
        for file in os.listdir(dirpath):
            full_path = os.path.join(dirpath,file)
            if full_path != zip_path and os.path.isfile(full_path):
                os.remove(full_path)

    def setupSampleAll3DMs(self):
        self.idSet = self.sampleXamountID(self.sampleSize)
        self.partnerSet = self.findRenameForIDS(self.idSet)
        print(self.idSet)
        print(self.partnerSet)
        print(self.specialDM)

    def setupSampleAll3DMsWithFinder(self,numOfIDSwaps):
        f = Finder(self.realDM,self.ec2dDM)
        Ids,tuples = f.findBiggestDifference(numOfIDSwaps)
        self.idSet = set(Ids)
        self.partnerSet = self.findRenameForIDS(self.idSet)
        print(self.idSet)
        print(self.partnerSet)
        print(self.specialDM)


    def sampleAll3DMs(self,id=None):
        dir = "samplerResDir"
        os.makedirs(dir,exist_ok=True)
        os.makedirs(f"{dir}/{self.saveName}",exist_ok=True)
        dirpath = os.path.join(dir,self.saveName)
        if self.idSet == None or self.partnerSet == None or self.specialDM== None:
            raise AssertionError(f"generate necessary stuff first! specialDM = {self.specialDM}")
        
        percent_labels = {
        3: "5Percent", 4: "10Percent", 5: "15Percent", 6: "20Percent",
        7: "25Percent", 8: "30Percent", 9: "35Percent", 10: "40Percent",
        11: "45Percent", 12: "50Percent"
        }
        
        for x in range(14):
            with open("samplerHelpDir/partnerIDS", "r") as f1:
                partnerSet_str = json.load(f1)
                sample_set_str = list(partnerSet_str.keys())

                sample_set = []
                for d in sample_set_str:
                    sample_set.append(int(d))
                partnerSet = {int(k): v for k,v in partnerSet_str.items()}

                entries = self.findAllEntriesFromSampledID(sample_set,x)
                varOrgEntries = f"OrgEntries{x}.json"
                self.saveXFile(entries,dirpath,varOrgEntries)
                UsableDM = self.mutateSampledDMToUsableDM(entries,partnerSet)
                self.testSampledDM(UsableDM,os.path.join(dirpath,varOrgEntries),partnerSet)
                if x == 0:
                    name = f"{self.sampleSize+1}Ec2dSampleMunich.json"
                elif(x==1):
                    name = f"{self.sampleSize+1}RealSampleMunich.json"
                elif(x==2):
                    name = f"{self.sampleSize+1}Ec2dWithRealDepotSampleMunich.json"
                elif x in percent_labels:
                    name = f"{self.sampleSize+1}Munich{percent_labels[x]}ForRoad.json"
                elif(x==13):
                    name = f"{self.sampleSize+1}Ec2dSampleMunichSpecial.json"

                

                self.saveXFile(UsableDM,dirpath,name)
        os.rename("samplerHelpDir/partnerIDS",f"{dirpath}/partnerIDS.json")

        if id is None:
            self.zipAll(dirpath,f"{self.sampleSize+1}allMunichSampleDMS")
        else : 
            self.zipAll(dirpath,f"{self.sampleSize+1}MunichSamples_ID{id}")

        


        

        
        




    
        
    





if __name__ == "__main__":
    #this is original
    # 1 is for realdm
    # 0 is for ec2dm
    # 2 is for specialdm
    
    #s = Sampler("Munich1747",99,0,"AllMunichSampleDMs","Munich1747Ec2dRealDepot")
    #s.setupSampleAll3DMs()
    #s.sampleAll3DMs()

    #s = Sampler("Munich1747",99,1,"100SampleMunichEc2d")
    #s.saveAllToZip()

    # This is how i got the distance matrices
    #for i in range(10):
    #    x = i*100 + 99
    #    y = f"{x+1}allMunichSampleDMS"

    #    s = Sampler("Munich1747",x,0,y,"Munich1747Ec2dRealDepot")
    #    s.setupSampleAll3DMs()
    #    s.sampleAll3DMs()
    #    os.makedirs("SamplesUSED",exist_ok=True)
    #    src = f"samplerResDir/{y}"
    #    dst = f"SamplesUSED/{y}"
    #    os.rename(src,dst)

    
    #s = Sampler("Munich1747",100,0,"test1")
    #s.setupSampleAll3DMsWithFinder(10)

    for i in range(100):
        x = 199
        y = f"{x+1}MunichSampleDMS_ID{i}"

        s = Sampler("Munich1747",x,0,y,"Munich1747Ec2dRealDepot")
        s.setupSampleAll3DMs()
        s.sampleAll3DMs(i)
        os.makedirs("SamplesUSED",exist_ok=True)
        src = f"samplerResDir/{y}"
        name = "100x200MunichWithPercent"
        os.makedirs(f"SamplesUSED/{name}",exist_ok=True)
        dst = f"SamplesUSED/{name}/{y}"
        os.rename(src,dst)

    