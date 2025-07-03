
import re
import threading
import time
from ResultServer import Result_Server
import psutil
import subprocess   
from flask import Flask, request, jsonify,render_template, redirect, send_file, abort
from data.city_matrices import city_matrices
import os
import json
import shutil

app = Flask(__name__)

def check_cpu_usage(request):
    limit = 20
    if request.method == "POST":
        cpuPercent = psutil.cpu_percent(interval=2.0)
        if cpuPercent > limit:
            abort(503, description = "CPU overloaded. Probably running calculation!")

        

def is_process_alive(pid):
    try:
        proc = psutil.Process(pid)
        status = proc.status()
        alive = proc.is_running() and status != psutil.STATUS_ZOMBIE
        with open("progress.log", "a") as f:
            f.write(f"\npsutil check: pid={pid}, status={status}, alive={alive}\n")
        return alive
    except psutil.NoSuchProcess:
        return False
def watcherFunction(pid):
    res_dir = "IPC/resDictThreads"
    while True:
        if psutil.pid_exists(pid):
            if not is_process_alive(pid):
                if os.path.exists(res_dir):
                    with open("progress.log", "a") as log:
                        log.write("Solver process completed. Generating ZIP now...\n")
                    break
                else:
                    with open("progress.log", "a") as f:
                        f.write("IPC/resDictThreads not created yet!. No process has started till now! \n")
        else:
            if os.path.exists(res_dir):
                with open("progress.log","a") as f1:
                    f1.write("process gone but resDict There")
                break
            else:
                with open("progress.log","a") as f2:
                    f2.write("process gone but waiting longer")
        time.sleep(20)
    
    #The Zip gets created here once the watcher notices the end of the run!
    Result_Server().giveZipresDict()
def extract_n(filename):
    match = re.search(r"n(\d+)",filename)
    if match:
        return int(match.group(1))
    else:
        return 99999






@app.route("/")
def start():
    return render_template("index.html")
@app.route("/solution")
def get_data():
    with open("progress.log", "a") as log_file:
        log_file.write(f"Reached if-statement with (getResDict()) END\n")
        if os.path.exists("IPC/combined_resDict.zip"):
            log_file.write("Zip Exists! Serving Download now!")
            return render_template("download_solution.html")
        else:
            log_file.write("Zip doesnt Exist yet. Serve Wait page!")
            return render_template("wait.html")
@app.route("/download")
def download():
    return send_file("IPC/combined_resDict.zip", as_attachment=True)
@app.route("/solver")
def serverSolver():
    vrp_path = "data/Vrp-Set-X/X/"
    sorted_files = sorted(os.listdir(vrp_path), key=extract_n)

    filenames_list = [f[:-4] for f in sorted_files if f.endswith(".vrp")]

    city_names = list(city_matrices.keys())
    return render_template("solver.html",cities=city_names,filenames = filenames_list)
@app.route("/solverBatch")
def serverSolverBatch():
    vrp_path = "data/Vrp-Set-X/X/"
    sorted_files = sorted(os.listdir(vrp_path), key=extract_n)

    filenames_list = [f[:-4] for f in sorted_files if f.endswith(".vrp")]

    city_names = list(city_matrices.keys())
    return render_template("solverBatch.html",cities=city_names,filenames = filenames_list)
@app.route("/solveBatch", methods=["POST"])
def startSolverBatch():
    check_cpu_usage(request)
    numIterations = request.form.get("iterations", type=int)
    city = request.form.get("city", type=str)
    vrp_file = request.form.get("vrp-file", type=str)
    numClients = request.form.get("numClients", type=int)
    numThreads = request.form.get("numThreads",type=int)
    numRealDM = request.form.get("numRealDM",type=int)
    calcEc2D = numThreads-numRealDM
    debugCapacity = request.form.get("debugCapacity",type=int)
    debugstr = request.form.get("isDebugRun", type=str)
    isDebugRun = debugstr.lower() == "true"
    inputsHTML = {
            "numIterations": numIterations,
            "city": city,
            "vrp-file":vrp_file,
            "numClients":numClients,
            "numThreads": numThreads,
            "numRealDM": numRealDM,
            "numEc2D": calcEc2D,
            "debugCapacity": debugCapacity,
            "isDebugRun": isDebugRun
        }
    inputsHTMLstr = json.dumps(inputsHTML)
    with open("IPC/inputsHTML.json","w") as f:

            json.dump(inputsHTML,f, indent=4)
    res_dir = "IPC/resDictThreads"
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)
    if os.path.exists("IPC/combined_resDict.zip"):
        os.remove("IPC/combined_resDict.zip")
        with open("progress.log", "a") as abc:
            abc.write("Deleted old Resdict. Now can rerun succesfully")
    with open("progress.log", "a") as f:
        process = subprocess.Popen(["python3","BatchQueue.py",inputsHTMLstr],
                                   stdout=f,
                                   stderr=f
                               )
    return redirect("/running")


@app.route("/solve", methods=["POST"])
def startSolver():
    check_cpu_usage(request)
    numIterations = request.form.get("iterations", type=int)
    city = request.form.get("city", type=str)
    vrp_file = request.form.get("vrp-file", type=str)
    numClients = request.form.get("numClients", type=int)
    numThreads = request.form.get("numThreads",type=int)
    numRealDM = request.form.get("numRealDM",type=int)
    calcEc2D = numThreads-numRealDM
    debugCapacity = request.form.get("debugCapacity",type=int)
    debugstr = request.form.get("isDebugRun", type=str)
    isDebugRun = debugstr.lower() == "true"

    with open("progress.log", "a") as log_file:
        log_file.write(f"Form received with {numIterations}")
        log_file.write("Creating the inputsHTML now!")
    
    inputsHTML = {
        "numIterations": numIterations,
        "city": city,
        "vrp-file":vrp_file,
        "numClients":numClients,
        "numThreads": numThreads,
        "numRealDM": numRealDM,
        "numEc2D": calcEc2D,
        "debugCapacity": debugCapacity,
        "isDebugRun": isDebugRun
    }
    inputsHTMLstr = json.dumps(inputsHTML)
    with open("IPC/inputsHTML.json","w") as f:
        json.dump(inputsHTML,f, indent=4)
    # Blocking process !!
    # os.system(f"python distmain.py {numIterations} > progress.log 2>&1")

    # Delete old resDictThreads so Subprocess and watcher dont Fail
    res_dir = "IPC/resDictThreads"
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)
    if os.path.exists("IPC/combined_resDict.zip"):
        os.remove("IPC/combined_resDict.zip")
        with open("progress.log", "a") as abc:
            abc.write("Deleted old Resdict. Now can rerun succesfully")
    with open("progress.log", "a") as f:
        process = subprocess.Popen(["python3","distmain.py",inputsHTMLstr],
                                   stdout=f,
                                   stderr=f
                               )
    with open("IPC/job.pid","w") as f:
        f.write(str(process.pid))
        watcher = threading.Thread(target=watcherFunction, args=(process.pid,))
        watcher.start()
    return redirect("/running")
@app.route("/running")
def running():
    return render_template("running.html")


if __name__ == "__main__":
    # normal version
    #app.run(host="0.0.0.0", port=80,debug=True, use_reloader=False)

    #for localhost without port exposing
    app.run(debug=True)

