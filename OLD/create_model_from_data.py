from pyvrp.stop import MaxIterations, MaxRuntime
from pyvrp import Model,read

def createModel(Instance):
    model = Model.from_data(Instance)
    return model