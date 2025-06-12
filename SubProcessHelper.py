
from pyvrp import Model,Result,ProblemData


def figureRuntime(model: Model):
    numClients = model.data().num_locations
    return numClients*13
    