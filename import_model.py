from pyvrp import Model,read

def createInstance(name):
    Instance = read(f"data/Vrp-Set-X/X/{name}.vrp",round_func="round")
    return Instance
