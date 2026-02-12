import boto3
import json
from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# --- KONFIGURASI (GANTI INI!) ---
# Masukkan nama bucket S3 (huruf kecil) dari output terraform
BUCKET_NAME = os.environ.get('BUCKET_NAME') 

# Masukkan URL SQS (https://...) dari output terraform
SQS_URL = os.environ.get('SQS_URL')

# --- INISIALISASI AWS ---
# Perhatikan: Kita TIDAK butuh access key disini karena sudah pakai IAM Role!
s3 = boto3.client('s3', region_name='ap-southeast-1')
sqs = boto3.client('sqs', region_name='ap-southeast-1')

# --- HTML SEDERHANA (Form Upload) ---
HTML_PAGE = """
<!doctype html>
<html>
<head><title>Hybrid Cloud Uploader</title></head>
<body>
    <h1>Upload Foto untuk Diproses</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file_foto">
      <input type="submit" value="Upload & Proses">
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 1. Ambil file dari form
        file = request.files.get('file_foto')
        if not file:
            return "Mana filenya?"
        
        filename = file.filename
        
        try:
            # 2. Upload ke S3 (Masuk Gudang)
            print(f"Mengupload {filename} ke S3...")
            s3.upload_fileobj(file, BUCKET_NAME, filename)
            
            # 3. Kirim Pesan ke SQS (Lapor Kantor Pos)
            message = {
                "filename": filename,
                "action": "grayscale"
            }
            
            print(f"Mengirim pesan ke SQS...")
            sqs.send_message(
                QueueUrl=SQS_URL,
                MessageBody=json.dumps(message)
            )
            
            return f"<h1>Sukses!</h1> <p>File <b>{filename}</b> sudah di S3 dan pesan antrian sudah dikirim.</p> <a href='/'>Upload Lagi</a>"
            
        except Exception as e:
            return f"<h1>Error :(</h1> <p>{str(e)}</p>"

    return HTML_PAGE

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)