
import json
from ProblemDataGenerator import ProblemDataGenerator
from pyvrp import Model
from pyvrp.stop import MaxIterations
from create_data_for_api import DataCreator
import sys
from Process_Starter import Subprocess_Starter
from data.city_matrices import city_matrices

def run():
    print("REACHED RUN")

    inputsHTMLstr = sys.argv[1]
    inputsHTML = json.loads(inputsHTMLstr)
    
    numIterations = 500
    numItInput=int(inputsHTML["numIterations"])
    if numItInput > 500:
        numIterations = numItInput
    realDM, Ec2DDM = city_matrices[inputsHTML["city"]]
    vrp_file = inputsHTML["vrp-file"]
    numClients = inputsHTML["numClients"]
    numThreads = inputsHTML["numThreads"]
    numRealDM = inputsHTML["numRealDM"]
    numEc2D = inputsHTML["numEc2D"]
    debugCapacity = inputsHTML["debugCapacity"]
    isDebugRun = inputsHTML["isDebugRun"]
    
    if isDebugRun:
        with open("data/Vrp-Set-X/X/debug.vrp", "r") as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("CAPACITY"):
                lines[i] = f"CAPACITY : {debugCapacity}\n"
                break
        with open("data/Vrp-Set-X/X/debug.vrp", "w") as f2:
            f2.writelines(lines)
    else:
        pass

    inputs={
        "dm":"placeholder", # THIS IS NOT USED ANYMORE!!!! DONT DELETE IT THO
        "X_set":vrp_file, # Instead of debug boolean assign debug.vrp here
        "numClients": numClients
        }
    subprocessstarter = Subprocess_Starter(realDM,Ec2DDM,inputs,numThreads,numEc2D,numRealDM,numIterations)
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