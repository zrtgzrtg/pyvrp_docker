
import graph_model
from ProblemDataGenerator import ProblemDataGenerator
import pyvrp
from pyvrp import Model
from pyvrp.stop import MaxIterations
from flask import jsonify
from create_data_for_api import DataCreator
import runpy

inputs={
    "dm":"Chicago_100x100_RoadData",
    "X_set":"X-n101-k25",}
gen = ProblemDataGenerator(inputs["dm"],inputs["X_set"])
gen.doEverything()

model = Model.from_data(gen.problemData)
res = model.solve(stop=MaxIterations(1000))
print("This is the originial version \n")
print(res)

DataCreator = DataCreator(res,inputs["dm"],inputs["X_set"])
resDict = DataCreator.runStatistics()
runpy.run_path("flask_endpoint.py", init_globals={"resDict": resDict})


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