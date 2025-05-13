
import graph_model
from ProblemDataGenerator import ProblemDataGenerator
import pyvrp
from pyvrp import Model
from pyvrp.stop import MaxIterations
from flask import jsonify
from create_data_for_api import DataCreator
import runpy
import sys
import os
from shared import setResDict

def run():
    print("REACHED RUN")
    
    numIterations = 1000
    numItInput=int(sys.argv[1])
    if numItInput > 1000:
        numIterations = numItInput

    inputs={
        "dm":"Chicago_100x100_RoadData",
        "X_set":"X-n101-k25",}
    gen = ProblemDataGenerator(inputs["dm"],inputs["X_set"])
    gen.doEverything()

    model = Model.from_data(gen.problemData)
    res = model.solve(stop=MaxIterations(numIterations))
    print("This is the originial version \n")
    print(res)

    DataCreatorObj = DataCreator(res,inputs["dm"],inputs["X_set"])
    resDict = DataCreatorObj.runStatistics()
    setResDict(resDict)
    print(f"END RUN with (setResDict())")

    #very important
    #runpy.run_path("flask_endpoint.py", init_globals={"resDict": resDict})

if __name__ == "__main__":
    print("REACHED MAIN")
    run()


#print("This is the rebuild version!!!!\n\n\n")
#print(DataCreator.build_from_resdict(resDict,gen.problemData))
#resret=DataCreator.import_statistics(inputs["dm"],inputs["X_set"])
#print(resret)


#print("Now res.best")

#print(res.best)
#print("now rest.stats")
#print(res.stats)
#print("now res.num_iterations")
#print(res.num_iterations)
#print("now res.runtime")
#print(res.runtime)

#print(res)


#generator = graph_model.GraphGenerator(gen.X_scenario,gen.instance,model,res)
#generator.genAllGraphs()
# later