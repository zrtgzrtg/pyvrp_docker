
import graph_model
from ProblemDataGenerator import ProblemDataGenerator
import pyvrp
from pyvrp import Model
from pyvrp.stop import MaxIterations

gen = ProblemDataGenerator("A","Synthetic_Full_OD_CostMatrix","X-n101-k25",99)
gen.doEverything()

model = Model.from_data(gen.problemData)
res = model.solve(stop=MaxIterations(30000))

print(res)


#generator = graph_model.GraphGenerator(gen.X_scenario,gen.instance,model,res)
#generator.genAllGraphs()
# later