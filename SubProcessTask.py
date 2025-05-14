import subprocess
from pyvrp import Model
from pyvrp.stop import MaxIterations,MaxRuntime
from pyvrp import RandomNumberGenerator

# DONT FORGET to implement different seeds
class SubProcessTask():
    def __init__(self,model,inputs):
        self.model = model
        self.inputs = inputs
    
    def start(self):
        #implement start logic here with open logfile, random seed and resDict implementation
        # f = open(logfile)
        # p = subprocess.Popen()
        # return p,f

        print("NOT implemented")
