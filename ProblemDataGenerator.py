
import time
import re
import vrplib
import numpy 
import sys
import os
import json
import random
import pyvrp
import rapidjson

class ProblemDataGenerator():
    def __init__(self,distance_matrix_name: str,X_scenario: str, numClients: int):
        self.numClients = int(numClients)
        self.distance_matrix = None
        self.distance_matrix_raw = None
        self.X_scenario = X_scenario
        self.instance = self.importScenario()
        self.distance_matrix_name = distance_matrix_name
        self.problemData = None
        #self.numVehicles = self.get_num_vehicles()
        self.problemDataList = {
            "depots": "a",
            "clients": "a",
            "vehicle_types": "a",
        }


    def import_distance_matrix(self):
        current_dir = os.path.dirname(__file__)
        #old line
        #location = f"data/distance_matrices/{self.distance_matrix_name}.json"
        if not self.distance_matrix_name.endswith(".json"):
            filename = self.distance_matrix_name + ".json"
        else :
            filename = self.distance_matrix_name

        location = os.path.join("data",self.parentDir,filename)
        filepath = os.path.join(current_dir, location)
        if not os.path.isfile(filepath):
            print(f"{filepath} is not valid!")
            #raise FileNotFoundError(f"{distance_matrix_name} not found!")
        with open(filepath,"r") as f:
            self.distance_matrix_raw = rapidjson.load(f)

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
        # num_available is num of locations
        vehicle_type = pyvrp.VehicleType(capacity = [capacity], num_available=self.numClients)
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
        # dm is 100x100
        # self.instance = vrplib import from X-n101-k25 Scenario
        remainingNumClients = self.numClients #99
        clients = []
        while remainingNumClients > 0:
            time.sleep(0.1)    
            if remainingNumClients > self.instance["dimension"]-1:
                demands = self.instance["demand"][1:self.instance["dimension"]]
                # x = 0 and y = 0 are placeholders again since we are using distance matrix
                for demand in demands:
                    client = pyvrp.Client(x=0,y=0, delivery = [demand])
                    clients.append(client)
                remainingNumClients -= self.instance["dimension"]-1
            else:
                demands = self.instance["demand"][1:remainingNumClients+1]
                for demand in demands:
                    client = pyvrp.Client(x=0,y=0, delivery= [demand])
                    clients.append(client)
                remainingNumClients = remainingNumClients-len(demands)
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
    def doEverythingDEBUG(self, debugCapacity):
        self.import_distance_matrix()
        self.convert_distance_matrix()
        # Now we overwrite capacity in the .vrp file so vehicle type in createEverythingForProblemData is affected
        self.overwriteCapacityDebugFile(int(debugCapacity))
        self.createEverythingForProblemData()
        self.constructProblemData()
 
    def getProblemData(self):
        self.doEverything()
        if self.problemData is None:
            raise ValueError("PROBLEMDATA wasnt generated correctly")
        return self.problemData

    def overwriteCapacityDebugFile(self,new_capacity):
        filepath = f"data/Vrp-Set-X/X/debug.vrp"
        with open(filepath, "r") as f:
            lines = f.readlines()

        lines[5] = f"CAPACITY : {new_capacity}\n"

        with open(filepath, "w") as f:
            f.writelines(lines)









#if __name__ == "__main__":
#    #inputs={
#    #    "dm":"Chicago_100x100_RoadData",
#    #    "X_set":"X-n101-k25",
#    #    "numClients":"99"
#    #    }
#    #gen = ProblemDataGenerator(inputs["dm"],inputs["X_set"],inputs["numClients"])
#    #gen.doEverything()
#    #print(gen.problemData.clients())
#    #demands = [client.delivery for client in gen.problemData.clients()]
#    #print(demands)
#    inputs = {
#        "dm": "Chicago_100x100_RoadData",
#        "X_set": "X-n101-k25",
#        "numClients": "99"
#    }
#
#    gen = ProblemDataGenerator(inputs["dm"], inputs["X_set"], inputs["numClients"])
#    gen.doEverything()
#
#    # Extract generated problem data
#    problem_data = gen.getProblemData()
#
#    # Extract actual demands from the generated clients
#    clients = problem_data.clients()
#    print(clients[0].delivery[0])
#    print(clients[98].delivery[0])
#    m = problem_data.distance_matrix(0)
#
#    
#    print(problem_data.num_profiles)
#    print(m[1,10])
#    print(m[1][2])
#    print(m[0, 1])
#    print(clients[0].delivery[0])
#
#


   