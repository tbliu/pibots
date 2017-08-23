import subprocess
from flask import Flask, render_template

app = Flask(__name__);

proc = None

@app.route("/")
def hello():
    return render_template("index.html");

@app.route("/start", methods=['GET', 'POST'])
def start():
    global proc
    proc = subprocess.Popen(["python", "security.py", "-c"]);
    return "Started!";

@app.route("/stop", methods=['GET', 'POST'])
def stop():
    global proc
    proc.kill();
    return "Stopped!";

@app.route("/status", methods=['GET','POST'])
def status():
    global proc
    if proc is None:
        return "Resting!"

    if proc.poll() is None:
        return "Running!"

    else:
        return "Stopped!";

if __name__ == "__main__":
    app.run(host="0.0.0.0", port =5555, debug=False)

