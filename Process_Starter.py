import subprocess
import uuid
import os
import shutil
from TaskQueue import TaskQueue
from SubProcessTask import SubProcessTask

class Subprocess_Starter():
    def __init__(self, RealDMname,Ec2DDMname,inputs,numThreads: int,numEc2D: int,numRealDM: int, numIterations: int):
        self.RealDMname = RealDMname
        self.Ec2dDMname = Ec2DDMname
        self.inputs = inputs
        self.numThreads = numThreads
        self.numEc2D = numEc2D
        self.numRealDM = numRealDM
        self.taskQueue = None
        self.numIterations = numIterations
        self.counter = 1

    def checkInputs(self):
        if not all(isinstance(x, int) for x in (self.numThreads,self.numEc2D,self.numRealDM,self.numIterations)):
            raise ValueError("All inputs integers! Check passed!")
        if not self.numThreads == self.numEc2D+self.numRealDM:
            raise ValueError("numThreads is in proportion to numEc2D and numRealDM")
        if self.numThreads > 64:
            raise ValueError("numThreads too large!!! number below 64 only") 
    
    def fill_TaskQueue(self):
        # type 1 = RealDM
        # type 2 = Ec2D
        cpu_countins = os.cpu_count()
        if isinstance(cpu_countins,int):
            taskQueue = TaskQueue(cpu_countins,"PLACEHOLDER")
        else:
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
        i = taskQueue.startTaskQueue()
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
    def createOutputDicts(self):
        run_dir = "IPC/resDictThreads"
        if os.path.exists(run_dir):
            shutil.rmtree(run_dir)
        os.makedirs(run_dir)
        for i in range(self.numThreads):
            outputdir = f"solver_{i+1}_output"
            dirpath = os.path.join(run_dir,outputdir)
            os.makedirs(dirpath)




    def create_Task(self, type):
        if type == 1:
            task = SubProcessTask("RealDM",self.inputs,self.numIterations,self.counter,self.RealDMname,self.Ec2dDMname)
            print(f"RealDM process with ID: {self.counter} created! \n")
            self.counter += 1
            return task
        else:
            task = SubProcessTask("Ec2D",self.inputs,self.numIterations,self.counter,self.RealDMname,self.Ec2dDMname)
            print(f"Ec2D process with ID: {self.counter} created!\n")
            self.counter += 1
            return task
    def doEverything(self):
        self.checkInputs()
        self.createLogFiles()
        self.createOutputDicts()
        self.fill_TaskQueue()




#if __name__ == "__main__":
#    starter = Subprocess_Starter(1,1,1,4,2,2)
#    starter.checkInputs()
#    starter.createLogFiles()
