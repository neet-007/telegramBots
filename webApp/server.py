import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.send_file("index.html")

@app.route('/media', methods=["POST"])
def get_media():
    if not "file" in flask.request.files:
        return "not found", 400

    file = flask.request.files["file"]

    if file.filename == "":
        return "not found", 400

    if file:
        file.save(f'static/uploads/uploaded_img.jpg')
        return "found", 200

    return "error", 400

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
