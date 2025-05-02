
import re
import vrplib
import numpy 
import sys
import os
import json
import random
import pyvrp

class ProblemDataGenerator():
    def __init__(self,name,distance_matrix_name: str,X_scenario: str,numClients):
        self.name = name
        self.numClients = 99
        self.distance_matrix = None
        self.distance_matrix_raw = None
        self.X_scenario = X_scenario
        self.instance = self.importScenario()
        self.distance_matrix_name = distance_matrix_name
        self.problemData = None
        self.numVehicles = self.get_num_vehicles()
        self.problemDataList = {
            "depots": "a",
            "clients": "a",
            "vehicle_types": "a",
        }


    def import_distance_matrix(self):
        current_dir = os.path.dirname(__file__)
        location = f"data/distance_matrices/{self.distance_matrix_name}.json"
        filepath = os.path.join(current_dir, location)
        if not os.path.isfile(filepath):
            print(f"{filepath} is not valid!")
            #raise FileNotFoundError(f"{distance_matrix_name} not found!")
        with open(filepath,"r") as f:
            self.distance_matrix_raw = json.load(f)

    def convert_distance_matrix(self):
        if self.distance_matrix_raw is None:
            raise ValueError("No distance matrix loaded yet!")
        records = self.distance_matrix_raw
        node_ids = sorted({r["OriginID"] for r in records} | {r["DestinationID"] for r in records})
        id_to_index = {node_id: idx for idx, node_id in enumerate(node_ids)}
        n = len(node_ids)

        matrix = numpy.zeros((n, n), dtype=int)
        
        for r in records:
            i = id_to_index[r["OriginID"]]
            j = id_to_index[r["DestinationID"]]
            matrix[i, j] = int(r["Total_Length"])

        self.distance_matrix = [row for row in matrix]
    def ret_distance_matrix(self):
        self.import_distance_matrix()
        self.convert_distance_matrix()
        return self.distance_matrix
    
    def importScenario(self):
        filepath = os.path.join(os.path.dirname(__file__),f"data/Vrp-Set-X/X/{self.X_scenario}.vrp")
        return vrplib.read_instance(filepath)
    
    def createVehicleTypes(self):
        capacity = self.instance["capacity"]
        vehicle_type = pyvrp.VehicleType(capacity = [capacity], num_available=self.get_num_vehicles())
        self.problemDataList["vehicle_types"] = [vehicle_type]
    
    def createDepots(self):
        # x = 0 and y = 0 as placeholders since they are required for code but irrelevant if distance matrix is used
        depot = pyvrp.Depot(x = 0,y = 0)
        self.problemDataList["depots"] = [depot]
    
    def get_num_vehicles(self) -> int:
        match = re.search(r"k(\d+)", self.X_scenario)
        if match:
            return int(match.group(1))
        raise ValueError(f"Could not extract vehicle count from: {self.X_scenario}")
    
    def createClients(self):
        demands = self.instance["demand"][1:self.numClients+1]
        clients = []
        # x = 0 and y = 0 are placeholders again since we are using distance matrix
        for demand in demands:
            client = pyvrp.Client(x=0,y=0, delivery = [demand])
            clients.append(client)
        self.problemDataList["clients"] = clients
    
    def createEverythingForProblemData(self):
        self.createDepots()
        self.createClients()
        self.createVehicleTypes()





    def constructProblemData(self):
        self.problemData = pyvrp.ProblemData(
            clients = self.problemDataList["clients"],
            depots = self.problemDataList["depots"],
            vehicle_types = self.problemDataList["vehicle_types"],
            distance_matrices = [self.distance_matrix],
            duration_matrices = [self.distance_matrix]
        )
    def doEverything(self):
        self.import_distance_matrix()
        self.convert_distance_matrix()
        self.createEverythingForProblemData()
        self.constructProblemData()
        print(self.problemData)









#if __name__ == "__main__":
    #gen = ProblemDataGenerator("A","Synthetic_Full_OD_CostMatrix","X-n101-k25",99)

    #gen.import_distance_matrix()
    #gen.convert_distance_matrix()
    #gen.createEverythingForProblemData()
    #print(len(gen.problemDataList["clients"]))
    #print(len(gen.problemDataList["depots"]))
    #print(len(gen.problemDataList["vehicle_types"]))
    #print(gen.numVehicles)
    #gen.constructProblemData()
    #print(gen.problemData)

