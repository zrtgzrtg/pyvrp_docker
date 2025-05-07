from pyvrp.stop import MaxIterations, MaxRuntime

def solveModel(model,numIterations):
    result = model.solve(stop=MaxIterations(numIterations),seed=42,display=True)
    return result
    