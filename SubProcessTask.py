import subprocess
import os
import json
from pyvrp import Model
from pyvrp.stop import MaxIterations,MaxRuntime
from pyvrp import RandomNumberGenerator
from pyvrp.stop import MaxIterations
import time

# DONT FORGET to implement different seeds
class SubProcessTask():
    def __init__(self,modelType,inputs,numIterations,ID,RealDMname,Ec2DDMname,collectStats,autoIterations):
        self.modelType = modelType
        self.inputs = inputs
        self.numIterations = numIterations
        self.ID = ID
        self.RealDMname = RealDMname
        self.Ec2DDMname = Ec2DDMname
        self.collectStats = collectStats
        self.autoIterations = autoIterations
    
    def start(self):
        #implement start logic here with open logfile, random seed and resDict implementation
        # f = open(logfile)
        # p = subprocess.Popen()
        # return p,f
        if self.modelType not in ["RealDM","Ec2D"]:
            raise ValueError(f"modelType wrong in ID: {self.ID}! Needs to be RealDM or Ec2D")

        log_path = os.path.join("runLogs",f"solver_{self.ID}.log")
        fileDesc = open(log_path, "a")
        fileDesc.write(f"Startmethod of ID: {self.ID} reached successfully! \n")

        inputDict = {
            "modelType": self.modelType,
            "dm":self.inputs["dm"],
            "X_set":self.inputs["X_set"],
            "numClients":self.inputs["numClients"],
            "numIterations":self.numIterations,
            "ID":self.ID,
            "RealDMname":self.RealDMname,
            "Ec2DDMname":self.Ec2DDMname,
            "collectStats": self.collectStats,
            "autoIterations": self.autoIterations
        }
        inputDictjson = json.dumps(inputDict)

        process = subprocess.Popen(
            ["python3", "SubProcessCode.py",inputDictjson],
            stdout=fileDesc,
            stderr=fileDesc
        )
        return process,fileDesc
