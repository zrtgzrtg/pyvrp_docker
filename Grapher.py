
from pyvrp.stop import MaxIterations
from pyvrp import Model,solve
from ProblemDataGenerator import ProblemDataGenerator
import matplotlib.pyplot as plt
from rebuild_res import loadPickleBackup,importAndSaveToDB,writeResFile,Res_Builder_Factory
import os
from pyvrp.plotting import (
    plot_coordinates,
    plot_demands,
    plot_diversity,
    plot_instance,
    plot_objectives,
    plot_result,
    plot_route_schedule,
    plot_runtimes,
    plot_solution
)

class Grapher():
    def __init__(self,problemData,result,uniqueID,dirpath="Plottest"):
        self.problemData = problemData
        self.result = result
        self.uniqueID = str(uniqueID)
        self.dirpath = dirpath
        os.makedirs(self.dirpath,exist_ok=True)
    
    def createGraphs(self):
        solution = self.result.best

        plots = [
            ("coordinates", lambda: plot_coordinates(self.problemData)),
            ("demands", lambda: plot_demands(self.problemData)),
            ("instance", lambda: plot_instance(self.problemData)),
            ("solution", lambda: plot_solution(self.problemData, solution)),
            ("route_schedule", lambda: plot_route_schedule(self.problemData, solution)),
            ("diversity", lambda: plot_diversity(self.result)),
            ("objectives", lambda: plot_objectives(self.result)),
            ("result", lambda: plot_result(self.result,self.problemData)),
            ("runtimes", lambda: plot_runtimes(self.result)),
        ]

        for name, plot_func in plots:
            try:
                fig, ax = plot_func()
                fig.savefig(os.path.join(self.dirpath, f"{name}{self.uniqueID}.png"))
                plt.close(fig)
                print(f"Saved {name}{self.uniqueID} plot to {os.path.join(self.dirpath, f'{name}{self.uniqueID}.png')}")
            except Exception as e:
                print(f"Could not create/save {name}{self.uniqueID}: {e}") 

    def genGraphSolution(self):
        fig = plt.figure(figsize=(15, 9))
        plot_result(self.result, self.problemData, fig)
        fig.tight_layout()
        ProblemSolutionName=f"Solution{self.uniqueID}.png"
        filepath = f"{os.path.join(self.dirpath,str(self.uniqueID))}.png"
        plt.savefig(filepath, dpi=300,bbox_inches="tight")
        plt.close(fig)
        print(f"Solution saved as {ProblemSolutionName} under {filepath}")



if __name__ == "__main__":
    #zipName = "abcde"
    #importAndSaveToDB(zipName)
    #inputsHTML, SortedRealDMlist, SortedEc2Dlist, zipName = loadPickleBackup("abcde",0,0)
    #writeResFile(inputsHTML,SortedRealDMlist,SortedEc2Dlist,zipName)

    pg = ProblemDataGenerator("100SampleMunichRealDM","X-n101-k25",99)
    pd = pg.getProblemData()
    model = Model.from_data(pd)
    print(pd.location())
    res = model.solve(stop=MaxIterations(2000))
    g = Grapher(pd,res,0)
    g.genGraphSolution()

       

    

    #for i, res in enumerate(SortedRealDMlist):
    #    g = Grapher(pdReal,res,i)
    #    g.createGraphs()
    #for idx, res in enumerate(SortedEc2Dlist,start=4):
    #    g = Grapher(pdEc2d,res,idx)
    #    g.createGraphs()




   

