import os
import uuid
import queue
import threading
import subprocess
# import docker

from flask import Flask, request, render_template, send_from_directory, jsonify, url_for, abort
app = Flask(__name__)

cwd = os.path.abspath(os.path.dirname(__file__))
SAMPLES_FOLDER = os.path.join(cwd, "online_doodle_files")

# styles = {
#     "monet": {
#         "original": "Monet.jpg",
#         "annotation": "Monet_sem.png",
#     },
#     "renoir": {
#         "original": "Renoir.jpg",
#         "annotation": "Renoir_sem.png"
#     }
# }

class Converter:
    def __init__(self):
        self.lock = threading.Lock()
        self.in_progress = set()
        self.ready = set()

        self._shutdown_thread = False
        self.queue = queue.Queue()

        self.my_worker_thread = threading.Thread(target=self.worker_function)
        self.my_worker_thread.start()

    def convert(self, filename):
        with self.lock:
            self.in_progress.add(filename)
        self.queue.put(filename)

    def is_ready(self, filename):
        with self.lock:
            return filename in self.ready

    def worker_function(self):
        while not self._shutdown_thread:
            item = self.queue.get()
            subprocess.call(["venv/bin/python", "apply.py",
            "--colors", "pretrained/gen_doodles.hdf5colors.npy",
            "--target_mask", os.path.join(SAMPLES_FOLDER, "{}_mask.png".format(item)),
            "--model", "pretrained/starry_night.t7",
            "--out_path", os.path.join(SAMPLES_FOLDER, "{}.png".format(item))], cwd=os.path.join(cwd, os.pardir))

            with self.lock:
                self.in_progress.remove(item)
                self.ready.add(item)


    def shutting_down(self):
        self._shutdown_thread = True

converter = Converter()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/ready/<uid>')
def ready(uid):
    if converter.is_ready(uid):
        return jsonify(ready=True, url=url_for('result', filename=uid + ".png"))
    else:
        abort(404)

@app.route('/upload', methods=["POST"])
def upload():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            uid = str(uuid.uuid4())
            filename = uid + "_mask.png"
            file.save(os.path.join(SAMPLES_FOLDER, filename))
            converter.convert(uid)
            return jsonify(uid=uid)
    return jsonify(error="no file")


@app.route('/annotation/<style>.png')
def annotation_picture(style):
    return send_from_directory(SAMPLES_FOLDER,
                               "style_mask.png")

@app.route('/result/<filename>')
def result(filename):
    return send_from_directory(SAMPLES_FOLDER, filename)
