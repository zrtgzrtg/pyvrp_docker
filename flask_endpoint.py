
import threading
import time
from ResultServer import Result_Server
import psutil
import subprocess   
from flask import Flask, request, jsonify,render_template, redirect, send_file
import os
import json

app = Flask(__name__)

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
    while psutil.pid_exists(pid):
        if not is_process_alive(pid):
            break
        time.sleep(60)
    with open("progress.log", "a") as log:
        log.write("Solver process completed. Generating ZIP now...\n")
    Result_Server().giveZipresDict()





@app.route("/")
def start():
    return render_template("index.html")
@app.route("/solution")
def get_data():
    with open("progress.log", "a") as log_file:
        log_file.write(f"Reached if-statement with (getResDict()) END\n")
    try:
        with open("IPC/job.pid") as f:
            pid = int(f.read().strip())
        with open("progress.log","a") as log:
            log.write(f"PID ASSIGNED NOW pid: {pid}")
    except FileNotFoundError:
        with open("progress.log", "a")as f:
            f.write(f"reached FileNotFoundError")
            return render_template("wait.html")
    if is_process_alive(pid):
        return render_template("wait.html")
    else:
        with open("progress.log","a") as f:
            res_handler = Result_Server()
            res_handler.giveZipresDict()
            return render_template("download_solution.html")
@app.route("/download")
def download():
    return send_file("IPC/combined_resDict.zip", as_attachment=True)
@app.route("/solver")
def serverSolver():
    return render_template("solver.html")
@app.route("/solve", methods=["POST"])
def startSolver():
    numIterations = request.form.get("iterations", type=int)
    with open("progress.log", "a") as log_file:
        log_file.write(f"Form received with {numIterations}")
    # Blocking process !!
    # os.system(f"python distmain.py {numIterations} > progress.log 2>&1")
    with open("progress.log", "a") as f:
        process = subprocess.Popen(["python3","distmain.py",f"{numIterations}"],
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


if globals().get("resDict") is not None or __name__ == "__main__":
    app.run(host="0.0.0.0", port=80,debug=True, use_reloader=False)

