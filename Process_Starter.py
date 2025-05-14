import subprocess
import uuid
import os
import shutil
from TaskQueue import TaskQueue
from SubProcessTask import SubProcessTask

class Subprocess_Starter():
    def __init__(self, modelToSolveRealDM,modelToSolveEc2D, inputs,numThreads: int,numEc2D: int,numRealDM: int):
        self.modelToSolveRealDM = modelToSolveRealDM
        self.modelToSolveEc2D = modelToSolveEc2D
        self.inputs = inputs
        self.numThreads = numThreads
        self.numEc2D = numEc2D
        self.numRealDM = numRealDM
        self.taskQueue = None

    def checkInputs(self):
        if not all(isinstance(x, int) for x in (self.numThreads,self.numEc2D,self.numRealDM)):
            raise ValueError("All inputs integers! Check passed!")
        if not self.numThreads == self.numEc2D+self.numRealDM:
            raise ValueError("numThreads is in proportion to numEc2D and numRealDM")
        if self.numThreads > 64:
            raise ValueError("numThreads too large!!! number below 64 only") 
    
    def fill_TaskQueue(self):
        # type 1 = RealDM
        # type 2 = Ec2D
        taskQueue = TaskQueue(4,"PLACEHOLDER")
        for i in range(self.numThreads):
            if self.numRealDM > 0:
                subPTask1 = self.create_Task(1)
                taskQueue.addTask(subPTask1)
                self.numRealDM -= 1
            if self.numEc2D > 0:
                subPTask2 = self.create_Task(2)
                taskQueue.addTask(subPTask2)
                self.numEc2D -= 1
        taskQueue.startTaskQueue()
        print("task_queue fill function ran!")
    
    def createLogFiles(self):
        run_dir = f"runLogs"
        if os.path.exists(run_dir):
            shutil.rmtree(run_dir)
        os.makedirs(run_dir)
        for i in range(self.numThreads):
            log_filename = f"solver_{i+1}.log"
            log_filepath = os.path.join(run_dir,log_filename)
            with open(log_filepath, "w") as log_file:
                log_file.write(f"LogFile for Solver: {i+1}\n")




    def create_Task(self, type):
        if type == 1:
            task = SubProcessTask(self.modelToSolveRealDM,self.inputs)
            print(f"RealDM process created")
            return task
        else:
            task = SubProcessTask(self.modelToSolveEc2D,self.inputs)
            print(f"Ec2D process created!")
            return task




if __name__ == "__main__":
    starter = Subprocess_Starter(1,1,1,4,2,2)
    starter.checkInputs()
    starter.createLogFiles()
