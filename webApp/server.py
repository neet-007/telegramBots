from flask import send_file, jsonify, request, Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return send_file("index.html")

@app.route('/media', methods=["POST"])
def get_media():
    if not "file" in request.files:
        return "not found", 400

    file = request.files["file"]

    if file.filename == "":
        return "not found", 400

    if file:
        file.save('static/uploads/uploaded_img.jpg')
        return "found", 200

    return "error", 400

@app.route('/upload', methods=["POST"])
def compress_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the file to a specific path (optional)
    file_name = f'image{datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")}' 
    file.save(f'static/uploads/{file_name}.jpg')
    
    return jsonify({'fileName': file_name}), 200

@app.route("/download/<string:file_id>", methods=["GET"])
def donwload(file_id):
    return send_file(f"static/uploads/{file_id}.jpg", as_attachment=True)

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
