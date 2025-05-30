
import json
import sys



from Process_Starter import Subprocess_Starter

def run(realDM,Ec2DDM,inputs,numThreads,numEc2D,numRealDM,numIterations):
    subprocessstarter = Subprocess_Starter(realDM,Ec2DDM,inputs,numThreads,numEc2D,numRealDM,numIterations)
    subprocessstarter.doEverything()
    pass


if __name__ == "__main__":
    sys.argv[1] = json.loads(sys.argv[1])
    realDM =  sys.argv[1][0]
    Ec2DDM=  sys.argv[1][1]
    inputs=  sys.argv[1][2]
    numThreads=  sys.argv[1][3]
    numEc2D=  sys.argv[1][4]
    numRealDM=  sys.argv[1][5]
    numIterations =  sys.argv[1][6]
    run(realDM,Ec2DDM,inputs,numThreads,numEc2D,numRealDM,numIterations)