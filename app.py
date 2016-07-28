import os
import uuid
import queue
import threading
import docker

from flask import Flask, request, render_template, send_from_directory, jsonify, url_for, abort
app = Flask(__name__)

cwd = os.path.abspath(os.path.dirname(__file__))
SAMPLES_FOLDER = os.path.join(cwd, "samples")

styles = {
    "monet": {
        "original": "Monet.jpg",
        "annotation": "Monet_sem.png",
    },
    "renoir": {
        "original": "Renoir.jpg",
        "annotation": "Renoir_sem.png"
    }
}

class Converter:
    def __init__(self):
        self.lock = threading.Lock()
        self.in_progress = set()
        self.ready = set()

        self._shutdown_thread = False
        self.queue = queue.Queue()

        self.client = docker.from_env()
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
            container = self.client.create_container(
                image="alexjc/neural-doodle:gpu",
                command="--style=samples/Monet.jpg --output samples/{}.png --iterations=40".format(item),
                volumes=["/nd/samples"],
                host_config=self.client.create_host_config(binds={
                    SAMPLES_FOLDER: {
                        'bind': '/nd/samples',
                        'mode': 'rw'
                    }
                })
            )
            self.client.start(container)
            self.client.wait(container)
            print(self.client.logs(container))
            self.client.remove_container(container)

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
            filename = uid + "_sem.png"
            file.save(os.path.join(SAMPLES_FOLDER, filename))
            converter.convert(uid)
            return jsonify(uid=uid)
    return jsonify(error="no file")


@app.route('/annotation/<style>.png')
def annotation_picture(style):
    return send_from_directory(SAMPLES_FOLDER,
                               styles[style]["annotation"])

@app.route('/result/<filename>')
def result(filename):
    return send_from_directory(SAMPLES_FOLDER, filename)
