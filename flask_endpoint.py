
resDict: dict
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def start():
    return "The Server is running and the solution is ready. Change URL to /solution to access"
@app.route("/solution")
def get_data():
    return jsonify(resDict)

if globals().get("resDict") is not None or __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

