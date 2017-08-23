import subprocess
from flask import Flask, render_template

"""
Reference:
    https://hackernoon.com/raspberrypi-home-surveillance-with-only-150-lines-of-python-code-2701bd0373c9
"""

app = Flask(__name__);

proc = None

@app.route("/")
def hello():
    return render_template("index.html");

@app.route("/start", methods=['GET', 'POST'])
def start():
    global proc
    print("> Starting up");
    proc = subprocess.Popen(["python", "security.py", "-c"]);
    print(" > Process id {}".format(proc.pid))
    return "Started!";

@app.route("/stop", methods=['GET', 'POST'])
def stop():
    global proc
    print("> Stopping...");
    proc.kill();
    print("> Process {} killed!".format(proc.pid));
    return "Stopped!";

@app.route("/status", methods=['GET','POST'])
def status():
    global proc
    if proc is None:
        print("> Camera is stopped")
        return "Resting!"

    if proc.poll() is None:
        print("> Camera is running (Process {})!".format(proc.id))
        return "Running!"

    else:
        print("> Camera is stopped");
        return "Stopped!";

if __name__ == "__main__":
    app.run(host="0.0.0.0", port =5555, debug=False)

