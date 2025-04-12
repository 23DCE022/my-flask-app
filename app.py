from flask import Flask, request, Response, render_template, redirect, url_for, send_file
from bson import ObjectId
from pymongo import MongoClient
import gridfs
import os
import io
from werkzeug.utils import secure_filename
from flask_ngrok import run_with_ngrok

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['file_db']
fs = gridfs.GridFS(db)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    files = fs.find()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    if file:
        filename = secure_filename(file.filename)
        fs.put(file, filename=filename, content_type=file.content_type)
    return redirect('/')

@app.route('/download/<file_id>')
def download_file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return Response(
            file.read(),
            mimetype=file.content_type,
            headers={"Content-Disposition": f"attachment;filename={file.filename}"}
        )
    except Exception as e:
        return f"Download error: {str(e)}", 404

@app.route('/preview/<file_id>')
def preview_file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(
            io.BytesIO(file.read()),
            mimetype=file.content_type,
            as_attachment=False,
            download_name=file.filename
        )
    except Exception as e:
        return f"Preview error: {str(e)}", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
