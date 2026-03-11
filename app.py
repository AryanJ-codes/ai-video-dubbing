import os
import threading
from flask import Flask, request, render_template, jsonify, send_from_directory
from main import run_pipeline
from utils import logger
import traceback

app = Flask(__name__)

# Global state for the running pipeline
task_status = {
    "status": "idle",   # idle | processing | completed | error
    "stage": "",
    "message": "",
    "progress": 0,      # 0-100
    "eta_seconds": None,
    "output_file": None
}

def process_video_background(url: str):
    global task_status

    def status_updater(progress, stage, message, eta_seconds):
        task_status["progress"] = progress
        task_status["stage"] = stage
        task_status["message"] = message
        task_status["eta_seconds"] = round(eta_seconds) if eta_seconds is not None else None

    try:
        final_video_path = run_pipeline(url, status_updater=status_updater)
        task_status["status"] = "completed"
        task_status["progress"] = 100
        task_status["message"] = "Pipeline finished successfully!"
        task_status["output_file"] = os.path.basename(final_video_path)
    except Exception as e:
        task_status["status"] = "error"
        task_status["message"] = str(e)
        logger.error(f"Background task failed: {e}")
        logger.debug(traceback.format_exc())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/dub", methods=["POST"])
def dub_video():
    global task_status
    data = request.json
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "No URL provided"}), 400
        
    if task_status["status"] == "processing":
        return jsonify({"error": "A job is already running! Please wait for it to finish."}), 429
        
    # Reset status
    task_status = {
        "status": "processing",
        "stage": "Initializing",
        "message": "Initializing...",
        "progress": 0,
        "eta_seconds": None,
        "output_file": None
    }
    
    # Start background thread
    t = threading.Thread(target=process_video_background, args=(url,))
    t.daemon = True
    t.start()
    
    return jsonify({"message": "Job started", "status": "processing"})

@app.route("/api/status", methods=["GET"])
def get_status():
    global task_status
    return jsonify(task_status)

@app.route("/outputs/<filename>")
def get_output(filename):
    from config import OUTPUTS_DIR
    return send_from_directory(OUTPUTS_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
