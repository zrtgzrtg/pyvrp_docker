
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
    def __init__(self,problemData,result,dirpath="Plottest"):
        self.problemData = problemData
        self.result = result
        self.dirpath = dirpath
        os.makedirs(self.dirpath,exist_ok=True)
    
    def createGraphs(self):
        # run createGraphs to fullfill everything in this class

        plots = [
            ("demands", lambda: plot_demands(self.problemData)),
            ("diversity", lambda: plot_diversity(self.result)),
            ("objectives", lambda: plot_objectives(self.result)),
            ("runtimes", lambda: plot_runtimes(self.result)),
        ]

        for name, plot_func in plots:
            self.genGraphSolution(name,plot_func)

    def genGraphSolution(self,name,plot_func):
        fig = plt.figure(figsize=(15, 9))
        plot_func()
        fig.tight_layout()
        filepath = f"{os.path.join(self.dirpath,name)}.png"
        plt.savefig(filepath, dpi=300,bbox_inches="tight")
        plt.close(fig)

        # works:
        # plot_demands
        # plot_diversity
        # plot_result
        # works but useless:
        # plot_instance
        # plot_results





#if __name__ == "__main__":
    #zipName = "abcde"
    #importAndSaveToDB(zipName)
    #inputsHTML, SortedRealDMlist, SortedEc2Dlist, zipName = loadPickleBackup("abcde",0,0)
    #writeResFile(inputsHTML,SortedRealDMlist,SortedEc2Dlist,zipName)

    #pg = ProblemDataGenerator("100SampleMunichRealDM","X-n101-k25",99)
    #pd = pg.getProblemData()
    #model = Model.from_data(pd)
    #res = model.solve(stop=MaxIterations(1000))
    #g = Grapher(pd,res,"Plottest")
    #g.createGraphs()

       


    

    #for i, res in enumerate(SortedRealDMlist):
    #    g = Grapher(pdReal,res,i)
    #    g.createGraphs()
    #for idx, res in enumerate(SortedEc2Dlist,start=4):
    #    g = Grapher(pdEc2d,res,idx)
    #    g.createGraphs()




   

