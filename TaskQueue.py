import time
import os



class RunningTask():
    def __init__(self,process,openFile):
        self.process = process
        self.openFile = openFile
 

class TaskQueue():
    def __init__(self, max_Amount_Parallel,start_Process_Function):
        self.max_Amount_Parallel = max_Amount_Parallel
        self.queue = []
        self.running = []
        self.start_Process_Function = start_Process_Function


    def addTask(self, subProcessTask):
        self.queue.append(subProcessTask)

    def startTaskQueue(self):
        while self.queue or self.running:
            still_running = []

            for runningTask in self.running:
                if runningTask.process.poll() is None:
                    still_running.append(runningTask)
                else:
                    print(f"Process with has finished!")
                    runningTask.openFile.close()
            
            self.running = still_running

            while len(self.running) < self.max_Amount_Parallel and self.queue:
                subProcessTask = self.queue.pop(0)

                # needs class that has a .start function
                process, openFile = subProcessTask.start()

                self.running.append(RunningTask(process,openFile))
            
            time.sleep(0.5)

                


       