
import io
from pyvrp import Result,Statistics,Solution
import contextlib
import pandas as pd
import os
from vrplib import read_instance


class DataCreator():
    def __init__(self,res,dataset,X_set,threadID,seed):
        self.dataset = dataset
        self.X_set = X_set
        self.res = res
        self.threadID = threadID
        self.seed = seed
        
    def getDemandandCapa(self):
        vrp_file_dir = "data/Vrp-Set-X/X"
        x_set_file = os.path.join(vrp_file_dir,f"{self.X_set}.vrp")
        instance = read_instance(x_set_file)
        capa = instance["capacity"]
        demandList = instance["demand"].tolist()
        return capa, demandList




    def runStatistics(self,collectStats=True):
        current_dir = os.path.dirname(__file__)
        location=f"output_from_res"
        filepath=os.path.join(current_dir,location)
        os.makedirs(f"{filepath}", exist_ok=True)

        capa, demandList = self.getDemandandCapa()

        pd_statistics_object = "No Stats collected!"

        if collectStats:
            output_file=os.path.join(filepath,f"{self.dataset}_{self.X_set}_{self.threadID}.csv")
            self.res.stats.to_csv(output_file)
            pd_statistics_object = self.turn_data_to_dict(output_file)


        
        # THIS IS THE STRUCTURE OF RES#DICT
        return {
            "routes": self.get_best_output(),
            "stats": pd_statistics_object,
            "num_iterations": self.res.num_iterations,
            "runtime": self.res.runtime,
            "DMUsedName": self.dataset,
            "X_setUsedName": self.X_set,
            "seed":self.seed,
            "isFeasible":self.res.best.is_feasible(),
            "CapacityUsed": capa,
            "demandsUsed": demandList,
            "distance": self.res.distance()
        }

        
    
    #def import_statistics(self,dataset,X_set):
    #    current_dir=os.path.dirname(__file__)
    #    location=f"output_from_res/{dataset}_{X_set}.csv"
    #    filepath=os.path.join(current_dir,location)
    #    res=Statistics.from_csv(filepath)
    #    return res
    def turn_data_to_dict(self,filepath):
        df=pd.read_csv(filepath)
        return df.to_dict(orient="records")
    
        
    def get_best_output(self):
        solution = self.res.best
        routes = solution.routes()

        normalized_routes = []

        for i, route in enumerate(routes):
            route_list = []

            for j, client in enumerate(route):
                if isinstance(client, int):
                    route_list.append(client)
                elif hasattr(client, "idx"):
                    route_list.append(client.idx)
                else:
                    raise TypeError(
                        f"routes[{i}][{j}] = {client} (type {type(client)}) is neither int nor has .idx"
                    )

            normalized_routes.append(route_list)

        return normalized_routes        
    
    def build_from_resdict(self,resDict,problemData):
        # if resDict is Feasible IMPLEMENTATION

        if resDict["stats"] == "No Stats collected!":
            resDict["stats"] = Statistics()
        
        res = Result(Solution(problemData,resDict["routes"]),resDict["stats"],int(resDict["num_iterations"]),float(resDict["runtime"]))
        return res





 

 


