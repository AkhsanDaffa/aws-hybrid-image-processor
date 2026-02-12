import boto3
import time
import json
import os
from PIL import Image

# --- KONFIGURASI (GANTI DENGAN DATA BARU HARI INI) ---
BUCKET_NAME = os.environ.get('BUCKET_NAME')
QUEUE_URL = os.environ.get('SQS_URL')

# Setup AWS Client
s3 = boto3.client('s3', region_name='ap-southeast-1')
sqs = boto3.client('sqs', region_name='ap-southeast-1')

def process_image(filename):
    print(f"[*] Mendownload {filename}...")
    s3.download_file(BUCKET_NAME, filename, filename)

    print(f"[*] Mengubah jadi Hitam Putih...")
    img = Image.open(filename)
    grayscale = img.convert('L') # 'L' mode = Grayscale
    
    output_filename = f"processed_{filename}"
    grayscale.save(output_filename)

    print(f"[*] Uploading {output_filename} ke S3...")
    s3.upload_file(output_filename, BUCKET_NAME, output_filename)

    # Bersihkan file lokal biar disk RPi tidak penuh
    os.remove(filename)
    os.remove(output_filename)
    print("[+] Selesai! File lokal dihapus.")

def main():
    print("=== WORKER RASPBERRY PI SIAP KERJA ===")
    print("Menunggu pesan dari SQS (Tekan Ctrl+C untuk stop)...")

    while True:
        try:
            # Long Polling (Tunggu 20 detik kalau kosong, biar hemat internet)
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20 
            )

            if 'Messages' in response:
                message = response['Messages'][0]
                receipt_handle = message['ReceiptHandle']
                body = json.loads(message['Body'])
                
                print(f"\n[!] Pesan Diterima: {body}")
                
                # Eksekusi Proses
                filename = body.get('filename')
                if filename:
                    process_image(filename)

                # Hapus pesan dari antrian (ACK)
                sqs.delete_message(
                    QueueUrl=QUEUE_URL,
                    ReceiptHandle=receipt_handle
                )
                print("[V] Pesan dihapus dari antrian.")
            else:
                print(".", end="", flush=True) # Print titik kalau sepi

        except Exception as e:
            print(f"\n[X] Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()