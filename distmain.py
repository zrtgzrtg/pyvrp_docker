
from ProblemDataGenerator import ProblemDataGenerator
from pyvrp import Model
from pyvrp.stop import MaxIterations
from create_data_for_api import DataCreator
import sys
from shared import setResDict
from Process_Starter import Subprocess_Starter

def run():
    print("REACHED RUN")
    
    numIterations = 500
    numItInput=int(sys.argv[1])
    if numItInput > 500:
        numIterations = numItInput

    inputs={
        "dm":"Chicago_100x100_RoadData", # THIS IS NOT USED ANYMORE!!!! DONT DELETE IT THO
        "X_set":"X-n101-k25",
        "numClients":"99"
        }
        # DebugCapacity is set to 10 standard and debugBoolean has standard value False
    subprocessstarter = Subprocess_Starter("Chicago_100x100_RoadData","Chicago_100x100_EuclideanData",inputs,2,1,1,numIterations,debugBOOLEAN=True,debugCapacity=10)
    subprocessstarter.doEverything()
    # OLD DISTMAIN.py
    #gen = ProblemDataGenerator(inputs["dm"],inputs["X_set"],inputs["numClients"])

    #model = Model.from_data(gen.getProblemData())
    #res = model.solve(stop=MaxIterations(numIterations))
    #print("This is the originial version \n")
    #print(res)

    #DataCreatorObj = DataCreator(res,inputs["dm"],inputs["X_set"],inputs)
    #resDict = DataCreatorObj.runStatistics()
    #setResDict(resDict)
    #print(f"END RUN with (setResDict())")

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