import flask
from datetime import datetime

app = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.send_file("static/index.html")

@app.route("/media", methods=["POST"])
def get_media():
    if not "file" in flask.request.files:
        return "file must be uploaded with the name file", 400
    
    file = flask.request.files["file"]

    if file == None:
        return "must provide a valid file", 400

    if file.filename == "":
        return "file must have a name", 400

    file.save("static/uploads/uploaded_img.jpeg")
    return "succses", 200

@app.route('/upload', methods=["POST"])
def compress_image():
    if 'image' not in flask.request.files:
        return flask.jsonify({'error': 'No file part'}), 400
    
    file = flask.request.files['image']
    
    if file.filename == '':
        return flask.jsonify({'error': 'No selected file'}), 400

    # Save the file to a specific path (optional)
    file_name = f'image{datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")}' 
    file.save(f'static/uploads/{file_name}.jpg')
    
    return flask.jsonify({'fileName': file_name}), 200

@app.route("/download/<string:file_id>", methods=["GET"])
def donwload(file_id):
    return flask.send_file(f"static/uploads/{file_id}.jpg", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
