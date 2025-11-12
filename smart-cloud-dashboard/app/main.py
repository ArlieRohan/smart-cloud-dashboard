from flask import Flask, render_template, jsonify, request
from app.aws_client import AWSClient

app = Flask(__name__, template_folder="templates", static_folder="static")
aws = AWSClient()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/instances", methods=["GET"])
def instances():
    return jsonify(aws.list_instances())

@app.route("/api/instance/<instance_id>/start", methods=["POST"])
def start_instance(instance_id):
    ok = aws.start_instance(instance_id)
    return jsonify({"status": "started" if ok else "error", "instance": instance_id})

@app.route("/api/instance/<instance_id>/stop", methods=["POST"])
def stop_instance(instance_id):
    ok = aws.stop_instance(instance_id)
    return jsonify({"status": "stopped" if ok else "error", "instance": instance_id})

@app.route("/api/cpu/<instance_id>", methods=["GET"])
def cpu_metric(instance_id):
    try:
        val = aws.fetch_cpu(instance_id)
        cpu_val = None if val is None else float(val)
        return jsonify({"instance": instance_id, "cpu": cpu_val})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
