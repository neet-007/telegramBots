import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.send_file("index.html")

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
