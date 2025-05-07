
import io
from pyvrp import Result,Statistics,Solution
import contextlib
import pandas as pd
import os


class DataCreator():
    def __init__(self,res,dataset,X_set):
        self.dataset = dataset
        self.X_set = X_set
        self.res = res
        
    def runStatistics(self):
        current_dir = os.path.dirname(__file__)
        location=f"output_from_res"
        filepath=os.path.join(current_dir,location)
        os.makedirs(f"{filepath}", exist_ok=True)
        output_file=os.path.join(filepath,f"{self.dataset}_{self.X_set}.csv")

        self.res.stats.to_csv(output_file)
        pd_statistics_object = self.turn_data_to_dict(output_file)
        return {
            "routes": self.get_best_output(),
            "stats": pd_statistics_object,
            "num_iterations": self.res.num_iterations,
            "runtime": self.res.runtime,
        }

        
    
    def import_statistics(self,dataset,X_set):
        current_dir=os.path.dirname(__file__)
        location=f"output_from_res/{dataset}_{X_set}.csv"
        filepath=os.path.join(current_dir,location)
        res=Statistics.from_csv(filepath)
        return res
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
                        f"❌ routes[{i}][{j}] = {client} (type {type(client)}) is neither int nor has .idx"
                    )

            normalized_routes.append(route_list)

        return normalized_routes        
    
    def build_from_resdict(self,resDict,problemData):
        
        res = Result(Solution(problemData,resDict["routes"]),resDict["stats"],int(resDict["num_iterations"]),float(resDict["runtime"]))
        return res





 

 


