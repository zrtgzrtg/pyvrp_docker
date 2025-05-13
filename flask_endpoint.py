
from flask import Flask, request, jsonify,render_template, redirect, send_file
import os
import json

app = Flask(__name__)



@app.route("/")
def start():
    return render_template("index.html")
@app.route("/solution")
def get_data():
    with open("progress.log", "a") as log_file:
        log_file.write(f"Reached if-statement with (getResDict()) END\n")
    if os.path.isfile("IPC/resDict.json"): 
        with open("progress.log", "a") as log_file2:
            log_file2.write("REACHED Download \n")
            return render_template("download_solution.html")
    else:
        return render_template("wait.html")
@app.route("/download")
def download():
    return send_file("IPC/resDict.json", as_attachment=True)
@app.route("/solver")
def serverSolver():
    return render_template("solver.html")
@app.route("/solve", methods=["POST"])
def startSolver():
    numIterations = request.form.get("iterations", type=int)
    with open("progress.log", "a") as log_file:
        log_file.write(f"Form received with {numIterations}")
    os.system(f"python distmain.py {numIterations} > progress.log 2>&1")
    return redirect("/running")
@app.route("/running")
def running():
    return render_template("running.html")


if globals().get("resDict") is not None or __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True, use_reloader=False)

