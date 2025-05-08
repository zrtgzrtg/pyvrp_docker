
from flask import Flask, request, jsonify,render_template, redirect
import os
from shared import getResDict

app = Flask(__name__)



@app.route("/")
def start():
    return render_template("index.html")
@app.route("/solution")
def get_data():
    if getResDict() is not None: 
        return jsonify(getResDict())
    else:
        return render_template("solution.html")
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
    app.run(host="0.0.0.0", port=80,debug=True, use_reloader=False)

