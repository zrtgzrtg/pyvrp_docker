 
import os
import matplotlib.pyplot as plt
from pyvrp.plotting import (
    plot_coordinates,
    plot_instance,
    plot_result,
    plot_route_schedule,
)

class GraphGenerator:
    def __init__(self,modelName,INSTANCE,model,modelSolution):
        self.modelName = modelName
        self.INSTANCE = INSTANCE
        self.model = model
        self.modelSolution = modelSolution

        os.makedirs(self.modelName, exist_ok=True)

    def genGraphLocation(self):
        fig, ax = plt.subplots(figsize=(8, 8))
        plot_coordinates(self.INSTANCE, ax=ax)
        plt.tight_layout()
        ProblemLocationsName = "Locations.png"
        filepath = os.path.join(self.modelName, f"{ProblemLocationsName}")
        plt.savefig(filepath, dpi=300,bbox_inches="tight")
        plt.close(fig)
        print(f"Locations saves as {ProblemLocationsName} under {filepath}")
 

    def genGraphSolution(self):
        fig = plt.figure(figsize=(15, 9))
        plot_result(self.modelSolution, self.INSTANCE, fig)
        fig.tight_layout()
        ProblemSolutionName="Solution.png"
        filepath = os.path.join(self.modelName, f"{ProblemSolutionName}")
        plt.savefig(filepath, dpi=300,bbox_inches="tight")
        plt.close(fig)
        print(f"Solution saved as {ProblemSolutionName} under {filepath}")

    def genAllGraphs(self):
        self.genGraphLocation()
        self.genGraphSolution()
 