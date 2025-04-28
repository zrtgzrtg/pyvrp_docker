import create_model_from_data
import os
import import_model 
import solveModel
import graph_model

data_dir = "./data/Vrp-Set-X/X"
numIterations = 2000

while True:
    modelDataInput = input("Which scenario would you like to run?")
    
    filename = f"{modelDataInput}.vrp"
    
    filepath = os.path.join(data_dir, filename)
    print(filepath)
    
    if os.path.isfile(filepath):
        print(f"Valid .vrp File!")
        numIterationsInput = int(input(f"How many Iterations would you like?"))
        if numIterationsInput>1:
           numIterations=numIterationsInput
        break
    else:
        print(f"Not Valid! Retry")




modelData = modelDataInput

Instance = import_model.createInstance(modelData)

model = create_model_from_data.createModel(Instance)

res = solveModel.solveModel(model,numIterations)
print(res)

generator = graph_model.GraphGenerator(modelData,Instance,model,res)
generator.genAllGraphs()

#27591

print("FINISHED")