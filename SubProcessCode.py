
from shared import setResDictThread
from create_data_for_api import DataCreator
from ProblemDataGenerator import ProblemDataGenerator
import time
from pyvrp import Model
import sys,json
from pyvrp.stop import MaxIterations
from Grapher import Grapher
from SubProcessHelper import figureRuntime

def main():
    #Structure of args
    #inputDict = {
    #        "modelType": self.modelType,
    #        "dm":self.inputs["dm"], DONT USE IN THREAD IMPLEMENTATION
    #        "X_set":self.inputs["X_Set"],
    #        "numClients":self.inputs["numClients"],
    #        "numIterations":self.numIterations,
    #        "ID":self.ID
    #        "RealDMname":self.RealDMname,
    #        "Ec2DDMname":self.Ec2DDMname
    #    }
    args = json.loads(sys.argv[1])
    print(f"Subprocess main method of SubProcessTask with ID: {args['ID']} reached. Model Type: {args['modelType']}\n")
    if args["modelType"] == "RealDM":
        gen = ProblemDataGenerator(args["RealDMname"],args["X_set"],args["numClients"])
        usedName = args["RealDMname"]

    else:
        gen = ProblemDataGenerator(args["Ec2DDMname"],args["X_set"],args["numClients"])
        usedName = args["Ec2DDMname"]
    
    collectStats = bool(args["collectStats"])

    
    problemData = gen.getProblemData()
    model = Model.from_data(problemData)
    if bool(args["autoIterations"]) == True:
        args["numIterations"] = figureRuntime(model)



    # nanoseconds since 1970 modulo max integer size
    timeseed = time.time_ns() % (2**32)
    res = model.solve(stop=MaxIterations(args["numIterations"])
                      ,seed=timeseed,collect_stats=collectStats)
    
    
    # graphs are hard!
    #g = Grapher(problemData,res,f"IPC/Graphs/ID_{timeseed}")
    #g.createGraphs()
    # if statement already determined gen based on modelType. Now calling gen for the right dm-name
    dataC = DataCreator(res,usedName,args["X_set"],args["ID"],timeseed)
    resDict = dataC.runStatistics(collectStats)
    setResDictThread(resDict,args["ID"])


if __name__=="__main__":
    main()
