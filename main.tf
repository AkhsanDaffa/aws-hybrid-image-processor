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

# Security Group (Satpam)
resource "aws_security_group" "web_sg" {
    name        = "web-server-sg"
    description = "Allow SSH and Flask traffic"

    # Izin Masuk SSH (Port 22)
    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    # Izin Masuk Flask Web (Port 5000)
    ingress {
        from_port   = 5000
        to_port     = 5000
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    # Izin Keluar
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# DATA SOURCE
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # ID Resmi Canonical (Pembuat Ubuntu)

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# EC2 INSTANCE (SERVER)
resource "aws_instance" "web_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro" # Gratis (Free Tier)
  
  # Masukkan nama Key Pair yang tadi dibuat di Console
  key_name      = "devops-key" 

  # Tempelkan Security Group
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = {
    Name = "Flask-Web-Server"
  }
}

# 4. Output (Show info after finish create)
output "bucket_name" {
    value = aws_s3_bucket.image_bucket.bucket
}

output "queue_url" {
    value = aws_sqs_queue.task_queue.url
}

# --- UPDATE OUTPUT ---
output "public_ip" {
  value = aws_instance.web_server.public_ip
  description = "Alamat IP Publik server web kita"
}