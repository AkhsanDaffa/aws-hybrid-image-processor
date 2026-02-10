# 1. Definisikan Provider
terraform {
    required_providers {
      aws = {
        source      = "hashicorp/aws"
        version     = "~> 4.16"
      }
    }
    required_version = ">= 1.2.0"
}

provider "aws" {
    region = "ap-southeast-1" # Singapura
}

# 2. Buat S3 Bucket (Gudang File)
resource "aws_s3_bucket" "image_bucket" {
    bucket = "hybrid-images-project-rpi-adap26"

    force_destroy = true

    tags = {
        Name        = "Image Processing Bucket"
        Environment = "Dev"
    }
}

# 3. Buat SQS Queue (Antrian Tugas)
resource "aws_sqs_queue" "task_queue" {
    name                        = "image-processing-queue"
    delay_seconds               = 0
    max_message_size            = 2048
    message_retention_seconds   = 86400
    receive_wait_time_seconds   = 10

    tags = {
        Environment = "Dev"
    }
}

# 4. Output (Show info after finish create)
output "bucket_name" {
    value = aws_s3_bucket.image_bucket.bucket
}

output "queue_url" {
    value = aws_sqs_queue.task_queue.url
}