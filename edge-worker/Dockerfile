FROM python:3.9-slim
WORKDIR /app
RUN pip install boto3 pillow
COPY worker.py .
CMD ["python", "-u", "worker.py"]