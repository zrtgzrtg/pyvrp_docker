
import zipfile
import json
import rapidjson
import os
import numpy as np
from data.city_matrices import city_matrices,city_sizes,city_matrices_TESTING,city_sizes_TESTING
from Swapper import Swapper



class Sampler():
    def __init__(self,city,sampleSize,isRealDM,saveName):
        self.realDM = city_matrices_TESTING[city][0]
        self.ec2dDM = city_matrices_TESTING[city][1]
        self.citySize = city_sizes_TESTING[city]
        self.sampleSize = sampleSize
        self.isRealDM = isRealDM
        self.saveName = saveName

    def sampleXamountID(self,x):
        rng = np.random.default_rng()
        ids = np.arange(2,self.citySize+1)
        sampled_ids_numpy = rng.choice(ids,size=x,replace=False)
        sampled_ids = sampled_ids_numpy.tolist()
        sampled_ids_set = set(sampled_ids)
        sampled_ids_set.add(1)
        return sampled_ids_set
    
    def findAllEntriesFromSampledID(self,sample_set,isRealDM):
        if isRealDM:
            s = Swapper(self.realDM)
        else:
            s = Swapper(self.ec2dDM)
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
        partnerSet = s.findRenameForIDS(sample_set)
        print(partnerSet)
        entries = self.findAllEntriesFromSampledID(sample_set,self.isRealDM)
        # python mutating original values in place. This is workaround dont change order!
        varOrgEntries = "OrgEntries.json"
        s.saveXFile(entries,dirpath,varOrgEntries)

        UsableDM = self.mutateSampledDMToUsableDM(entries,partnerSet)
        s.testSampledDM(UsableDM,os.path.join(dirpath,varOrgEntries),partnerSet)

        s.saveXFile(list(sample_set),dirpath,"ChosenIDs.json")
        partnerSetSaveable = {}
        for k,v in partnerSet.items():
            partnerSetSaveable[str(k)] = v
        s.saveXFile(partnerSetSaveable,dirpath,"PartnerIDS.json")
        s.saveXFile(UsableDM,dirpath,"NewSampledDM.json")
        
        self.zipAll(dirpath,self.saveName)

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
            




    
        
    





if __name__ == "__main__":
    s = Sampler("Munich1747",99,True,"100SampleMunichEc2d")
    s.saveAllToZip()

